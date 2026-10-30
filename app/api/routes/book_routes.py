from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.book_schema import AvailabilityRead, BookCreate, BookRead, BookUpdate
from app.schemas.common_schema import Page
from app.services import book_service

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED,
             summary="Add a book", description="Register a book with a unique ISBN.")
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, payload)


@router.get("", response_model=Page[BookRead], summary="List and search books",
            description="List books with pagination and optional partial-match filters.")
def list_books(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    title: str | None = None,
    author: str | None = None,
    isbn: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    items, total = book_service.list_books(db, limit, offset, title, author, isbn, category)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/search", response_model=Page[BookRead], summary="Search books",
            description="Search by title, author, ISBN, and/or category.")
def search_books(
    q: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = book_service.search_books(db, limit, offset, q)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{book_id}/availability", response_model=AvailabilityRead,
            summary="Check book availability")
def check_availability(book_id: int, db: Session = Depends(get_db)):
    return book_service.check_availability(db, book_id)


@router.get("/{book_id}", response_model=BookRead, summary="Get a book")
def get_book(book_id: int, db: Session = Depends(get_db)):
    return book_service.get_book(db, book_id)


@router.put("/{book_id}", response_model=BookRead, summary="Update a book")
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    return book_service.update_book(db, book_id, payload)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a book", description="Archive the book; historical issue records are retained.")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book_service.delete_book(db, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
