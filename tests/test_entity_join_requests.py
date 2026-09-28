import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all tables
from app.api.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.entity import Entity
from app.models.entity_join_request import EntityJoinRequest, JoinRequestStatus
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User


class EntityJoinRequestTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.requester = self.make_user(1, "Pessoa Solicitante")
        self.admin = self.make_user(2, "Administradora")
        self.second_admin = self.make_user(3, "Outro Administrador")
        self.member = self.make_user(4, "Membro")
        self.other_admin = self.make_user(5, "Admin Externo")
        self.entity = self.make_entity("Patas Felizes", "patas-felizes")
        self.other_entity = self.make_entity("Outra Entidade", "outra-entidade")
        self.session.flush()
        self.session.add_all([
            MemberEntity(id_user=self.admin.id, id_entity=self.entity.id,
                         position=MemberPosition.ADMIN),
            MemberEntity(id_user=self.second_admin.id, id_entity=self.entity.id,
                         position=MemberPosition.ADMIN),
            MemberEntity(id_user=self.member.id, id_entity=self.entity.id,
                         position=MemberPosition.MEMBER),
            MemberEntity(id_user=self.other_admin.id, id_entity=self.other_entity.id,
                         position=MemberPosition.ADMIN),
        ])
        self.session.commit()
        self.current_user = self.requester
        app.dependency_overrides[get_session] = lambda: self.session
        app.dependency_overrides[get_current_user] = lambda: self.current_user
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()
        self.session.close()
        self.engine.dispose()

    def make_user(self, suffix, name):
        user = User(
            name=name, cpf=f"{suffix:011d}", email=f"join{suffix}@example.com",
            password="test", birth_date=date(2000, 1, 1),
            city="São Paulo", uf="SP",
        )
        self.session.add(user)
        return user

    def make_entity(self, name, slug):
        entity = Entity(
            name=name, slug=slug, sector="Animais",
            description="Apoio comunitário", city="São Paulo", uf="SP",
        )
        self.session.add(entity)
        return entity

    def submit(self, entity=None):
        entity_id = (entity or self.entity).id
        return self.client.post(f"/api/v1/entities/{entity_id}/join-requests")

    def notifications_for(self, user):
        return list(self.session.scalars(
            select(Notification).where(Notification.recipient_id == user.id)
        ).all())

    def test_submit_notifies_administrators_but_not_requester(self):
        response = self.submit()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "pending")
        self.assertEqual(response.json()["user"]["id"], self.requester.id)
        self.assertEqual(self.notifications_for(self.requester), [])
        self.assertEqual(
            self.client.get("/api/v1/notifications").json()["items"], []
        )
        self.assertEqual(self.notifications_for(self.member), [])
        self.assertEqual(self.notifications_for(self.other_admin), [])
        for admin in (self.admin, self.second_admin):
            notifications = self.notifications_for(admin)
            self.assertEqual(len(notifications), 1)
            self.assertEqual(
                notifications[0].notification_type,
                NotificationType.ENTITY_JOIN_REQUESTED,
            )
            self.assertEqual(notifications[0].actor_id, self.requester.id)
            self.assertEqual(notifications[0].entity_id, self.entity.id)

        self.current_user = self.admin
        admin_notifications = self.client.get("/api/v1/notifications")
        self.assertEqual(admin_notifications.status_code, 200)
        self.assertEqual(
            admin_notifications.json()["items"][0]["notification_type"],
            "entity_join_requested",
        )
        self.current_user = self.requester

        self.assertEqual(self.submit().status_code, 409)
        self.assertEqual(len(self.notifications_for(self.admin)), 1)
        self.assertEqual(
            len(self.client.get("/api/v1/entities/join-requests/me").json()), 1
        )

    def test_accept_creates_member_and_notifies_requester(self):
        request_id = self.submit().json()["id"]
        self.current_user = self.admin
        listing = self.client.get(
            f"/api/v1/entities/{self.entity.id}/join-requests"
        )
        self.assertEqual(listing.status_code, 200)
        self.assertEqual([item["id"] for item in listing.json()], [request_id])
        response = self.client.patch(
            f"/api/v1/entities/{self.entity.id}/join-requests/{request_id}",
            json={"status": "accepted"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "accepted")
        membership = self.session.scalar(select(MemberEntity).where(
            MemberEntity.id_user == self.requester.id
        ))
        self.assertEqual(membership.position, MemberPosition.MEMBER)
        requester_notifications = self.notifications_for(self.requester)
        self.assertEqual(len(requester_notifications), 1)
        self.assertEqual(
            requester_notifications[0].notification_type,
            NotificationType.ENTITY_MEMBER_JOINED,
        )
        self.assertEqual(
            requester_notifications[0].message,
            "Agora você faz parte da entidade Patas Felizes.",
        )
        self.current_user = self.requester
        inbox = self.client.get("/api/v1/notifications")
        self.assertEqual(inbox.status_code, 200)
        self.assertEqual(inbox.json()["items"][0]["message"],
                         "Agora você faz parte da entidade Patas Felizes.")
        self.current_user = self.admin
        self.assertEqual(self.client.patch(
            f"/api/v1/entities/{self.entity.id}/join-requests/{request_id}",
            json={"status": "accepted"},
        ).status_code, 409)
        self.assertEqual(len(self.notifications_for(self.requester)), 1)

    def test_only_entity_admin_can_list_and_decide(self):
        request_id = self.submit().json()["id"]
        path = f"/api/v1/entities/{self.entity.id}/join-requests"
        for actor in (self.requester, self.member, self.other_admin):
            self.current_user = actor
            self.assertEqual(self.client.get(path).status_code, 403)
            self.assertEqual(self.client.patch(
                f"{path}/{request_id}", json={"status": "accepted"}
            ).status_code, 403)
        self.assertIsNone(self.session.scalar(select(MemberEntity).where(
            MemberEntity.id_user == self.requester.id
        )))

    def test_rejection_does_not_join_or_notify_requester_and_allows_retry(self):
        request_id = self.submit().json()["id"]
        self.current_user = self.admin
        response = self.client.patch(
            f"/api/v1/entities/{self.entity.id}/join-requests/{request_id}",
            json={"status": "rejected"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "rejected")
        self.assertEqual(self.notifications_for(self.requester), [])
        self.current_user = self.requester
        self.assertEqual(self.submit().status_code, 201)

    def test_accept_closes_other_pending_requests(self):
        first = self.submit().json()["id"]
        second = self.submit(self.other_entity).json()["id"]
        self.current_user = self.admin
        self.assertEqual(self.client.patch(
            f"/api/v1/entities/{self.entity.id}/join-requests/{first}",
            json={"status": "accepted"},
        ).status_code, 200)
        self.assertEqual(
            self.session.get(EntityJoinRequest, second).status,
            JoinRequestStatus.CANCELED,
        )
        self.current_user = self.other_admin
        self.assertEqual(self.client.patch(
            f"/api/v1/entities/{self.other_entity.id}/join-requests/{second}",
            json={"status": "accepted"},
        ).status_code, 409)

    def test_member_cannot_submit_and_public_entities_are_listed(self):
        self.current_user = self.member
        self.assertEqual(self.submit().status_code, 409)
        self.current_user = self.requester
        entities = self.client.get("/api/v1/entities")
        self.assertEqual(entities.status_code, 200)
        self.assertEqual(
            {item["id"] for item in entities.json()},
            {self.entity.id, self.other_entity.id},
        )
        self.assertEqual(self.client.post(
            "/api/v1/entities/999999/join-requests"
        ).status_code, 404)
        self.assertEqual(self.client.patch(
            f"/api/v1/entities/{self.entity.id}/join-requests/999999",
            json={"status": "pending"},
        ).status_code, 422)


if __name__ == "__main__":
    unittest.main()
