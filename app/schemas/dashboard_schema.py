from pydantic import BaseModel


class DashboardRead(BaseModel):
    total_books: int
    total_members: int
    total_available_copies: int
    currently_issued_books: int
    overdue_books: int
    returned_books: int
