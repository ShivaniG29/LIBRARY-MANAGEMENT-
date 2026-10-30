from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (
        Index(
            "uq_issues_active_book_member",
            "book_id",
            "member_id",
            unique=True,
            sqlite_where=text("return_date IS NULL"),
            postgresql_where=text("return_date IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="RESTRICT"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="RESTRICT"), index=True)
    issue_date: Mapped[date] = mapped_column(Date, default=date.today)
    due_date: Mapped[date] = mapped_column(Date)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fine_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    @property
    def status(self) -> str:
        if self.return_date is not None:
            return "Returned"
        if self.due_date < date.today():
            return "Overdue"
        return "Issued"
