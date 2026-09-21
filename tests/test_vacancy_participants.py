import unittest
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - registra os models no metadata
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.base import Base
from app.models.entity import Entity
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.vacancy import Vacancies, VacancyBranch, VacancyModality
from app.models.vacancy_participant import VacancyParticipant
from app.services.vacancy_participants import VacancyParticipantService


class VacancyParticipantTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

        self.admin = self.create_user(1, "Admin")
        self.editor = self.create_user(2, "Editor")
        self.member = self.create_user(3, "Membro")
        self.participant_one = self.create_user(4, "Participante 1")
        self.participant_two = self.create_user(5, "Participante 2")

        self.entity = Entity(
            name="Entidade",
            slug="entidade-participantes",
            sector="Social",
            description="Entidade de teste",
            city="São Paulo",
            uf="SP",
        )
        self.session.add(self.entity)
        self.session.flush()
        self.session.add_all([
            MemberEntity(
                id_user=self.admin.id,
                id_entity=self.entity.id,
                position=MemberPosition.ADMIN,
            ),
            MemberEntity(
                id_user=self.editor.id,
                id_entity=self.entity.id,
                position=MemberPosition.EDITOR,
            ),
            MemberEntity(
                id_user=self.member.id,
                id_entity=self.entity.id,
                position=MemberPosition.MEMBER,
            ),
        ])

        starts_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
        self.vacancy = Vacancies(
            title="Vaga de teste",
            description="Atividade voluntária",
            id_entity=self.entity.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            branch=VacancyBranch.COMMUNITY,
            modality=VacancyModality.REMOTE,
        )
        self.session.add(self.vacancy)
        self.session.flush()
        self.participation_one = VacancyParticipant(
            id_vacancy=self.vacancy.id,
            id_user=self.participant_one.id,
        )
        self.participation_two = VacancyParticipant(
            id_vacancy=self.vacancy.id,
            id_user=self.participant_two.id,
        )
        self.session.add_all([
            self.participation_one,
            self.participation_two,
        ])
        self.session.commit()
        self.service = VacancyParticipantService(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def create_user(self, suffix: int, name: str) -> User:
        user = User(
            name=name,
            cpf=f"{suffix:011d}",
            email=f"participant{suffix}@example.com",
            password="test",
            birth_date=date(2000, 1, 1),
            city="São Paulo",
            uf="SP",
        )
        self.session.add(user)
        return user

    def test_admin_and_editor_can_list_participants(self):
        for actor in (self.admin, self.editor):
            with self.subTest(actor=actor.name):
                participants = self.service.list_participants(
                    self.vacancy.id, actor
                )
                self.assertEqual(len(participants), 2)

        with self.assertRaises(ForbiddenError):
            self.service.list_participants(self.vacancy.id, self.member)

    def test_participant_can_leave_vacancy(self):
        participation_id = self.participation_one.id
        self.service.leave_vacancy(self.vacancy.id, self.participant_one)

        self.assertIsNone(
            self.session.get(VacancyParticipant, participation_id)
        )
        notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.participant_one.id,
                Notification.notification_type
                == NotificationType.VACANCY_PARTICIPANT_LEFT,
            )
        )
        self.assertIsNotNone(notification)
        self.assertEqual(notification.vacancy_id, self.vacancy.id)

        with self.assertRaises(NotFoundError):
            self.service.leave_vacancy(self.vacancy.id, self.participant_one)

    def test_admin_and_editor_can_remove_participant(self):
        self.service.remove_participant(
            self.vacancy.id,
            self.participant_one.id,
            self.admin,
        )
        self.service.remove_participant(
            self.vacancy.id,
            self.participant_two.id,
            self.editor,
        )

        participants = self.service.list_participants(self.vacancy.id, self.admin)
        self.assertEqual(participants, [])
        notifications = self.session.scalars(
            select(Notification).where(
                Notification.notification_type
                == NotificationType.VACANCY_PARTICIPANT_REMOVED
            ).order_by(Notification.recipient_id)
        ).all()
        self.assertEqual(
            [notification.recipient_id for notification in notifications],
            [self.participant_one.id, self.participant_two.id],
        )
        self.assertEqual(notifications[0].actor_id, self.admin.id)
        self.assertEqual(notifications[1].actor_id, self.editor.id)

    def test_member_cannot_remove_participant(self):
        with self.assertRaises(ForbiddenError):
            self.service.remove_participant(
                self.vacancy.id,
                self.participant_one.id,
                self.member,
            )


if __name__ == "__main__":
    unittest.main()
