from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.notification import NotificationType
from app.schemas.user import UserSummary


class CreateNotification(BaseModel):
    recipient_id: int
    actor_id: int | None = None
    notification_type: NotificationType
    title: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=255)
    invitation_id: int | None = None
    entity_id: int | None = None
    vacancy_id: int | None = None

    @model_validator(mode="after")
    def validate_related_resource(self):
        resources = (self.invitation_id, self.entity_id, self.vacancy_id)
        if sum(resource is not None for resource in resources) > 1:
            raise ValueError("A notificação pode referenciar somente um recurso")
        return self


class NotificationResponse(BaseModel):
    id: int
    notification_type: NotificationType
    title: str
    message: str
    actor: UserSummary | None
    resource_type: str | None
    resource_id: int | None
    created_at: datetime
    read_at: datetime | None


class NotificationListResponse(BaseModel):
    unread_count: int
    items: list[NotificationResponse]


class MarkAllNotificationsReadResponse(BaseModel):
    updated: int
