"""Stats API endpoints."""

from datetime import datetime, timezone, timedelta
from typing import Set
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models import Mission
from app.schemas.stats import StatsResponse

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Calculate and return completed mission stats:
    - total completed missions
    - total outdoor minutes
    - current streak (consecutive calendar days ending today or yesterday)
    """
    completed_missions = (
        db.query(Mission)
        .filter(Mission.status == "completed")
        .order_by(Mission.completed_at.desc())
        .all()
    )

    count = len(completed_missions)
    total_minutes = sum(m.duration_minutes for m in completed_missions)

    # Streak calculation based on UTC calendar dates
    if not completed_missions:
        return StatsResponse(
            completed_missions=0,
            total_outdoor_minutes=0,
            current_streak=0,
        )

    # Collect distinct dates where at least one mission was completed
    completed_dates: Set[datetime.date] = set()
    for m in completed_missions:
        if m.completed_at:
            completed_dates.add(m.completed_at.astimezone(timezone.utc).date())

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    streak = 0
    # Check if active today or yesterday
    if today in completed_dates:
        curr = today
    elif yesterday in completed_dates:
        curr = yesterday
    else:
        # Streak broken
        return StatsResponse(
            completed_missions=count,
            total_outdoor_minutes=total_minutes,
            current_streak=0,
        )

    # Count consecutive days backwards
    while curr in completed_dates:
        streak += 1
        curr -= timedelta(days=1)

    return StatsResponse(
        completed_missions=count,
        total_outdoor_minutes=total_minutes,
        current_streak=streak,
    )
