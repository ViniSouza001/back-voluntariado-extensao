from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.invitation import Invitation, InvitationStatus, InvitationType
from app.models.invitation_send_attempt import InvitationSendAttempt

class RepositoryInvitation:

    @staticmethod
    def create(session: Session, invitation: Invitation) -> Invitation:
        session.add(invitation)
        return invitation

    @staticmethod
    def search_received(session: Session, id_user: int) -> list[Invitation]:
        query = (
            select(Invitation)
            .options(
                selectinload(Invitation.sender),
                selectinload(Invitation.recipient),
            )
            .where(
                Invitation.recipient_id == id_user,
                Invitation.recipient_archived_at.is_(None),
            )
            .order_by(Invitation.sent_at.desc())
        )
        return list(session.scalars(query).all())

    @staticmethod
    def last_send_attempt(
        session: Session, sender_id: int
    ) -> InvitationSendAttempt | None:
        return session.scalar(
            select(InvitationSendAttempt)
            .where(InvitationSendAttempt.sender_id == sender_id)
            .order_by(
                InvitationSendAttempt.attempted_at.desc(),
                InvitationSendAttempt.id.desc(),
            )
            .limit(1)
        )

    @staticmethod
    def record_send_attempt(
        session: Session, sender_id: int
    ) -> InvitationSendAttempt:
        attempt = InvitationSendAttempt(sender_id=sender_id)
        session.add(attempt)
        return attempt

    @staticmethod
    def search_for_id(session: Session, id_invitation: int) -> Invitation | None:
        query = (
            select(Invitation)
            .options(
                selectinload(Invitation.sender),
                selectinload(Invitation.recipient),
            )
            .where(Invitation.id == id_invitation)
        )
        return session.scalar(query)

    @staticmethod
    def search_pending(
        session: Session,
        recipient_id: int,
        invitation_type: InvitationType,
        target_id: int | None,
    ) -> Invitation | None:
        return session.scalar(
            select(Invitation).where(
                Invitation.recipient_id == recipient_id,
                Invitation.invitation_type == invitation_type,
                Invitation.target_id == target_id,
                Invitation.status == InvitationStatus.PENDING,
            )
        )

    @staticmethod
    def delete_from_user(session: Session, id_user: int) -> None:
        session.execute(
            delete(Invitation).where(
                or_(
                    Invitation.sender_id == id_user,
                    Invitation.recipient_id == id_user,
                )
            )
        )


    # def search(sender_id: int | None, recipient_id: int | None, )
    
