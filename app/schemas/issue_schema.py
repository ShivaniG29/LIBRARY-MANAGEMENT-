from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class IssueCreate(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)


class IssueRead(BaseModel):
    id: int
    book_id: int
    member_id: int
    issue_date: date
    due_date: date
    return_date: date | None
    status: Literal["Issued", "Returned", "Overdue"]
    fine_amount: float

    model_config = ConfigDict(from_attributes=True)
