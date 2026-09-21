from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.member_entity import MemberPosition
from app.models.user import User
from app.repositories.member_entities import RepositoryMemberEntity
from app.repositories.member_positions import count_entity_admins
from app.repositories.entities import RepositoryEntity
from app.schemas.entity_membership import EntityMemberResponse
from app.schemas.user import UserSummary
from app.services.entity_membership import require_entity_position
from app.services.notifications import NotificationService


class EntityMemberService:
    def __init__(self, session: Session):
        self.session = session

    def list_members(
        self,
        id_entity: int,
        user: User,
    ) -> list[EntityMemberResponse]:
        require_entity_position(
            self.session,
            user.id,
            id_entity,
            {
                MemberPosition.ADMIN,
                MemberPosition.EDITOR,
                MemberPosition.MEMBER,
            },
        )

        memberships = RepositoryMemberEntity.list_from_entity(
            self.session, id_entity
        )
        return [
            EntityMemberResponse(
                user=UserSummary.model_validate(membership.user),
                position=membership.position,
            )
            for membership in memberships
        ]

    def remove_member(
        self,
        id_entity: int,
        id_user: int,
        actor: User,
    ) -> None:
        require_entity_position(
            self.session,
            actor.id,
            id_entity,
            {MemberPosition.ADMIN},
        )

        membership = RepositoryMemberEntity.search_by_user_and_entity(
            self.session, id_user, id_entity
        )
        if membership is None:
            raise NotFoundError("Membro não encontrado nesta entidade")

        entity = RepositoryEntity.search_for_id(self.session, id_entity)
        if entity is None:
            raise NotFoundError("Entidade não encontrada")

        if (
            membership.position == MemberPosition.ADMIN
            and count_entity_admins(self.session, id_entity) == 1
        ):
            raise ConflictError("A entidade precisa ter pelo menos um administrador")

        RepositoryMemberEntity.delete(self.session, membership)
        NotificationService(self.session).notify_entity_member_removed(
            id_user,
            actor.id,
            entity,
        )
        self.session.commit()

    def leave_entity(self, id_entity: int, user: User) -> None:
        membership = RepositoryMemberEntity.search_by_user_and_entity(
            self.session, user.id, id_entity
        )
        if membership is None:
            raise NotFoundError("Você não participa desta entidade")

        if (
            membership.position == MemberPosition.ADMIN
            and count_entity_admins(self.session, id_entity) == 1
        ):
            raise ConflictError(
                "O último administrador não pode sair da entidade"
            )

        entity = RepositoryEntity.search_for_id(self.session, id_entity)
        if entity is None:
            raise NotFoundError("Entidade não encontrada")

        RepositoryMemberEntity.delete(self.session, membership)
        NotificationService(self.session).notify_entity_left(
            user.id,
            entity,
        )
        self.session.commit()
