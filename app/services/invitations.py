from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
)
from app.models.invitation import Invitation, InvitationStatus, InvitationType
from app.models.entity_join_request import JoinRequestStatus
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.user import User
from app.models.vacancy_participant import VacancyParticipant
from app.repositories.entities import RepositoryEntity
from app.repositories.invitations import RepositoryInvitation
from app.repositories.users import RepositoryUser
from app.repositories.vacancies import RepositoryVacancy
from app.repositories.vacancy_participants import RepositoryVacancyParticipant
from app.repositories.vacancy_join_requests import RepositoryVacancyJoinRequest
from app.schemas.invitation import (
    CreateInvitation,
    InvitationListsResponse,
    InvitationTarget,
    RespondInvitation,
    ResponseInvitation,
)
from app.schemas.user import UserSummary
from app.services.entity_membership import require_entity_position
from app.services.notifications import NotificationService
from app.repositories.member_entities import RepositoryMemberEntity


class InvitationService:
    SEND_COOLDOWN = timedelta(minutes=2)

    def __init__(self, session: Session):
        self.session = session

    def _get_invitation_target(
        self, invitation: Invitation
    ) -> InvitationTarget | None:
        if invitation.target_id is None:
            return None

        if invitation.invitation_type == InvitationType.ENTITY:
            entity = RepositoryEntity.search_for_id(
                self.session, invitation.target_id
            )
            if entity is not None:
                return InvitationTarget(id=entity.id, name=entity.name)

        if invitation.invitation_type == InvitationType.VACANCY:
            vacancy = RepositoryVacancy.search_for_id(
                self.session, invitation.target_id
            )
            if vacancy is not None:
                return InvitationTarget(id=vacancy.id, name=vacancy.title)

        return None

    def _build_response(
        self,
        invitation: Invitation,
        target: InvitationTarget | None = None,
    ) -> ResponseInvitation:
        return ResponseInvitation(
            id=invitation.id,
            sender=UserSummary.model_validate(invitation.sender),
            recipient=UserSummary.model_validate(invitation.recipient),
            sent_at=invitation.sent_at,
            status=invitation.status,
            invitation_type=invitation.invitation_type,
            target=target or self._get_invitation_target(invitation),
        )

    def create_invitation(
        self, data: CreateInvitation, user: User
    ) -> ResponseInvitation | None:
        target = None

        if data.invitation_type == InvitationType.ENTITY:
            entity = RepositoryEntity.search_for_id(self.session, data.target_id)

            if entity is None:
                raise NotFoundError("Entidade não encontrada")

            require_entity_position(
                self.session,
                user.id,
                entity.id,
                {MemberPosition.ADMIN},
            )

            target = InvitationTarget(id=entity.id, name=entity.name)

        elif data.invitation_type == InvitationType.VACANCY:
            vacancy = RepositoryVacancy.search_for_id(self.session, data.target_id)

            if vacancy is None:
                raise NotFoundError("Vaga não encontrada")

            require_entity_position(
                self.session,
                user.id,
                vacancy.id_entity,
                {MemberPosition.ADMIN, MemberPosition.EDITOR},
            )

            target = InvitationTarget(id=vacancy.id, name=vacancy.title)

        now = datetime.now(UTC).replace(tzinfo=None)
        last_attempt = RepositoryInvitation.last_send_attempt(self.session, user.id)
        if (
            last_attempt is not None
            and now - last_attempt.attempted_at < self.SEND_COOLDOWN
        ):
            raise RateLimitError(
                "Aguarde 2 minutos antes de enviar outro convite"
            )

        RepositoryInvitation.record_send_attempt(self.session, user.id)
        self.session.commit()

        recipient = RepositoryUser.search_for_email(
            self.session, str(data.recipient_email)
        )

        if recipient is None or recipient.id == user.id:
            return None

        if (
            data.invitation_type == InvitationType.ENTITY
            and RepositoryMemberEntity.search_by_user(self.session, recipient.id)
        ):
            return None

        if (
            data.invitation_type == InvitationType.VACANCY
            and RepositoryVacancyParticipant.search(
                self.session, data.target_id, recipient.id
            )
        ):
            return None

        if RepositoryInvitation.search_pending(
            self.session,
            recipient.id,
            data.invitation_type,
            data.target_id,
        ):
            return None

        invitation = Invitation(
            sender_id=user.id,
            recipient_id=recipient.id,
            invitation_type=data.invitation_type,
            target_id=data.target_id,
        )

        try:
            RepositoryInvitation.create(self.session, invitation)
            self.session.flush()
            NotificationService(self.session).notify_invitation_received(
                invitation,
                target.name if target else None,
            )
            self.session.commit()
            self.session.refresh(invitation)
        except IntegrityError:
            self.session.rollback()
            return None
        except Exception:
            self.session.rollback()
            raise

        return self._build_response(invitation, target)

    def list_invitations(self, user: User) -> InvitationListsResponse:
        invitations = RepositoryInvitation.search_received(self.session, user.id)
        return InvitationListsResponse(
            received=[self._build_response(invitation) for invitation in invitations]
        )

    def respond_to_invitation(
        self,
        id_invitation: int,
        data: RespondInvitation,
        user: User,
    ) -> ResponseInvitation:
        invitation = RepositoryInvitation.search_for_id(
            self.session, id_invitation
        )

        if invitation is None:
            raise NotFoundError("Convite não encontrado")

        if invitation.recipient_id != user.id:
            raise ForbiddenError("Somente o destinatário pode responder ao convite")

        if invitation.status != InvitationStatus.PENDING:
            raise ConflictError("Este convite já foi respondido")

        if (
            data.status == InvitationStatus.ACCEPTED
            and invitation.invitation_type == InvitationType.ENTITY
        ):
            entity = RepositoryEntity.search_for_id(
                self.session, invitation.target_id
            )
            if entity is None:
                raise NotFoundError("Entidade do convite não encontrada")

            if RepositoryMemberEntity.search_by_user(self.session, user.id):
                raise ConflictError("Você já participa de uma entidade")

            self.session.add(
                MemberEntity(
                    id_user=user.id,
                    id_entity=entity.id,
                    position=MemberPosition.MEMBER,
                )
            )

        if (
            data.status == InvitationStatus.ACCEPTED
            and invitation.invitation_type == InvitationType.VACANCY
        ):
            vacancy = RepositoryVacancy.search_for_id(
                self.session, invitation.target_id
            )
            if vacancy is None:
                raise NotFoundError("Vaga do convite não encontrada")

            if RepositoryVacancyParticipant.search(
                self.session, vacancy.id, user.id
            ):
                raise ConflictError("Você já participa desta vaga")

            RepositoryVacancyParticipant.create(
                self.session,
                VacancyParticipant(
                    id_vacancy=vacancy.id,
                    id_user=user.id,
                ),
            )
            pending_request = RepositoryVacancyJoinRequest.search_pending(
                self.session, user.id, vacancy.id
            )
            if pending_request is not None:
                pending_request.status = JoinRequestStatus.CANCELED
                pending_request.reviewed_at = datetime.now(UTC).replace(tzinfo=None)

        invitation.status = data.status

        try:
            notification_service = NotificationService(self.session)
            target = self._get_invitation_target(invitation)
            notification_service.notify_invitation_response(
                invitation,
                user.name,
                target.name if target else None,
            )

            if (
                data.status == InvitationStatus.ACCEPTED
                and invitation.invitation_type == InvitationType.ENTITY
            ):
                notification_service.notify_entity_joined(
                    user.id,
                    invitation.sender_id,
                    entity,
                )

            if (
                data.status == InvitationStatus.ACCEPTED
                and invitation.invitation_type == InvitationType.VACANCY
            ):
                notification_service.notify_vacancy_joined(
                    user.id,
                    invitation.sender_id,
                    vacancy,
                )

            self.session.commit()
            self.session.refresh(invitation)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível responder ao convite") from error
        except Exception:
            self.session.rollback()
            raise

        return self._build_response(invitation)

    def archive_invitation(self, id_invitation: int, user: User) -> None:
        invitation = RepositoryInvitation.search_for_id(
            self.session, id_invitation
        )
        if invitation is None:
            raise NotFoundError("Convite não encontrado")

        archived_at = datetime.now(UTC).replace(tzinfo=None)

        if invitation.sender_id == user.id:
            invitation.sender_archived_at = archived_at
        elif invitation.recipient_id == user.id:
            invitation.recipient_archived_at = archived_at
        else:
            raise ForbiddenError("Você não pode arquivar este convite")

        self.session.commit()
