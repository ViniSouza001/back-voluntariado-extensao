from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import ActualUser, BaseSession
from app.schemas.notification import (
    MarkAllNotificationsReadResponse,
    NotificationListResponse,
    NotificationResponse,
)
from app.services.notifications import NotificationService


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    user: ActualUser,
    session: BaseSession,
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return NotificationService(session).list_notifications(
        user,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/read-all",
    response_model=MarkAllNotificationsReadResponse,
)
def mark_all_notifications_as_read(
    user: ActualUser,
    session: BaseSession,
):
    return NotificationService(session).mark_all_as_read(user)


@router.patch("/{id_notification}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    id_notification: int,
    user: ActualUser,
    session: BaseSession,
):
    return NotificationService(session).mark_as_read(id_notification, user)


@router.patch(
    "/{id_notification}/archive",
    status_code=status.HTTP_204_NO_CONTENT,
)
def archive_notification(
    id_notification: int,
    user: ActualUser,
    session: BaseSession,
) -> Response:
    NotificationService(session).archive(id_notification, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
