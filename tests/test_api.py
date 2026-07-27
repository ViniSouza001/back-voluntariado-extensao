import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.email_confirmation import EmailConfirmation


class ApiFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "test.db"
        self.engine = create_engine(
            f"sqlite:///{database_path.as_posix()}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False
        )

        application = create_app()

        def override_database():
            session = self.session_factory()
            try:
                yield session
            finally:
                session.close()

        application.dependency_overrides[get_db] = override_database
        self.client_context = TestClient(application)
        self.client = self.client_context.__enter__()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.engine.dispose()
        self.temporary_directory.cleanup()

    def test_complete_account_and_organization_flow(self) -> None:
        self.assertEqual(self.client.get("/health").json(), {"status": "healthy"})

        with patch("app.services.auth.secrets.token_urlsafe", return_value="known-token"):
            registration = self.client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Test User",
                    "cpf": "529.982.247-25",
                    "email": "user@example.com",
                    "password": "safe-password",
                    "birth_date": "2000-01-01",
                    "city": "Campinas",
                    "state": "sp",
                },
            )
        self.assertEqual(registration.status_code, 201, registration.text)
        self.assertFalse(registration.json()["confirmation_email_sent"])

        with self.session_factory() as session:
            confirmation = session.scalar(select(EmailConfirmation))
            self.assertIsNotNone(confirmation)
            self.assertNotEqual(confirmation.token_hash, "known-token")

        unconfirmed_login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "safe-password"},
        )
        self.assertEqual(unconfirmed_login.status_code, 401)

        confirmation = self.client.get("/api/v1/auth/confirm-email/known-token")
        self.assertEqual(confirmation.status_code, 200, confirmation.text)

        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "safe-password"},
        )
        self.assertEqual(login.status_code, 200, login.text)
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        profile = self.client.get("/api/v1/users/me", headers=headers)
        self.assertEqual(profile.status_code, 200, profile.text)
        self.assertEqual(profile.json()["state"], "SP")

        organization = self.client.post(
            "/api/v1/organizations",
            headers=headers,
            json={
                "name": "Helping Hands",
                "username": "helping-hands",
                "sector": "Education",
                "description": "Volunteer education projects",
                "city": "Campinas",
                "state": "sp",
            },
        )
        self.assertEqual(organization.status_code, 201, organization.text)
        self.assertEqual(organization.json()["username"], "helping-hands")

        updated_profile = self.client.patch(
            "/api/v1/users/me",
            headers=headers,
            json={"city": "Sao Paulo", "state": "sp"},
        )
        self.assertEqual(updated_profile.status_code, 200, updated_profile.text)
        self.assertEqual(updated_profile.json()["city"], "Sao Paulo")

        password_change = self.client.patch(
            "/api/v1/users/me/password",
            headers=headers,
            json={
                "current_password": "safe-password",
                "new_password": "new-safe-password",
                "new_password_confirmation": "new-safe-password",
            },
        )
        self.assertEqual(password_change.status_code, 200, password_change.text)

        new_login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "new-safe-password"},
        )
        self.assertEqual(new_login.status_code, 200, new_login.text)
        new_headers = {"Authorization": f"Bearer {new_login.json()['access_token']}"}

        deletion = self.client.delete("/api/v1/users/me", headers=new_headers)
        self.assertEqual(deletion.status_code, 204, deletion.text)
        self.assertEqual(self.client.get("/api/v1/users/me", headers=new_headers).status_code, 401)


if __name__ == "__main__":
    unittest.main()
