from pydantic import BaseModel, ConfigDict

from app.models.member_entity import MemberPosition
from app.schemas.entity import EntityResponse


class EntityMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity: EntityResponse
    position: MemberPosition
