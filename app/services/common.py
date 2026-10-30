from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found.")


def commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=message) from exc


def paginate(db: Session, query, limit: int, offset: int):
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    items = db.scalars(query.offset(offset).limit(limit)).all()
    return items, total
