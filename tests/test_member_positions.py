import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all models
from app.api.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.entity import Entity
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User


class MemberPositionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.users = [
            User(
                name=f"Pessoa {index}", cpf=f"{index:011d}",
                email=f"member{index}@example.com", password="test",
                birth_date=date(2000, 1, 1), city="São Paulo", uf="SP",
            )
            for index in range(5)
        ]
        self.entities = [
            Entity(
                name=f"Entidade {index}", slug=f"entity-{index}",
                sector="Educação", description="Teste", city="São Paulo", uf="SP",
            )
            for index in range(2)
        ]
        self.session.add_all(self.users + self.entities)
        self.session.flush()
        self.session.add_all([
            MemberEntity(id_user=self.users[0].id, id_entity=self.entities[0].id,
                         position=MemberPosition.ADMIN),
            MemberEntity(id_user=self.users[1].id, id_entity=self.entities[0].id,
                         position=MemberPosition.EDITOR),
            MemberEntity(id_user=self.users[2].id, id_entity=self.entities[0].id,
                         position=MemberPosition.MEMBER),
            MemberEntity(id_user=self.users[3].id, id_entity=self.entities[1].id,
                         position=MemberPosition.ADMIN),
        ])
        self.session.commit()
        self.current_user = self.users[0]
        app.dependency_overrides[get_session] = lambda: self.session
        app.dependency_overrides[get_current_user] = lambda: self.current_user
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()
        self.session.close()
        self.engine.dispose()

    def change_role(self, entity_id, user_id, position):
        return self.client.patch(
            f"/api/v1/entities/{entity_id}/members/{user_id}/position",
            json={"position": position},
        )

    def list_members(self, entity_id):
        return self.client.get(f"/api/v1/entities/{entity_id}/members")

    def remove_member(self, entity_id, user_id):
        return self.client.delete(
            f"/api/v1/entities/{entity_id}/members/{user_id}"
        )

    def leave_entity(self, entity_id):
        return self.client.delete(f"/api/v1/entities/{entity_id}/leave")

    def test_admin_can_promote_and_demote_existing_member(self):
        entity_id = self.entities[0].id
        user_id = self.users[2].id
        for position in ("editor", "admin", "member"):
            response = self.change_role(entity_id, user_id, position)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                "id_user": user_id, "id_entity": entity_id, "position": position,
            })
        self.assertEqual(
            self.session.get(MemberEntity, 3).position, MemberPosition.MEMBER
        )
        notifications = self.session.scalars(
            select(Notification).where(
                Notification.recipient_id == user_id,
                Notification.notification_type
                == NotificationType.ENTITY_ROLE_CHANGED,
            )
        ).all()
        self.assertEqual(len(notifications), 3)
        self.assertTrue(all(
            notification.actor_id == self.users[0].id
            and notification.entity_id == entity_id
            for notification in notifications
        ))

    def test_editor_and_member_cannot_change_roles(self):
        for actor in (self.users[1], self.users[2]):
            self.current_user = actor
            response = self.change_role(
                self.entities[0].id, self.users[2].id, "admin"
            )
            self.assertEqual(response.status_code, 403)
        self.assertEqual(
            self.session.get(MemberEntity, 3).position, MemberPosition.MEMBER
        )

    def test_admin_of_another_entity_cannot_change_roles(self):
        self.current_user = self.users[3]
        response = self.change_role(
            self.entities[0].id, self.users[2].id, "editor"
        )
        self.assertEqual(response.status_code, 403)

    def test_target_must_belong_to_the_same_entity(self):
        response = self.change_role(
            self.entities[0].id, self.users[3].id, "editor"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            self.session.get(MemberEntity, 4).position, MemberPosition.ADMIN
        )

    def test_last_admin_cannot_be_demoted(self):
        response = self.change_role(
            self.entities[0].id, self.users[0].id, "editor"
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            self.session.get(MemberEntity, 1).position, MemberPosition.ADMIN
        )
        self.assertEqual(
            self.change_role(self.entities[0].id, self.users[2].id, "admin").status_code,
            200,
        )
        self.assertEqual(
            self.change_role(self.entities[0].id, self.users[0].id, "editor").status_code,
            200,
        )

    def test_invalid_role_and_missing_login_are_rejected(self):
        self.assertEqual(
            self.change_role(self.entities[0].id, self.users[2].id, "owner").status_code,
            422,
        )
        app.dependency_overrides.pop(get_current_user)
        self.assertEqual(
            self.change_role(self.entities[0].id, self.users[2].id, "admin").status_code,
            401,
        )

    def test_all_entity_positions_can_list_members(self):
        expected_positions = ["admin", "editor", "member"]

        for actor in self.users[:3]:
            with self.subTest(actor=actor.name):
                self.current_user = actor
                response = self.list_members(self.entities[0].id)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [member["position"] for member in response.json()],
                    expected_positions,
                )

        self.current_user = self.users[3]
        self.assertEqual(self.list_members(self.entities[0].id).status_code, 403)

    def test_only_admin_can_remove_entity_member(self):
        entity_id = self.entities[0].id

        for actor in (self.users[1], self.users[2], self.users[3]):
            with self.subTest(actor=actor.name):
                self.current_user = actor
                self.assertEqual(
                    self.remove_member(entity_id, self.users[2].id).status_code,
                    403,
                )

        self.current_user = self.users[0]
        response = self.remove_member(entity_id, self.users[2].id)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(
            self.session.query(MemberEntity).filter_by(
                id_user=self.users[2].id,
                id_entity=entity_id,
            ).first()
        )
        notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.users[2].id,
                Notification.notification_type
                == NotificationType.ENTITY_MEMBER_REMOVED,
            )
        )
        self.assertIsNotNone(notification)
        self.assertEqual(notification.actor_id, self.users[0].id)
        self.assertEqual(notification.entity_id, entity_id)

    def test_member_can_leave_entity_and_receives_notification(self):
        self.current_user = self.users[2]

        response = self.leave_entity(self.entities[0].id)

        self.assertEqual(response.status_code, 204)
        self.assertIsNone(
            self.session.query(MemberEntity).filter_by(
                id_user=self.users[2].id,
                id_entity=self.entities[0].id,
            ).first()
        )
        notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.users[2].id,
                Notification.notification_type
                == NotificationType.ENTITY_MEMBER_LEFT,
            )
        )
        self.assertIsNotNone(notification)
        self.assertEqual(notification.entity_id, self.entities[0].id)

    def test_last_admin_cannot_leave_entity(self):
        response = self.leave_entity(self.entities[0].id)

        self.assertEqual(response.status_code, 409)
        self.assertIsNotNone(
            self.session.query(MemberEntity).filter_by(
                id_user=self.users[0].id,
                id_entity=self.entities[0].id,
            ).first()
        )
        notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.users[0].id,
                Notification.notification_type
                == NotificationType.ENTITY_MEMBER_LEFT,
            )
        )
        self.assertIsNone(notification)

    def test_last_admin_cannot_be_removed(self):
        response = self.remove_member(
            self.entities[0].id,
            self.users[0].id,
        )

        self.assertEqual(response.status_code, 409)
        self.assertIsNotNone(
            self.session.query(MemberEntity).filter_by(
                id_user=self.users[0].id,
                id_entity=self.entities[0].id,
            ).first()
        )


if __name__ == "__main__":
    unittest.main()
