from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.invitation import Invitation, InvitationStatus, InvitationType

class RepositoryInvitation:

    @staticmethod
    def create(session: Session, invitation: Invitation) -> Invitation:
        session.add(invitation)
        return invitation

    @staticmethod
    def search_for_user(session: Session, id_user: int) -> list[Invitation]:
        query = (
            select(Invitation)
            .options(
                selectinload(Invitation.sender),
                selectinload(Invitation.recipient),
            )
            .where(
                or_(
                    and_(
                        Invitation.sender_id == id_user,
                        Invitation.sender_archived_at.is_(None),
                    ),
                    and_(
                        Invitation.recipient_id == id_user,
                        Invitation.recipient_archived_at.is_(None),
                    ),
                )
            )
            .order_by(Invitation.sent_at.desc())
        )
        return list(session.scalars(query).all())

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
    
