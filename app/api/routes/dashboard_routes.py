from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.dashboard_schema import DashboardRead
from app.services.dashboard_service import get_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardRead, summary="Get library statistics",
            description="Return book, member, issue, overdue, and return totals.")
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard(db)
