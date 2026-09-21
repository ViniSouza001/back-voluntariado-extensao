import unittest
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - registra os models no metadata
from app.core.exceptions import ConflictError, ForbiddenError, ValidationError
from app.db.base import Base
from app.models.entity import Entity
from app.models.invitation import Invitation, InvitationStatus, InvitationType
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.vacancy import Vacancies, VacancyBranch, VacancyModality
from app.models.vacancy_participant import VacancyParticipant
from app.schemas.invitation import CreateInvitation, RespondInvitation
from app.services.invitations import InvitationService


class InvitationPermissionTests(unittest.TestCase):
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
        self.other_admin = self.create_user(4, "Outro admin")
        self.recipient = self.create_user(5, "Destinatário")

        self.entity = self.create_entity("entidade-principal")
        self.other_entity = self.create_entity("outra-entidade")
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
            MemberEntity(
                id_user=self.other_admin.id,
                id_entity=self.other_entity.id,
                position=MemberPosition.ADMIN,
            ),
        ])

        starts_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=1)
        self.vacancy = Vacancies(
            title="Apoio comunitário",
            description="Atividade voluntária",
            id_entity=self.entity.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            branch=VacancyBranch.COMMUNITY,
            modality=VacancyModality.REMOTE,
        )
        self.session.add(self.vacancy)
        self.session.commit()
        self.service = InvitationService(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def create_user(self, suffix: int, name: str) -> User:
        user = User(
            name=name,
            cpf=f"{suffix:011d}",
            email=f"user{suffix}@example.com",
            password="test",
            birth_date=date(2000, 1, 1),
            city="São Paulo",
            uf="SP",
        )
        self.session.add(user)
        return user

    def create_entity(self, slug: str) -> Entity:
        entity = Entity(
            name=slug.replace("-", " ").title(),
            slug=slug,
            sector="Assistência social",
            description="Entidade usada nos testes",
            city="São Paulo",
            uf="SP",
        )
        self.session.add(entity)
        return entity

    def invitation_data(
        self, invitation_type: InvitationType, target_id: int
    ) -> CreateInvitation:
        return CreateInvitation(
            recipient_id=self.recipient.id,
            invitation_type=invitation_type,
            target_id=target_id,
        )

    def test_only_admin_of_target_entity_can_create_entity_invitation(self):
        data = self.invitation_data(InvitationType.ENTITY, self.entity.id)

        response = self.service.create_invitation(data, self.admin)

        self.assertEqual(response.target.id, self.entity.id)
        self.assertEqual(response.invitation_type, InvitationType.ENTITY)

        for unauthorized_user in (self.editor, self.member, self.other_admin):
            with self.subTest(user=unauthorized_user.name):
                with self.assertRaises(ForbiddenError):
                    self.service.create_invitation(data, unauthorized_user)

    def test_admin_and_editor_of_vacancy_entity_can_invite(self):
        data = self.invitation_data(InvitationType.VACANCY, self.vacancy.id)

        for authorized_user in (self.admin, self.editor):
            with self.subTest(user=authorized_user.name):
                response = self.service.create_invitation(data, authorized_user)
                self.assertEqual(response.target.id, self.vacancy.id)
                self.service.respond_to_invitation(
                    response.id,
                    RespondInvitation(status=InvitationStatus.REJECTED),
                    self.recipient,
                )

    def test_member_and_user_from_another_entity_cannot_invite_to_vacancy(self):
        data = self.invitation_data(InvitationType.VACANCY, self.vacancy.id)

        for unauthorized_user in (self.member, self.other_admin):
            with self.subTest(user=unauthorized_user.name):
                with self.assertRaises(ForbiddenError):
                    self.service.create_invitation(data, unauthorized_user)

        invitations = self.session.scalars(select(Invitation)).all()
        self.assertEqual(invitations, [])

    def test_list_separates_received_and_sent_invitations(self):
        received_data = self.invitation_data(
            InvitationType.ENTITY, self.entity.id
        )
        received_invitation = self.service.create_invitation(
            received_data, self.admin
        )

        sent_invitation = self.service.create_invitation(
            CreateInvitation(
                recipient_id=self.admin.id,
                invitation_type=InvitationType.FRIEND,
            ),
            self.recipient,
        )

        self.service.create_invitation(
            CreateInvitation(
                recipient_id=self.member.id,
                invitation_type=InvitationType.FRIEND,
            ),
            self.editor,
        )

        invitations = self.service.list_invitations(self.recipient)

        self.assertEqual(
            [invitation.id for invitation in invitations.received],
            [received_invitation.id],
        )
        self.assertEqual(
            [invitation.id for invitation in invitations.sent],
            [sent_invitation.id],
        )
        self.assertEqual(invitations.received[0].target.id, self.entity.id)
        self.assertIsNone(invitations.sent[0].target)

    def test_recipient_can_accept_entity_invitation_and_become_member(self):
        created = self.service.create_invitation(
            self.invitation_data(InvitationType.ENTITY, self.entity.id),
            self.admin,
        )

        response = self.service.respond_to_invitation(
            created.id,
            RespondInvitation(status=InvitationStatus.ACCEPTED),
            self.recipient,
        )

        membership = self.session.scalar(
            select(MemberEntity).where(
                MemberEntity.id_user == self.recipient.id,
                MemberEntity.id_entity == self.entity.id,
            )
        )
        self.assertEqual(response.status, InvitationStatus.ACCEPTED)
        self.assertIsNotNone(membership)
        self.assertEqual(membership.position, MemberPosition.MEMBER)

        recipient_notifications = self.session.scalars(
            select(Notification).where(
                Notification.recipient_id == self.recipient.id
            )
        ).all()
        self.assertEqual(
            [notification.notification_type for notification in recipient_notifications],
            [
                NotificationType.INVITATION_RECEIVED,
                NotificationType.ENTITY_MEMBER_JOINED,
            ],
        )
        self.assertEqual(recipient_notifications[1].entity_id, self.entity.id)

        sender_notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.admin.id
            )
        )
        self.assertEqual(
            sender_notification.notification_type,
            NotificationType.INVITATION_ACCEPTED,
        )
        self.assertEqual(sender_notification.invitation_id, created.id)

    def test_recipient_can_reject_invitation_without_joining_entity(self):
        created = self.service.create_invitation(
            self.invitation_data(InvitationType.ENTITY, self.entity.id),
            self.admin,
        )

        response = self.service.respond_to_invitation(
            created.id,
            RespondInvitation(status=InvitationStatus.REJECTED),
            self.recipient,
        )

        membership = self.session.scalar(
            select(MemberEntity).where(MemberEntity.id_user == self.recipient.id)
        )
        self.assertEqual(response.status, InvitationStatus.REJECTED)
        self.assertIsNone(membership)
        sender_notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.admin.id
            )
        )
        self.assertEqual(
            sender_notification.notification_type,
            NotificationType.INVITATION_REJECTED,
        )

    def test_only_recipient_can_respond_and_only_once(self):
        created = self.service.create_invitation(
            self.invitation_data(InvitationType.VACANCY, self.vacancy.id),
            self.admin,
        )
        accepted = RespondInvitation(status=InvitationStatus.ACCEPTED)

        with self.assertRaises(ForbiddenError):
            self.service.respond_to_invitation(created.id, accepted, self.admin)

        response = self.service.respond_to_invitation(
            created.id, accepted, self.recipient
        )
        self.assertEqual(response.status, InvitationStatus.ACCEPTED)
        participant = self.session.scalar(
            select(VacancyParticipant).where(
                VacancyParticipant.id_vacancy == self.vacancy.id,
                VacancyParticipant.id_user == self.recipient.id,
            )
        )
        self.assertIsNotNone(participant)
        joined_notification = self.session.scalar(
            select(Notification).where(
                Notification.recipient_id == self.recipient.id,
                Notification.notification_type
                == NotificationType.VACANCY_PARTICIPANT_JOINED,
            )
        )
        self.assertIsNotNone(joined_notification)
        self.assertEqual(joined_notification.actor_id, self.admin.id)
        self.assertEqual(joined_notification.vacancy_id, self.vacancy.id)

        with self.assertRaises(ConflictError):
            self.service.respond_to_invitation(
                created.id,
                RespondInvitation(status=InvitationStatus.REJECTED),
                self.recipient,
            )

    def test_user_cannot_invite_themself(self):
        data = CreateInvitation(
            recipient_id=self.admin.id,
            invitation_type=InvitationType.ENTITY,
            target_id=self.entity.id,
        )

        with self.assertRaises(ValidationError):
            self.service.create_invitation(data, self.admin)

    def test_user_already_in_entity_cannot_receive_entity_invitation(self):
        data = CreateInvitation(
            recipient_id=self.editor.id,
            invitation_type=InvitationType.ENTITY,
            target_id=self.entity.id,
        )

        with self.assertRaises(ConflictError):
            self.service.create_invitation(data, self.admin)

    def test_duplicate_pending_invitation_is_rejected(self):
        data = self.invitation_data(InvitationType.ENTITY, self.entity.id)
        self.service.create_invitation(data, self.admin)

        with self.assertRaises(ConflictError):
            self.service.create_invitation(data, self.admin)

    def test_vacancy_participant_cannot_be_invited_again(self):
        data = self.invitation_data(InvitationType.VACANCY, self.vacancy.id)
        invitation = self.service.create_invitation(data, self.admin)
        self.service.respond_to_invitation(
            invitation.id,
            RespondInvitation(status=InvitationStatus.ACCEPTED),
            self.recipient,
        )

        with self.assertRaises(ConflictError):
            self.service.create_invitation(data, self.editor)

    def test_only_recipient_can_mark_invitation_as_read(self):
        created = self.service.create_invitation(
            self.invitation_data(InvitationType.ENTITY, self.entity.id),
            self.admin,
        )

        with self.assertRaises(ForbiddenError):
            self.service.mark_as_read(created.id, self.admin)

        first_read = self.service.mark_as_read(created.id, self.recipient)
        second_read = self.service.mark_as_read(created.id, self.recipient)

        self.assertIsNotNone(first_read.read_at)
        self.assertEqual(first_read.read_at, second_read.read_at)

    def test_archive_hides_only_the_current_users_copy(self):
        created = self.service.create_invitation(
            self.invitation_data(InvitationType.ENTITY, self.entity.id),
            self.admin,
        )

        self.service.archive_invitation(created.id, self.recipient)

        recipient_invitations = self.service.list_invitations(self.recipient)
        sender_invitations = self.service.list_invitations(self.admin)
        self.assertEqual(recipient_invitations.received, [])
        self.assertEqual(
            [invitation.id for invitation in sender_invitations.sent],
            [created.id],
        )
        self.assertIsNotNone(self.session.get(Invitation, created.id))

        self.service.archive_invitation(created.id, self.admin)
        sender_invitations = self.service.list_invitations(self.admin)
        self.assertEqual(sender_invitations.sent, [])

    def test_unrelated_user_cannot_archive_invitation(self):
        created = self.service.create_invitation(
            self.invitation_data(InvitationType.ENTITY, self.entity.id),
            self.admin,
        )

        with self.assertRaises(ForbiddenError):
            self.service.archive_invitation(created.id, self.member)


if __name__ == "__main__":
    unittest.main()
