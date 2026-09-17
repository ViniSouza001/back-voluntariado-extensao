from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.models.entity import Entity
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.user import User
from app.repositories.entities import RepositoryEntity
from app.repositories.member_entity import RepositoryMemberEntity
from app.schemas.entity import EntityCreation


class EntityService:
    def __init__(self, session: Session):
        self.session = session

    def get_for_user(self, user: User) -> MemberEntity | None:
        return RepositoryMemberEntity.search_by_user(self.session, user.id)

    def create(self, data: EntityCreation, creater: User) -> Entity:
        if RepositoryMemberEntity.search_by_user(self.session, creater.id):
            raise ConflictError("Você já participa de uma entidade")

        slug = data.slug.lower()
        if RepositoryEntity.search_for_slug(self.session, slug):
            raise ConflictError("Já existe uma entidade com este mesmo slug")

        entity = Entity(
            name = data.name.strip(),
            slug = slug,
            sector = data.sector.strip(),
            description = data.description.strip(),
            city = data.city.strip(),
            uf = data.uf.upper()
        )

        try:
            RepositoryEntity.add(self.session, entity)
            self.session.flush()
            self.session.add(
                MemberEntity(
                    id_user=creater.id,
                    id_entity=entity.id,
                    position=MemberPosition.ADMIN,
                )
            )
            self.session.commit()
            self.session.refresh(entity)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível criar a entidade: usuário ou slug já cadastrado") from error
        except Exception:
            self.session.rollback()
            raise
        return entity