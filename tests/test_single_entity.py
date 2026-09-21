import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register models
from app.api.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.entity import Entity
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User


class SingleEntityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.user = User(
            name="Pessoa Teste", cpf="12345678901", email="test@example.com",
            password="test", birth_date=date(2000, 1, 1), city="São Paulo", uf="SP",
        )
        self.session.add(self.user)
        self.session.commit()
        self.current_user = self.user
        app.dependency_overrides[get_session] = lambda: self.session
        app.dependency_overrides[get_current_user] = lambda: self.current_user
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()
        self.session.close()
        self.engine.dispose()

    def entity_data(self, slug):
        return {
            "name": "Entidade de teste", "slug": slug, "sector": "Educação",
            "description": "Apoio comunitário", "city": "São Paulo", "uf": "SP",
        }

    def test_create_returns_entity_and_get_me_returns_admin(self):
        self.assertIsNone(self.client.get("/api/v1/entities/me").json())
        response = self.client.post("/api/v1/entities", json=self.entity_data("first"))
        self.assertEqual(response.status_code, 201)
        entity_id = response.json()["id"]
        membership = self.client.get("/api/v1/entities/me")
        self.assertEqual(membership.status_code, 200)
        self.assertEqual(membership.json()["entity"]["id"], entity_id)
        self.assertEqual(membership.json()["position"], "admin")

        notification = self.session.query(Notification).filter_by(
            recipient_id=self.user.id,
            notification_type=NotificationType.ENTITY_MEMBER_JOINED,
        ).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.entity_id, entity_id)
        second = self.client.post("/api/v1/entities", json=self.entity_data("second"))
        self.assertEqual(second.status_code, 409)
        self.assertIsNone(self.session.query(Entity).filter_by(slug="second").first())

    def test_member_cannot_create_a_second_entity(self):
        entity = Entity(**self.entity_data("existing"))
        self.session.add(entity)
        self.session.flush()
        self.session.add(MemberEntity(
            id_user=self.user.id, id_entity=entity.id, position=MemberPosition.MEMBER
        ))
        self.session.commit()
        response = self.client.post("/api/v1/entities", json=self.entity_data("another"))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.client.get("/api/v1/entities/me").json()["position"], "member")

    def test_database_rejects_a_second_membership(self):
        entities = [Entity(**self.entity_data(slug)) for slug in ("first", "second")]
        self.session.add_all(entities)
        self.session.flush()
        self.session.add(MemberEntity(
            id_user=self.user.id, id_entity=entities[0].id, position=MemberPosition.ADMIN
        ))
        self.session.commit()
        self.session.add(MemberEntity(
            id_user=self.user.id, id_entity=entities[1].id, position=MemberPosition.EDITOR
        ))
        with self.assertRaises(IntegrityError):
            self.session.commit()
        self.session.rollback()


if __name__ == "__main__":
    unittest.main()
