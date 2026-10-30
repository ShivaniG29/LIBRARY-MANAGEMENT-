from datetime import date

from sqlalchemy import Boolean, Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Member(Base):
    __tablename__ = "members"
    __table_args__ = (UniqueConstraint("email", name="uq_members_email"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254), index=True)
    phone: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(300))
    membership_date: Mapped[date] = mapped_column(Date, default=date.today)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @property
    def membership_status(self) -> str:
        return "Active" if self.is_active else "Inactive"
