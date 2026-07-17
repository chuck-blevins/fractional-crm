from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fractional_crm.reporting import active_engagements, monthly_run_rate
from fractional_crm.sqlite_repository import SqliteEngagementRepository
from fractional_crm.web.deps import get_engagement_repo

router = APIRouter(prefix="/api/reporting", tags=["reporting"])

class SummaryOut(BaseModel):
    """Summary output model."""
    active_count: int
    monthly_run_rate: float

@router.get("/summary")
def summary(repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> SummaryOut:
    """Get reporting summary."""
    engagements = repo.list()
    return SummaryOut(active_count=len(active_engagements(engagements)), monthly_run_rate=monthly_run_rate(engagements))
