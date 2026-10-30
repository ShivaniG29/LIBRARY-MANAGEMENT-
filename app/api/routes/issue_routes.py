from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.common_schema import Page
from app.schemas.issue_schema import IssueCreate, IssueRead
from app.services import issue_service

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("", response_model=IssueRead, status_code=status.HTTP_201_CREATED,
             summary="Issue a book", description="Issue an available book to an active member.")
def create_issue(payload: IssueCreate, db: Session = Depends(get_db)):
    return issue_service.create_issue(db, payload)


@router.get("", response_model=Page[IssueRead], summary="List active issues",
            description="List all currently issued or overdue books, optionally filtered by member.")
def list_issues(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    member_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    items, total = issue_service.list_issues(db, limit, offset, member_id)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{issue_id}", response_model=IssueRead, summary="Get issue details")
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    return issue_service.get_issue(db, issue_id)
