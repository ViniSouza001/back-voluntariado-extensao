import unittest
from datetime import UTC, date, datetime, timedelta

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
from app.models.entity_join_request import JoinRequestStatus
from app.models.invitation import Invitation
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.vacancy import Vacancies, VacancyBranch, VacancyModality
from app.models.vacancy_join_request import VacancyJoinRequest
from app.models.vacancy_participant import VacancyParticipant


class VacancyJoinRequestTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.requester = self.make_user(1, "Solicitante")
        self.admin = self.make_user(2, "Admin")
        self.editor = self.make_user(3, "Editor")
        self.member = self.make_user(4, "Membro")
        self.outsider = self.make_user(5, "Externo")
        self.entity = Entity(
            name="Patas Felizes", slug="patas-felizes-vacancy",
            sector="Animais", description="Apoio", city="São Paulo", uf="SP",
        )
        self.session.add(self.entity)
        self.session.flush()
        self.session.add_all([
            MemberEntity(id_user=self.admin.id, id_entity=self.entity.id,
                         position=MemberPosition.ADMIN),
            MemberEntity(id_user=self.editor.id, id_entity=self.entity.id,
                         position=MemberPosition.EDITOR),
            MemberEntity(id_user=self.member.id, id_entity=self.entity.id,
                         position=MemberPosition.MEMBER),
        ])
        starts_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
        self.vacancy = Vacancies(
            title="Cuidar dos animais", description="Atividade voluntária",
            id_entity=self.entity.id, starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            branch=VacancyBranch.ANIMALS, modality=VacancyModality.REMOTE,
        )
        self.session.add(self.vacancy)
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

    def make_user(self, suffix: int, name: str) -> User:
        user = User(
            name=name, cpf=f"{suffix:011d}", email=f"vacancyjoin{suffix}@example.com",
            password="test", birth_date=date(2000, 1, 1),
            city="São Paulo", uf="SP",
        )
        self.session.add(user)
        self.session.flush()
        return user

    @property
    def path(self):
        return f"/api/v1/vacancies/{self.vacancy.id}/join-requests"

    def notifications_for(self, user):
        return list(self.session.scalars(
            select(Notification).where(Notification.recipient_id == user.id)
        ).all())

    def test_submit_notifies_admin_and_editor_only(self):
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "pending")
        self.assertEqual(response.json()["user"]["id"], self.requester.id)
        self.assertEqual(response.json()["vacancy"]["id"], self.vacancy.id)
        for recipient in (self.admin, self.editor):
            notices = self.notifications_for(recipient)
            self.assertEqual(len(notices), 1)
            self.assertEqual(notices[0].notification_type,
                             NotificationType.VACANCY_JOIN_REQUESTED)
            self.assertEqual(notices[0].vacancy_id, self.vacancy.id)
        for recipient in (self.requester, self.member, self.outsider):
            self.assertEqual(self.notifications_for(recipient), [])
        self.assertEqual(self.client.post(self.path).status_code, 409)
        self.assertEqual(len(self.notifications_for(self.admin)), 1)
        mine = self.client.get("/api/v1/vacancies/join-requests/me")
        self.assertEqual(mine.status_code, 200)
        self.assertEqual(len(mine.json()), 1)

    def test_accept_adds_participant_and_notifies_requester(self):
        request_id = self.client.post(self.path).json()["id"]
        self.current_user = self.editor
        listing = self.client.get(self.path)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual([item["id"] for item in listing.json()], [request_id])
        response = self.client.patch(
            f"{self.path}/{request_id}", json={"status": "accepted"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "accepted")
        participant = self.session.scalar(select(VacancyParticipant).where(
            VacancyParticipant.id_vacancy == self.vacancy.id,
            VacancyParticipant.id_user == self.requester.id,
        ))
        self.assertIsNotNone(participant)
        notices = self.notifications_for(self.requester)
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0].notification_type,
                         NotificationType.VACANCY_PARTICIPANT_JOINED)
        self.assertEqual(notices[0].actor_id, self.editor.id)
        self.assertEqual(self.client.patch(
            f"{self.path}/{request_id}", json={"status": "accepted"}
        ).status_code, 409)
        self.assertEqual(len(self.notifications_for(self.requester)), 1)
        self.assertEqual(self.client.get(f"{self.path}?pending_only=false").json()[0]["status"],
                         "accepted")
        self.assertEqual(self.client.get(self.path).json(), [])

    def test_rejection_allows_new_request_without_adding_participant(self):
        request_id = self.client.post(self.path).json()["id"]
        self.current_user = self.admin
        response = self.client.patch(
            f"{self.path}/{request_id}", json={"status": "rejected"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "rejected")
        self.assertIsNone(self.session.scalar(select(VacancyParticipant)))
        self.assertEqual(self.notifications_for(self.requester), [])
        self.current_user = self.requester
        self.assertEqual(self.client.post(self.path).status_code, 201)

    def test_permissions_and_invalid_requests(self):
        request_id = self.client.post(self.path).json()["id"]
        for actor in (self.requester, self.member, self.outsider):
            self.current_user = actor
            self.assertEqual(self.client.get(self.path).status_code, 403)
            self.assertEqual(self.client.patch(
                f"{self.path}/{request_id}", json={"status": "accepted"}
            ).status_code, 403)
        self.current_user = self.admin
        self.assertEqual(self.client.patch(
            f"{self.path}/{request_id}", json={"status": "pending"}
        ).status_code, 422)
        self.assertEqual(self.client.patch(
            f"{self.path}/999999", json={"status": "accepted"}
        ).status_code, 404)
        self.current_user = self.requester
        self.assertEqual(self.client.post(
            "/api/v1/vacancies/999999/join-requests"
        ).status_code, 404)
        self.assertEqual(self.session.get(VacancyJoinRequest, request_id).status,
                         JoinRequestStatus.PENDING)

    def test_cannot_request_when_already_participant_or_after_end(self):
        self.session.add(VacancyParticipant(
            id_vacancy=self.vacancy.id, id_user=self.requester.id
        ))
        self.session.commit()
        self.assertEqual(self.client.post(self.path).status_code, 409)
        self.session.query(VacancyParticipant).delete()
        self.vacancy.ends_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1)
        self.session.commit()
        self.assertEqual(self.client.post(self.path).status_code, 409)

    def test_accepting_invitation_cancels_pending_request(self):
        request_id = self.client.post(self.path).json()["id"]
        self.current_user = self.admin
        invitation = self.client.post("/api/v1/invitations", json={
            "recipient_email": self.requester.email.upper(),
            "invitation_type": "vacancy",
            "target_id": self.vacancy.id,
        })
        self.assertEqual(invitation.status_code, 202)
        self.assertEqual(
            invitation.json()["message"],
            "Se o e-mail estiver cadastrado e puder receber o convite, ele será enviado.",
        )
        created_invitation = self.session.scalar(select(Invitation).where(
            Invitation.sender_id == self.admin.id,
            Invitation.recipient_id == self.requester.id,
            Invitation.target_id == self.vacancy.id,
        ))
        self.assertIsNotNone(created_invitation)
        self.current_user = self.requester
        response = self.client.patch(
            f"/api/v1/invitations/{created_invitation.id}/response",
            json={"status": "accepted"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.session.get(VacancyJoinRequest, request_id).status,
            JoinRequestStatus.CANCELED,
        )
        self.current_user = self.editor
        self.assertEqual(self.client.get(self.path).json(), [])


if __name__ == "__main__":
    unittest.main()
