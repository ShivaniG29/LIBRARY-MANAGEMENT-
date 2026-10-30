from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.issue import Issue
from app.schemas.book_schema import BookCreate, BookUpdate
from app.services.common import commit_or_conflict, not_found, paginate


def create_book(db: Session, data: BookCreate) -> Book:
    values = data.model_dump()
    values["isbn"] = values["isbn"].upper()
    book = Book(**values, available_copies=data.total_copies)
    db.add(book)
    commit_or_conflict(db, "A book with this ISBN already exists.")
    db.refresh(book)
    return book


def list_books(db: Session, limit: int, offset: int, title: str | None, author: str | None,
               isbn: str | None, category: str | None):
    query = select(Book).where(Book.is_deleted.is_(False))
    for column, value in ((Book.title, title), (Book.author, author),
                          (Book.isbn, isbn), (Book.category, category)):
        if value:
            query = query.where(column.ilike(f"%{value.strip()}%"))
    return paginate(db, query, limit, offset)


def search_books(db: Session, limit: int, offset: int, query_text: str | None):
    query = select(Book).where(Book.is_deleted.is_(False))
    if query_text:
        pattern = f"%{query_text.strip()}%"
        query = query.where(or_(
            Book.title.ilike(pattern),
            Book.author.ilike(pattern),
            Book.isbn.ilike(pattern),
            Book.category.ilike(pattern),
        ))
    return paginate(db, query, limit, offset)


def get_book(db: Session, book_id: int) -> Book:
    book = db.scalar(select(Book).where(Book.id == book_id, Book.is_deleted.is_(False)))
    if book is None:
        raise not_found("Book")
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "total_copies" in changes:
        issued_copies = book.total_copies - book.available_copies
        if changes["total_copies"] < issued_copies:
            raise HTTPException(status_code=409, detail="Total copies cannot be less than currently issued copies.")
        book.available_copies = changes["total_copies"] - issued_copies
    for field, value in changes.items():
        if field != "total_copies":
            if field == "isbn":
                value = value.upper()
            setattr(book, field, value)
    commit_or_conflict(db, "A book with this ISBN already exists.")
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    active_issue = db.scalar(
        select(Issue.id).where(Issue.book_id == book_id, Issue.return_date.is_(None)).limit(1)
    )
    if active_issue is not None:
        raise HTTPException(status_code=409, detail="A book with active issues cannot be deleted.")
    book.is_deleted = True
    db.commit()


def check_availability(db: Session, book_id: int) -> dict:
    book = get_book(db, book_id)
    return {"book_id": book.id, "available": book.available_copies > 0,
            "available_copies": book.available_copies}
