import unittest
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all tables with SQLAlchemy
from app.api.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.entity import Entity
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.user import User
from app.schemas.vacancies import BR_TZ


class VacancyRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        user = User(
            name="Pessoa Teste", cpf="12345678901", email="test@example.com",
            password="test", birth_date=date(2000, 1, 1), city="São Paulo", uf="SP",
        )
        entity = Entity(
            name="Entidade Teste", slug="entidade-teste", sector="Educação",
            description="Teste", city="São Paulo", uf="SP",
        )
        self.session.add_all([user, entity])
        self.session.flush()
        self.session.add(MemberEntity(
            id_user=user.id, id_entity=entity.id, position=MemberPosition.ADMIN,
        ))
        self.session.commit()
        self.entity_id = entity.id
        app.dependency_overrides[get_session] = lambda: self.session
        app.dependency_overrides[get_current_user] = lambda: user
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()
        self.session.close()
        self.engine.dispose()

    def vacancy_data(self, modality):
        starts_at = (datetime.now(BR_TZ) + timedelta(days=2)).replace(
            tzinfo=None, microsecond=0,
        )
        return {
            "title": "Vaga de teste",
            "description": "Apoiar a comunidade",
            "id_entity": self.entity_id,
            "starts_at": starts_at.isoformat(timespec="minutes"),
            "ends_at": (starts_at + timedelta(hours=2)).isoformat(timespec="minutes"),
            "branch": "education",
            "modality": modality,
        }

    def test_remote_vacancy_needs_no_address(self):
        data = self.vacancy_data("remote")
        response = self.client.post("/api/v1/vacancies", json=data)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["modality"], "remote")
        self.assertIsNone(response.json()["thoroughfare"])
        self.assertTrue(response.json()["starts_at"].startswith(data["starts_at"]))
        vacancies = self.client.get(f"/api/v1/vacancies/?id_entity={self.entity_id}")
        self.assertEqual(vacancies.status_code, 200)
        self.assertEqual(vacancies.json()[0]["id"], response.json()["id"])

    def test_in_person_vacancy_needs_only_street_from_address_fields(self):
        data = self.vacancy_data("in_person")
        data.update({"city": "São Paulo", "uf": "SP", "thoroughfare": "Rua das Flores"})
        response = self.client.post("/api/v1/vacancies", json=data)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["thoroughfare"], "Rua das Flores")
        self.assertIsNone(response.json()["cep"])
        self.assertIsNone(response.json()["number"])
        self.assertIsNone(response.json()["details"])

    def test_in_person_vacancy_without_street_is_rejected(self):
        data = self.vacancy_data("in_person")
        data.update({"city": "São Paulo", "uf": "SP"})
        response = self.client.post("/api/v1/vacancies", json=data)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
