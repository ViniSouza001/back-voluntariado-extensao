from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.entity_join_request import EntityJoinRequest, JoinRequestStatus
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.user import User
from app.repositories.entities import RepositoryEntity
from app.repositories.entity_join_requests import RepositoryEntityJoinRequest
from app.repositories.member_entities import RepositoryMemberEntity
from app.services.entity_membership import require_entity_position
from app.services.notifications import NotificationService


class EntityJoinRequestService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, entity_id: int, user: User) -> EntityJoinRequest:
        entity = RepositoryEntity.search_for_id(self.session, entity_id)
        if entity is None:
            raise NotFoundError("Entidade não encontrada")
        if RepositoryMemberEntity.search_by_user(self.session, user.id):
            raise ConflictError("Você já participa de uma entidade")
        if RepositoryEntityJoinRequest.search_pending(self.session, user.id, entity_id):
            raise ConflictError("Você já possui uma solicitação pendente para esta entidade")

        request = EntityJoinRequest(user_id=user.id, entity_id=entity_id)
        try:
            self.session.add(request)
            self.session.flush()
            notification_service = NotificationService(self.session)
            for membership in RepositoryMemberEntity.list_from_entity(
                self.session, entity_id
            ):
                if membership.position == MemberPosition.ADMIN:
                    notification_service.notify_entity_join_requested(
                        membership.id_user, request
                    )
            self.session.commit()
            self.session.refresh(request)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível criar a solicitação") from error
        except Exception:
            self.session.rollback()
            raise
        return request

    def list_for_user(self, user: User) -> list[EntityJoinRequest]:
        return RepositoryEntityJoinRequest.list_for_user(self.session, user.id)

    def list_for_entity(
        self, entity_id: int, actor: User, pending_only: bool = True
    ) -> list[EntityJoinRequest]:
        require_entity_position(
            self.session, actor.id, entity_id, {MemberPosition.ADMIN}
        )
        return RepositoryEntityJoinRequest.list_for_entity(
            self.session, entity_id, pending_only
        )

    def decide(
        self,
        entity_id: int,
        request_id: int,
        decision: JoinRequestStatus,
        actor: User,
    ) -> EntityJoinRequest:
        require_entity_position(
            self.session, actor.id, entity_id, {MemberPosition.ADMIN}
        )
        request = RepositoryEntityJoinRequest.search_for_id(self.session, request_id)
        if request is None or request.entity_id != entity_id:
            raise NotFoundError("Solicitação não encontrada")
        if request.status != JoinRequestStatus.PENDING:
            raise ConflictError("Esta solicitação já foi encerrada")

        if decision == JoinRequestStatus.ACCEPTED:
            if RepositoryMemberEntity.search_by_user(self.session, request.user_id):
                raise ConflictError("O usuário já participa de uma entidade")
            self.session.add(MemberEntity(
                id_user=request.user_id,
                id_entity=entity_id,
                position=MemberPosition.MEMBER,
            ))

        now = datetime.now(UTC).replace(tzinfo=None)
        request.status = decision
        request.reviewed_at = now
        request.reviewed_by_id = actor.id

        try:
            if decision == JoinRequestStatus.ACCEPTED:
                for other in RepositoryEntityJoinRequest.other_pending_for_user(
                    self.session, request.user_id, request.id
                ):
                    other.status = JoinRequestStatus.CANCELED
                    other.reviewed_at = now
                NotificationService(self.session).notify_entity_join_request_accepted(
                    request, actor.id
                )
            self.session.commit()
            self.session.refresh(request)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível decidir a solicitação") from error
        except Exception:
            self.session.rollback()
            raise
        return request
