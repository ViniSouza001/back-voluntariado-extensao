import unittest
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all tables with SQLAlchemy
from app.core.exceptions import ForbiddenError
from app.db.base import Base
from app.models.entity import Entity
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.vacancy import Vacancies, VacancyBranch, VacancyModality
from app.models.vacancy_participant import VacancyParticipant
from app.schemas.vacancy import CreateVacancies, UpdateVacancies
from app.services.entity_membership import get_entity_position, require_entity_position
from app.services.vacancies import VacancieService


class EntityMembershipTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.users = [
            User(
                name=f"Pessoa {index}", cpf=f"{index:011d}",
                email=f"person{index}@example.com", password="test",
                birth_date=date(2000, 1, 1), city="São Paulo", uf="SP",
            )
            for index in range(4)
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
        self.session.add_all(
            MemberEntity(id_user=self.users[index].id, id_entity=self.entities[0].id,
                         position=position)
            for index, position in enumerate(
                (MemberPosition.ADMIN, MemberPosition.EDITOR, MemberPosition.MEMBER)
            )
        )
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def vacancy_data(self, entity_id, modality=VacancyModality.REMOTE):
        starts_at = datetime.now(UTC) + timedelta(days=2)
        return CreateVacancies(
            title="Apoio comunitário", description="Atividade voluntária",
            id_entity=entity_id, starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2), branch=VacancyBranch.EDUCATION,
            modality=modality,
            **({"thoroughfare": "Rua A", "city": "São Paulo", "uf": "SP",
                "number": "42"} if modality == VacancyModality.IN_PERSON else {}),
        )

    def test_returns_role_for_exact_user_and_entity(self):
        for index, position in enumerate(MemberPosition):
            self.assertEqual(
                get_entity_position(self.session, self.users[index].id, self.entities[0].id),
                position,
            )
        with self.assertRaises(ForbiddenError):
            get_entity_position(self.session, self.users[0].id, self.entities[1].id)
        with self.assertRaises(ForbiddenError):
            get_entity_position(self.session, self.users[3].id, self.entities[0].id)

    def test_allowed_positions_are_checked(self):
        allowed = {MemberPosition.ADMIN, MemberPosition.EDITOR}
        for index in (0, 1):
            self.assertEqual(
                require_entity_position(self.session, self.users[index].id,
                                        self.entities[0].id, allowed),
                list(MemberPosition)[index],
            )
        with self.assertRaises(ForbiddenError):
            require_entity_position(self.session, self.users[2].id,
                                    self.entities[0].id, allowed)

    def test_vacancy_create_update_and_delete_enforce_membership(self):
        service = VacancieService(self.session)
        data = self.vacancy_data(self.entities[0].id, VacancyModality.IN_PERSON)
        with self.assertRaises(ForbiddenError):
            service.create(data, self.users[2])
        with self.assertRaises(ForbiddenError):
            service.create(self.vacancy_data(self.entities[1].id), self.users[0])
        vacancy = service.create(data, self.users[1])
        self.assertEqual(vacancy.number, "42")
        self.assertIsNone(vacancy.details)
        created_notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.users[1].id,
                Notification.notification_type == NotificationType.VACANCY_CREATED,
            )
        )
        self.assertIsNotNone(created_notification)
        self.assertEqual(created_notification.vacancy_id, vacancy.id)

        self.session.add(VacancyParticipant(
            id_vacancy=vacancy.id,
            id_user=self.users[2].id,
        ))
        self.session.commit()
        with self.assertRaises(ForbiddenError):
            service.update(vacancy.id, UpdateVacancies(title="Título alterado"), self.users[2])
        with self.assertRaises(ForbiddenError):
            service.delete(vacancy.id, self.users[3])
        self.assertEqual(self.session.get(Vacancies, vacancy.id).title, data.title)

        self.session.add(MemberEntity(
            id_user=self.users[3].id, id_entity=self.entities[1].id,
            position=MemberPosition.ADMIN,
        ))
        self.session.commit()
        other_vacancy = service.create(self.vacancy_data(self.entities[1].id), self.users[3])
        with self.assertRaises(ForbiddenError):
            service.update(other_vacancy.id,
                           UpdateVacancies(title="Título alterado"), self.users[0])
        with self.assertRaises(ForbiddenError):
            service.delete(other_vacancy.id, self.users[0])
        self.assertIsNotNone(self.session.get(Vacancies, other_vacancy.id))
        self.assertEqual(self.session.get(Vacancies, other_vacancy.id).title,
                         "Apoio comunitário")

        service.update(vacancy.id, UpdateVacancies(title="Título alterado"), self.users[0])
        self.assertEqual(self.session.get(Vacancies, vacancy.id).title, "Título alterado")
        updated_notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.users[2].id,
                Notification.notification_type == NotificationType.VACANCY_UPDATED,
            )
        )
        self.assertIsNotNone(updated_notification)
        self.assertEqual(updated_notification.actor_id, self.users[0].id)
        self.assertEqual(updated_notification.vacancy_id, vacancy.id)

        service.delete(vacancy.id, self.users[1])
        deleted_notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.users[2].id,
                Notification.notification_type == NotificationType.VACANCY_DELETED,
            )
        )
        self.assertIsNotNone(deleted_notification)
        self.assertEqual(deleted_notification.actor_id, self.users[1].id)
        self.assertIsNone(deleted_notification.vacancy_id)
