from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.issue import Issue
from app.models.member import Member


def get_dashboard(db: Session) -> dict[str, int]:
    return {
        "total_books": db.scalar(
            select(func.count(Book.id)).where(Book.is_deleted.is_(False))
        ) or 0,
        "total_members": db.scalar(
            select(func.count(Member.id)).where(Member.is_deleted.is_(False))
        ) or 0,
        "total_available_copies": db.scalar(
            select(func.coalesce(func.sum(Book.available_copies), 0)).where(Book.is_deleted.is_(False))
        ) or 0,
        "currently_issued_books": db.scalar(
            select(func.count(Issue.id)).where(Issue.return_date.is_(None))
        ) or 0,
        "overdue_books": db.scalar(
            select(func.count(Issue.id)).where(
                Issue.return_date.is_(None), Issue.due_date < date.today()
            )
        ) or 0,
        "returned_books": db.scalar(
            select(func.count(Issue.id)).where(Issue.return_date.is_not(None))
        ) or 0,
    }
