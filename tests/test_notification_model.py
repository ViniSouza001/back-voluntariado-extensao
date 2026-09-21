import unittest
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - registra os models no metadata
from app.db.base import Base
from app.models.entity import Entity
from app.models.invitation import Invitation, InvitationType
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.vacancy import Vacancies, VacancyBranch, VacancyModality


class NotificationModelTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

        self.actor = self.create_user(1, "Autor")
        self.recipient = self.create_user(2, "Destinatário")
        self.entity = Entity(
            name="Entidade",
            slug="notification-entity",
            sector="Social",
            description="Entidade de teste",
            city="São Paulo",
            uf="SP",
        )
        self.session.add(self.entity)
        self.session.flush()

        starts_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
        self.vacancy = Vacancies(
            title="Vaga",
            description="Vaga de teste",
            id_entity=self.entity.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            branch=VacancyBranch.COMMUNITY,
            modality=VacancyModality.REMOTE,
        )
        self.invitation = Invitation(
            sender_id=self.actor.id,
            recipient_id=self.recipient.id,
            invitation_type=InvitationType.ENTITY,
            target_id=self.entity.id,
        )
        self.session.add_all([self.vacancy, self.invitation])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def create_user(self, suffix: int, name: str) -> User:
        user = User(
            name=name,
            cpf=f"{suffix:011d}",
            email=f"notification{suffix}@example.com",
            password="test",
            birth_date=date(2000, 1, 1),
            city="São Paulo",
            uf="SP",
        )
        self.session.add(user)
        self.session.flush()
        return user

    def test_notification_relationships(self):
        notification = Notification(
            recipient_id=self.recipient.id,
            actor_id=self.actor.id,
            notification_type=NotificationType.INVITATION_RECEIVED,
            title="Novo convite",
            message="Você recebeu um convite.",
            invitation_id=self.invitation.id,
        )
        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)

        self.assertEqual(notification.recipient.id, self.recipient.id)
        self.assertEqual(notification.actor.id, self.actor.id)
        self.assertEqual(notification.invitation.id, self.invitation.id)
        self.assertIsNone(notification.entity)
        self.assertIsNone(notification.vacancy)

    def test_notification_accepts_only_one_related_resource(self):
        notification = Notification(
            recipient_id=self.recipient.id,
            notification_type=NotificationType.ENTITY_ROLE_CHANGED,
            title="Alteração",
            message="Seu papel foi alterado.",
            entity_id=self.entity.id,
            vacancy_id=self.vacancy.id,
        )
        self.session.add(notification)

        with self.assertRaises(IntegrityError):
            self.session.commit()
        self.session.rollback()

    def test_deleting_resources_preserves_or_removes_notification_correctly(self):
        notification = Notification(
            recipient_id=self.recipient.id,
            actor_id=self.actor.id,
            notification_type=NotificationType.INVITATION_RECEIVED,
            title="Novo convite",
            message="Você recebeu um convite.",
            invitation_id=self.invitation.id,
        )
        self.session.add(notification)
        self.session.commit()
        notification_id = notification.id

        self.session.delete(self.invitation)
        self.session.commit()
        self.session.expire_all()
        notification = self.session.get(Notification, notification_id)
        self.assertIsNotNone(notification)
        self.assertIsNone(notification.invitation_id)

        self.session.delete(self.actor)
        self.session.commit()
        self.session.expire_all()
        notification = self.session.get(Notification, notification_id)
        self.assertIsNotNone(notification)
        self.assertIsNone(notification.actor_id)

        self.session.delete(self.recipient)
        self.session.commit()
        self.assertIsNone(self.session.get(Notification, notification_id))


if __name__ == "__main__":
    unittest.main()
