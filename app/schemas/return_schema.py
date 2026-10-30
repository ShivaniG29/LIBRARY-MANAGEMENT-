from datetime import date
from typing import Literal

from pydantic import BaseModel


class ReturnRead(BaseModel):
    issue_id: int
    book_id: int
    member_id: int
    issue_date: date
    due_date: date
    return_date: date
    status: Literal["Returned"]
    overdue_days: int
    fine_amount: float
