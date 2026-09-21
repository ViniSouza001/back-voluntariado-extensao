import unittest
from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - registra os models no metadata
from app.api.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.notification import CreateNotification
from app.services.notifications import NotificationService


class NotificationRouteTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.user = self.create_user(1, "Destinatário")
        self.other_user = self.create_user(2, "Outro usuário")

        now = datetime.now(UTC).replace(tzinfo=None)
        self.unread = Notification(
            recipient_id=self.user.id,
            actor_id=self.other_user.id,
            notification_type=NotificationType.INVITATION_RECEIVED,
            title="Nova notificação",
            message="Mensagem não lida",
            created_at=now - timedelta(minutes=2),
        )
        self.read = Notification(
            recipient_id=self.user.id,
            notification_type=NotificationType.ENTITY_ROLE_CHANGED,
            title="Notificação lida",
            message="Mensagem lida",
            created_at=now - timedelta(minutes=1),
            read_at=now,
        )
        self.archived = Notification(
            recipient_id=self.user.id,
            notification_type=NotificationType.ENTITY_MEMBER_REMOVED,
            title="Notificação arquivada",
            message="Mensagem arquivada",
            created_at=now,
            archived_at=now,
        )
        self.other_notification = Notification(
            recipient_id=self.other_user.id,
            notification_type=NotificationType.INVITATION_RECEIVED,
            title="Notificação de outra pessoa",
            message="Não pode aparecer",
            created_at=now,
        )
        self.session.add_all([
            self.unread,
            self.read,
            self.archived,
            self.other_notification,
        ])
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

    def create_user(self, suffix: int, name: str) -> User:
        user = User(
            name=name,
            cpf=f"{suffix:011d}",
            email=f"notification-route{suffix}@example.com",
            password="test",
            birth_date=date(2000, 1, 1),
            city="São Paulo",
            uf="SP",
        )
        self.session.add(user)
        self.session.flush()
        return user

    def test_list_only_current_users_unarchived_notifications(self):
        response = self.client.get("/api/v1/notifications")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["unread_count"], 1)
        self.assertEqual(
            [item["id"] for item in data["items"]],
            [self.read.id, self.unread.id],
        )
        self.assertEqual(data["items"][1]["actor"]["id"], self.other_user.id)

    def test_unread_filter_and_pagination(self):
        unread = self.client.get(
            "/api/v1/notifications",
            params={"unread_only": True},
        ).json()
        self.assertEqual(
            [item["id"] for item in unread["items"]],
            [self.unread.id],
        )

        paginated = self.client.get(
            "/api/v1/notifications",
            params={"limit": 1, "offset": 1},
        ).json()
        self.assertEqual(
            [item["id"] for item in paginated["items"]],
            [self.unread.id],
        )

    def test_mark_as_read_is_idempotent_and_private(self):
        first = self.client.patch(
            f"/api/v1/notifications/{self.unread.id}/read"
        )
        second = self.client.patch(
            f"/api/v1/notifications/{self.unread.id}/read"
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["read_at"], second.json()["read_at"])

        self.current_user = self.other_user
        forbidden = self.client.patch(
            f"/api/v1/notifications/{self.read.id}/read"
        )
        self.assertEqual(forbidden.status_code, 404)

    def test_mark_all_reads_only_visible_notifications(self):
        response = self.client.patch("/api/v1/notifications/read-all")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["updated"], 1)
        self.session.refresh(self.archived)
        self.assertIsNone(self.archived.read_at)
        self.assertEqual(
            self.client.get("/api/v1/notifications").json()["unread_count"],
            0,
        )

    def test_archive_hides_without_deleting(self):
        response = self.client.patch(
            f"/api/v1/notifications/{self.unread.id}/archive"
        )

        self.assertEqual(response.status_code, 204)
        listed_ids = [
            item["id"]
            for item in self.client.get("/api/v1/notifications").json()["items"]
        ]
        self.assertNotIn(self.unread.id, listed_ids)
        self.assertIsNotNone(self.session.get(Notification, self.unread.id))

    def test_internal_create_does_not_commit_transaction(self):
        service = NotificationService(self.session)
        service.create(CreateNotification(
            recipient_id=self.user.id,
            notification_type=NotificationType.INVITATION_RECEIVED,
            title="Notificação temporária",
            message="Deve ser desfeita com a transação principal",
        ))

        self.session.rollback()
        count = self.session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.title == "Notificação temporária")
        )
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
