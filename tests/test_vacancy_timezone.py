import unittest
from datetime import UTC, datetime, timedelta

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all tables with SQLAlchemy
from app.db.base import Base
from app.models.entity import Entity
from app.models.vacancy import Vacancies, VacancyBranch, VacancyModality
from app.schemas.vacancy import BR_TZ, CreateVacancies, ListVacancies, ResponseVacancies


class VacancyTimezoneTests(unittest.TestCase):
    def make_data(self, starts_at, ends_at):
        return CreateVacancies(
            title="Apoio comunitário",
            description="Atividade voluntária",
            id_entity=1,
            starts_at=starts_at,
            ends_at=ends_at,
            branch=VacancyBranch.EDUCATION,
            modality=VacancyModality.REMOTE,
        )

    def test_brasilia_time_is_stored_as_utc_and_returned_as_brasilia(self):
        starts_at = (datetime.now(BR_TZ) + timedelta(days=7)).replace(microsecond=0)
        ends_at = starts_at + timedelta(hours=2)
        data = self.make_data(starts_at, ends_at)
        expected_utc = starts_at.astimezone(UTC).replace(tzinfo=None)

        self.assertEqual(data.starts_at, expected_utc)
        self.assertIsNone(data.starts_at.tzinfo)

        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            entity = Entity(
                name="Entidade Teste", slug="entidade-teste", sector="Educação",
                description="Teste", city="São Paulo", uf="SP",
            )
            session.add(entity)
            session.flush()
            vacancy = Vacancies(
                title=data.title, description=data.description,
                id_entity=entity.id, starts_at=data.starts_at, ends_at=data.ends_at,
                branch=data.branch, modality=data.modality,
            )
            session.add(vacancy)
            session.commit()
            session.refresh(vacancy)

            self.assertEqual(vacancy.starts_at, expected_utc)
            self.assertIsNone(vacancy.starts_at.tzinfo)
            self.assertEqual(
                ResponseVacancies.model_validate(vacancy).model_dump(mode="json")["starts_at"],
                starts_at.isoformat(),
            )
            self.assertEqual(
                ListVacancies.model_validate(vacancy).model_dump(mode="json")["ends_at"],
                ends_at.isoformat(),
            )
        engine.dispose()

    def test_utc_input_keeps_the_same_instant(self):
        starts_at = (datetime.now(UTC) + timedelta(days=7)).replace(microsecond=0)
        data = self.make_data(starts_at.isoformat().replace("+00:00", "Z"),
                              (starts_at + timedelta(hours=2)).isoformat())
        self.assertEqual(data.starts_at, starts_at.replace(tzinfo=None))

    def test_naive_input_is_interpreted_as_brasilia_time(self):
        starts_at = (datetime.now(BR_TZ) + timedelta(days=7)).replace(
            tzinfo=None, microsecond=0,
        )
        data = self.make_data(starts_at, starts_at + timedelta(hours=2))
        self.assertEqual(data.starts_at, starts_at + timedelta(hours=3))

    def test_past_brasilia_time_is_rejected(self):
        starts_at = (datetime.now(BR_TZ) - timedelta(hours=1)).replace(tzinfo=None)
        with self.assertRaises(ValidationError):
            self.make_data(starts_at, starts_at + timedelta(hours=2))


if __name__ == "__main__":
    unittest.main()
