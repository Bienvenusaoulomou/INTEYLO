from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, CreatedAt, UUIDPk


class Organization(UUIDPk, CreatedAt, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="fr")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")


class Membership(UUIDPk, CreatedAt, Base):
    __tablename__ = "memberships"

    org_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class MembershipRole(Base):
    __tablename__ = "membership_roles"

    membership_id: Mapped[UUID] = mapped_column(
        ForeignKey("memberships.id", ondelete="CASCADE"), primary_key=True
    )
    role_key: Mapped[str] = mapped_column(ForeignKey("roles.key"), primary_key=True)
    org_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)


class Invitation(UUIDPk, CreatedAt, Base):
    __tablename__ = "invitations"

    org_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    role_key: Mapped[str] = mapped_column(ForeignKey("roles.key"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    invited_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
