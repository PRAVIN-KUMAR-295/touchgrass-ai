"""Stats response schema."""

from pydantic import BaseModel, Field


class StatsResponse(BaseModel):
    """Outdoor activity statistics summary."""

    completed_missions: int = Field(
        ...,
        description="Total number of successfully completed outdoor missions",
        ge=0,
    )
    total_outdoor_minutes: int = Field(
        ...,
        description="Total cumulative minutes spent outdoors across completed missions",
        ge=0,
    )
    current_streak: int = Field(
        ...,
        description="Current consecutive calendar days with at least one completed outdoor mission",
        ge=0,
    )
