from datetime import date

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.book import Book
from app.models.issue import Issue
from app.schemas.return_schema import ReturnRead
from app.services.common import not_found


def return_book(db: Session, issue_id: int) -> ReturnRead:
    issue = db.scalar(select(Issue).where(Issue.id == issue_id).with_for_update())
    if issue is None:
        raise not_found("Issue")
    if issue.return_date is not None:
        raise HTTPException(status_code=409, detail="This issue has already been returned.")
    today = date.today()
    overdue_days = max((today - issue.due_date).days, 0)
    fine_amount = round(overdue_days * settings.fine_per_day, 2)

    result = db.execute(
        update(Issue)
        .where(Issue.id == issue_id, Issue.return_date.is_(None))
        .values(return_date=today, fine_amount=fine_amount)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="This issue has already been returned.")

    result = db.execute(
        update(Book)
        .where(Book.id == issue.book_id, Book.available_copies < Book.total_copies)
        .values(available_copies=Book.available_copies + 1)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Returning this book would exceed its total copy count.")
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(issue)
    return ReturnRead(
        issue_id=issue.id,
        book_id=issue.book_id,
        member_id=issue.member_id,
        issue_date=issue.issue_date,
        due_date=issue.due_date,
        return_date=issue.return_date,
        status="Returned",
        overdue_days=overdue_days,
        fine_amount=issue.fine_amount,
    )


def get_return(db: Session, issue_id: int) -> ReturnRead:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise not_found("Issue")
    if issue.return_date is None:
        raise HTTPException(status_code=409, detail="This book has not been returned.")
    overdue_days = max((issue.return_date - issue.due_date).days, 0)
    return ReturnRead(
        issue_id=issue.id,
        book_id=issue.book_id,
        member_id=issue.member_id,
        issue_date=issue.issue_date,
        due_date=issue.due_date,
        return_date=issue.return_date,
        status="Returned",
        overdue_days=overdue_days,
        fine_amount=issue.fine_amount,
    )
