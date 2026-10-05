"""Mission Plan schema for structured AI generation."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.mission import (
    AllowedDuration,
    AllowedActivity,
    AllowedDifficulty,
    AllowedMode,
)


class MissionPlan(BaseModel):
    """Structured mission output schema required from AI providers."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Inspiring title for the outdoor mission",
    )
    duration_minutes: AllowedDuration = Field(
        ...,
        description="Duration in minutes strictly matching user preference (15, 30, or 60)",
    )
    activity_type: AllowedActivity = Field(
        ...,
        description="Activity type strictly matching user preference",
    )
    difficulty: AllowedDifficulty = Field(
        ...,
        description="Difficulty strictly matching user preference",
    )
    mode: AllowedMode = Field(
        ...,
        description="Mode strictly matching user preference",
    )
    steps: List[str] = Field(
        ...,
        min_length=3,
        max_length=6,
        description="3 to 6 practical, safe, real-world outdoor steps",
    )
    safety_note: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Sensible outdoor safety reminder",
    )

    model_config = ConfigDict(from_attributes=True)


class GeneratedMissionResponse(BaseModel):
    """API response after generating and persisting a mission."""

    id: str
    duration_minutes: int
    activity_type: str
    difficulty: str
    mode: str
    status: str
    title: Optional[str] = None
    steps: Optional[List[str]] = None
    safety_note: Optional[str] = None
    ai_provider: Optional[str] = None
    is_fallback: bool = False
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
