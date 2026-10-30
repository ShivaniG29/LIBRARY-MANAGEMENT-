from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=150)
    isbn: str = Field(min_length=1, max_length=20)
    category: str = Field(min_length=1, max_length=100)
    publisher: str = Field(min_length=1, max_length=150)
    published_year: int = Field(ge=0, le=9999)
    total_copies: int = Field(ge=1)

    @field_validator("title", "author", "isbn", "category", "publisher")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank.")
        return value


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=150)
    isbn: str | None = Field(default=None, min_length=1, max_length=20)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    publisher: str | None = Field(default=None, min_length=1, max_length=150)
    published_year: int | None = Field(default=None, ge=0, le=9999)
    total_copies: int | None = Field(default=None, ge=1)

    @field_validator("title", "author", "isbn", "category", "publisher")
    @classmethod
    def strip_update_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank.")
        return value


class BookRead(BookBase):
    id: int
    available_copies: int
    created_date: date

    model_config = ConfigDict(from_attributes=True)


class AvailabilityRead(BaseModel):
    book_id: int
    available: bool
    available_copies: int
