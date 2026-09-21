import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - registra os models no metadata
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.invitation import Invitation, InvitationType
from app.models.user import User


class UserDeletionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

        self.user = User(
            name="Usuário removido",
            cpf="12345678901",
            email="removed@example.com",
            password="test",
            birth_date=date(2000, 1, 1),
            city="São Paulo",
            uf="SP",
        )
        self.other_user = User(
            name="Usuário mantido",
            cpf="10987654321",
            email="kept@example.com",
            password="test",
            birth_date=date(2000, 1, 1),
            city="São Paulo",
            uf="SP",
        )
        self.session.add_all([self.user, self.other_user])
        self.session.flush()
        self.session.add_all([
            Invitation(
                sender_id=self.user.id,
                recipient_id=self.other_user.id,
                invitation_type=InvitationType.FRIEND,
            ),
            Invitation(
                sender_id=self.other_user.id,
                recipient_id=self.user.id,
                invitation_type=InvitationType.FRIEND,
            ),
        ])
        self.session.commit()

        app.dependency_overrides[get_session] = lambda: self.session
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()
        self.session.close()
        self.engine.dispose()

    def test_delete_any_user_by_id_and_related_invitations(self):
        deleted_user_id = self.user.id
        kept_user_id = self.other_user.id

        response = self.client.request(
            "DELETE",
            "/api/v1/user/me",
            json={"id": deleted_user_id},
        )

        self.assertEqual(response.status_code, 204)
        self.assertIsNone(self.session.get(User, deleted_user_id))
        self.assertIsNotNone(self.session.get(User, kept_user_id))
        self.assertEqual(self.session.scalars(select(Invitation)).all(), [])


if __name__ == "__main__":
    unittest.main()
