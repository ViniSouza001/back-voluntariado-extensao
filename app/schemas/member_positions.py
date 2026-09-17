from pydantic import BaseModel, ConfigDict

from app.models.member_entity import MemberPosition


class UpdateMemberPosition(BaseModel):
    position: MemberPosition


class MemberPositionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_user: int
    id_entity: int
    position: MemberPosition
