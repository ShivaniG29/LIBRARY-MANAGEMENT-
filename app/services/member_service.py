from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.member import Member
from app.schemas.member_schema import MemberCreate, MemberUpdate
from app.services.common import commit_or_conflict, not_found, paginate


def create_member(db: Session, data: MemberCreate) -> Member:
    values = data.model_dump()
    values["email"] = str(values["email"]).lower()
    values["is_active"] = values.pop("membership_status") == "Active"
    member = Member(**values)
    db.add(member)
    commit_or_conflict(db, "A member with this email already exists.")
    db.refresh(member)
    return member


def list_members(db: Session, limit: int, offset: int, membership_status: str | None):
    query = select(Member).where(Member.is_deleted.is_(False))
    if membership_status is not None:
        query = query.where(Member.is_active.is_(membership_status == "Active"))
    return paginate(db, query, limit, offset)


def get_member(db: Session, member_id: int) -> Member:
    member = db.scalar(select(Member).where(Member.id == member_id, Member.is_deleted.is_(False)))
    if member is None:
        raise not_found("Member")
    return member


def update_member(db: Session, member_id: int, data: MemberUpdate) -> Member:
    member = get_member(db, member_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        if field == "membership_status":
            member.is_active = value == "Active"
            continue
        if field == "email":
            value = str(value).lower()
        elif isinstance(value, str):
            value = value.strip()
        setattr(member, field, value)
    commit_or_conflict(db, "A member with this email already exists.")
    db.refresh(member)
    return member


def delete_member(db: Session, member_id: int) -> None:
    member = get_member(db, member_id)
    active_issue = db.scalar(
        select(Issue.id).where(Issue.member_id == member_id, Issue.return_date.is_(None)).limit(1)
    )
    if active_issue is not None:
        raise HTTPException(status_code=409, detail="A member with active issues cannot be deleted.")
    member.is_deleted = True
    db.commit()
