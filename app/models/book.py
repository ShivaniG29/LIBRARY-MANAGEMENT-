from datetime import date

from sqlalchemy import Boolean, Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (UniqueConstraint("isbn", name="uq_books_isbn"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    author: Mapped[str] = mapped_column(String(150), index=True)
    isbn: Mapped[str] = mapped_column(String(20), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    publisher: Mapped[str] = mapped_column(String(150))
    published_year: Mapped[int] = mapped_column(Integer)
    total_copies: Mapped[int] = mapped_column(Integer)
    available_copies: Mapped[int] = mapped_column(Integer)
    created_date: Mapped[date] = mapped_column(Date, default=date.today)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
