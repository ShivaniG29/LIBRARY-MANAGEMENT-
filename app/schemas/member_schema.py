from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class MemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=30)
    address: str = Field(min_length=1, max_length=300)
    membership_status: Literal["Active", "Inactive"] = "Active"

    @field_validator("name", "phone", "address")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank.")
        return value


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=1, max_length=30)
    address: str | None = Field(default=None, min_length=1, max_length=300)
    membership_status: Literal["Active", "Inactive"] | None = None

    @field_validator("name", "phone", "address")
    @classmethod
    def strip_update_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank.")
        return value


class MemberRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: str
    membership_date: date
    membership_status: Literal["Active", "Inactive"]

    model_config = ConfigDict(from_attributes=True)
