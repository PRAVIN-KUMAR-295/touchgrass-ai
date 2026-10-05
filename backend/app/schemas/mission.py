"""Pydantic schemas for mission validation and serialization."""

from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, ConfigDict, Field

# Strict enum-like literals matching requirements
AllowedDuration = Literal[15, 30, 60]
AllowedActivity = Literal["walking", "nature", "photography", "exercise", "social"]
AllowedDifficulty = Literal["easy", "medium", "hard"]
AllowedMode = Literal["solo", "friends"]
AllowedStatus = Literal["pending_generation", "ready", "in_progress", "completed", "abandoned"]


class MissionCreateRequest(BaseModel):
    """Strict schema for user mission setup preferences."""

    duration_minutes: AllowedDuration = Field(
        ...,
        description="Available time in minutes: 15, 30, or 60",
        examples=[30],
    )
    activity_type: AllowedActivity = Field(
        ...,
        description="Type of outdoor activity: walking, nature, photography, exercise, or social",
        examples=["nature"],
    )
    difficulty: AllowedDifficulty = Field(
        ...,
        description="Mission difficulty: easy, medium, or hard",
        examples=["easy"],
    )
    mode: AllowedMode = Field(
        ...,
        description="Mission mode: solo or friends",
        examples=["solo"],
    )


class MissionResponse(BaseModel):
    """Schema for mission details returned by the API."""

    id: str
    duration_minutes: int
    activity_type: str
    difficulty: str
    mode: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    title: Optional[str] = None
    steps: Optional[List[str]] = None
    safety_note: Optional[str] = None
    ai_provider: Optional[str] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
