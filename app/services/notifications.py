from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.entity import Entity
from app.models.invitation import Invitation, InvitationStatus
from app.models.member_entity import MemberPosition
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.vacancy import Vacancies
from app.repositories.notifications import RepositoryNotification
from app.schemas.notification import (
    CreateNotification,
    MarkAllNotificationsReadResponse,
    NotificationListResponse,
    NotificationResponse,
)
from app.schemas.user import UserSummary


class NotificationService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: CreateNotification) -> Notification:
        """Add a notification to the current transaction without committing it."""
        notification = Notification(**data.model_dump())
        return RepositoryNotification.create(self.session, notification)

    def notify_invitation_received(
        self,
        invitation: Invitation,
        target_name: str | None,
    ) -> Notification:
        target_description = f" para {target_name}" if target_name else ""
        return self.create(CreateNotification(
            recipient_id=invitation.recipient_id,
            actor_id=invitation.sender_id,
            notification_type=NotificationType.INVITATION_RECEIVED,
            title="Você recebeu um convite",
            message=f"Você recebeu um novo convite{target_description}.",
            invitation_id=invitation.id,
        ))

    def notify_invitation_response(
        self,
        invitation: Invitation,
        recipient_name: str,
        target_name: str | None,
    ) -> Notification:
        accepted = invitation.status == InvitationStatus.ACCEPTED
        response_text = "aceitou" if accepted else "recusou"
        target_description = f" para {target_name}" if target_name else ""
        notification_type = (
            NotificationType.INVITATION_ACCEPTED
            if accepted
            else NotificationType.INVITATION_REJECTED
        )
        return self.create(CreateNotification(
            recipient_id=invitation.sender_id,
            actor_id=invitation.recipient_id,
            notification_type=notification_type,
            title=f"Convite {response_text}",
            message=(
                f"{recipient_name} {response_text} o convite"
                f"{target_description}."
            ),
            invitation_id=invitation.id,
        ))

    def notify_entity_joined(
        self,
        recipient_id: int,
        actor_id: int | None,
        entity: Entity,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=NotificationType.ENTITY_MEMBER_JOINED,
            title="Você entrou em uma entidade",
            message=f"Você agora participa da entidade {entity.name}.",
            entity_id=entity.id,
        ))

    def notify_entity_left(
        self,
        recipient_id: int,
        entity: Entity,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=recipient_id,
            notification_type=NotificationType.ENTITY_MEMBER_LEFT,
            title="Você saiu de uma entidade",
            message=f"Você saiu da entidade {entity.name}.",
            entity_id=entity.id,
        ))

    def notify_entity_member_removed(
        self,
        recipient_id: int,
        actor_id: int,
        entity: Entity,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=NotificationType.ENTITY_MEMBER_REMOVED,
            title="Você foi removido de uma entidade",
            message=f"Você foi removido da entidade {entity.name}.",
            entity_id=entity.id,
        ))

    def notify_entity_role_changed(
        self,
        recipient_id: int,
        actor_id: int,
        entity: Entity,
        old_position: MemberPosition,
        new_position: MemberPosition,
    ) -> Notification:
        position_names = {
            MemberPosition.ADMIN: "administrador",
            MemberPosition.EDITOR: "editor",
            MemberPosition.MEMBER: "membro",
        }
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=NotificationType.ENTITY_ROLE_CHANGED,
            title="Seu cargo foi alterado",
            message=(
                f"Seu cargo na entidade {entity.name} mudou de "
                f"{position_names[old_position]} para "
                f"{position_names[new_position]}."
            ),
            entity_id=entity.id,
        ))

    def notify_vacancy_created(
        self,
        actor_id: int,
        vacancy: Vacancies,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=actor_id,
            actor_id=actor_id,
            notification_type=NotificationType.VACANCY_CREATED,
            title="Vaga criada",
            message=f"A vaga {vacancy.title} foi criada com sucesso.",
            vacancy_id=vacancy.id,
        ))

    def notify_vacancy_updated(
        self,
        recipient_id: int,
        actor_id: int,
        vacancy: Vacancies,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=NotificationType.VACANCY_UPDATED,
            title="Uma vaga foi alterada",
            message=f"Os dados da vaga {vacancy.title} foram atualizados.",
            vacancy_id=vacancy.id,
        ))

    def notify_vacancy_deleted(
        self,
        recipient_id: int,
        actor_id: int,
        vacancy_title: str,
    ) -> Notification:
        # A vaga será excluída na mesma transação, então a notificação
        # preserva o título em vez de guardar uma referência que deixará de existir.
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=NotificationType.VACANCY_DELETED,
            title="Uma vaga foi excluída",
            message=f"A vaga {vacancy_title} foi excluída.",
        ))

    def notify_vacancy_joined(
        self,
        recipient_id: int,
        actor_id: int | None,
        vacancy: Vacancies,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=NotificationType.VACANCY_PARTICIPANT_JOINED,
            title="Você entrou em uma vaga",
            message=f"Você agora participa da vaga {vacancy.title}.",
            vacancy_id=vacancy.id,
        ))

    def notify_vacancy_left(
        self,
        recipient_id: int,
        vacancy: Vacancies,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=recipient_id,
            notification_type=NotificationType.VACANCY_PARTICIPANT_LEFT,
            title="Você saiu de uma vaga",
            message=f"Você saiu da vaga {vacancy.title}.",
            vacancy_id=vacancy.id,
        ))

    def notify_vacancy_participant_removed(
        self,
        recipient_id: int,
        actor_id: int,
        vacancy: Vacancies,
    ) -> Notification:
        return self.create(CreateNotification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            notification_type=NotificationType.VACANCY_PARTICIPANT_REMOVED,
            title="Você foi removido de uma vaga",
            message=f"Você foi removido da vaga {vacancy.title}.",
            vacancy_id=vacancy.id,
        ))

    def _build_response(self, notification: Notification) -> NotificationResponse:
        resource_type = None
        resource_id = None

        if notification.invitation_id is not None:
            resource_type = "invitation"
            resource_id = notification.invitation_id
        elif notification.entity_id is not None:
            resource_type = "entity"
            resource_id = notification.entity_id
        elif notification.vacancy_id is not None:
            resource_type = "vacancy"
            resource_id = notification.vacancy_id

        actor = None
        if notification.actor is not None:
            actor = UserSummary.model_validate(notification.actor)

        return NotificationResponse(
            id=notification.id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )

    def list_notifications(
        self,
        user: User,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> NotificationListResponse:
        notifications = RepositoryNotification.list_for_user(
            self.session,
            user.id,
            unread_only,
            limit,
            offset,
        )
        return NotificationListResponse(
            unread_count=RepositoryNotification.count_unread(
                self.session, user.id
            ),
            items=[
                self._build_response(notification)
                for notification in notifications
            ],
        )

    def mark_as_read(
        self,
        id_notification: int,
        user: User,
    ) -> NotificationResponse:
        notification = RepositoryNotification.search_for_user_and_id(
            self.session, user.id, id_notification
        )
        if notification is None:
            raise NotFoundError("Notificação não encontrada")

        if notification.read_at is None:
            notification.read_at = datetime.now(UTC).replace(tzinfo=None)
            self.session.commit()
            self.session.refresh(notification)

        return self._build_response(notification)

    def mark_all_as_read(
        self,
        user: User,
    ) -> MarkAllNotificationsReadResponse:
        updated = RepositoryNotification.mark_all_as_read(
            self.session,
            user.id,
            datetime.now(UTC).replace(tzinfo=None),
        )
        self.session.commit()
        return MarkAllNotificationsReadResponse(updated=updated)

    def archive(self, id_notification: int, user: User) -> None:
        notification = RepositoryNotification.search_for_user_and_id(
            self.session, user.id, id_notification
        )
        if notification is None:
            raise NotFoundError("Notificação não encontrada")

        if notification.archived_at is None:
            notification.archived_at = datetime.now(UTC).replace(tzinfo=None)
            self.session.commit()
