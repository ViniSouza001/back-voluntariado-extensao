from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.models.notification import Notification


class RepositoryNotification:
    @staticmethod
    def create(session: Session, notification: Notification) -> Notification:
        session.add(notification)
        return notification

    @staticmethod
    def list_for_user(
        session: Session,
        id_user: int,
        unread_only: bool,
        limit: int,
        offset: int,
    ) -> list[Notification]:
        query = (
            select(Notification)
            .options(selectinload(Notification.actor))
            .where(
                Notification.recipient_id == id_user,
                Notification.archived_at.is_(None),
            )
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
            .offset(offset)
        )
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        return list(session.scalars(query).all())

    @staticmethod
    def count_unread(session: Session, id_user: int) -> int:
        count = session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.recipient_id == id_user,
                Notification.read_at.is_(None),
                Notification.archived_at.is_(None),
            )
        )
        return int(count or 0)

    @staticmethod
    def search_for_user_and_id(
        session: Session,
        id_user: int,
        id_notification: int,
    ) -> Notification | None:
        return session.scalar(
            select(Notification)
            .options(selectinload(Notification.actor))
            .where(
                Notification.id == id_notification,
                Notification.recipient_id == id_user,
            )
        )

    @staticmethod
    def mark_all_as_read(
        session: Session,
        id_user: int,
        read_at: datetime,
    ) -> int:
        result = session.execute(
            update(Notification)
            .where(
                Notification.recipient_id == id_user,
                Notification.read_at.is_(None),
                Notification.archived_at.is_(None),
            )
            .values(read_at=read_at)
        )
        return int(result.rowcount or 0)
