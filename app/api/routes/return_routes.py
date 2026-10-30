from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.return_schema import ReturnRead
from app.services import return_service

router = APIRouter(prefix="/returns", tags=["Returns"])


@router.post("/{issue_id}", response_model=ReturnRead, summary="Return a book",
             description="Record the return, restore one available copy, and calculate any overdue fine.")
def return_book(issue_id: int, db: Session = Depends(get_db)):
    return return_service.return_book(db, issue_id)


@router.get("/{issue_id}", response_model=ReturnRead, summary="Get return details")
def get_return(issue_id: int, db: Session = Depends(get_db)):
    return return_service.get_return(db, issue_id)
