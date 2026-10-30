from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.common_schema import Page
from app.schemas.member_schema import MemberCreate, MemberRead, MemberUpdate
from app.services import member_service

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED,
             summary="Register a member")
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    return member_service.create_member(db, payload)


@router.get("", response_model=Page[MemberRead], summary="List members")
def list_members(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    membership_status: Literal["Active", "Inactive"] | None = None,
    db: Session = Depends(get_db),
):
    items, total = member_service.list_members(db, limit, offset, membership_status)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{member_id}", response_model=MemberRead, summary="Get a member")
def get_member(member_id: int, db: Session = Depends(get_db)):
    return member_service.get_member(db, member_id)


@router.put("/{member_id}", response_model=MemberRead, summary="Update a member")
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    return member_service.update_member(db, member_id, payload)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a member", description="Archive the member while preserving issue history.")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member_service.delete_member(db, member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
