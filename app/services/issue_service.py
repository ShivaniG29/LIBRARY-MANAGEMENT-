from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.book import Book
from app.models.issue import Issue
from app.models.member import Member
from app.schemas.issue_schema import IssueCreate
from app.services.common import not_found, paginate


def create_issue(db: Session, data: IssueCreate) -> Issue:
    book = db.scalar(select(Book).where(Book.id == data.book_id, Book.is_deleted.is_(False)))
    if book is None:
        raise not_found("Book")
    member = db.scalar(select(Member).where(Member.id == data.member_id, Member.is_deleted.is_(False)))
    if member is None:
        raise not_found("Member")
    if not member.is_active:
        raise HTTPException(status_code=409, detail="Inactive members cannot borrow books.")
    duplicate = db.scalar(
        select(Issue.id).where(
            Issue.book_id == data.book_id,
            Issue.member_id == data.member_id,
            Issue.return_date.is_(None),
        ).limit(1)
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="This member already has an active issue for this book.")

    # The conditional update prevents two concurrent requests from issuing the last copy.
    result = db.execute(
        update(Book)
        .where(Book.id == data.book_id, Book.available_copies > 0, Book.is_deleted.is_(False))
        .values(available_copies=Book.available_copies - 1)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="No copies of this book are currently available.")
    today = date.today()
    issue = Issue(
        book_id=data.book_id,
        member_id=data.member_id,
        issue_date=today,
        due_date=today + timedelta(days=settings.loan_period_days),
    )
    db.add(issue)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This member already has an active issue for this book.",
        ) from exc
    except Exception:
        db.rollback()
        raise
    db.refresh(issue)
    return issue


def list_issues(db: Session, limit: int, offset: int, member_id: int | None):
    query = select(Issue).where(Issue.return_date.is_(None))
    if member_id is not None:
        query = query.where(Issue.member_id == member_id)
    return paginate(db, query, limit, offset)


def get_issue(db: Session, issue_id: int) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise not_found("Issue")
    return issue
