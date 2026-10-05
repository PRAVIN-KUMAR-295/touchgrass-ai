"""Database models for TouchGrass AI."""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.core.database import Base


class Mission(Base):
    """Outdoor mission record model."""

    __tablename__ = "missions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    duration_minutes = Column(Integer, nullable=False)
    activity_type = Column(String(30), nullable=False)
    difficulty = Column(String(20), nullable=False)
    mode = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="pending_generation")

    # AI Generated content fields
    title = Column(String(150), nullable=True)
    steps_json = Column(Text, nullable=True)  # JSON-encoded array of steps
    safety_note = Column(Text, nullable=True)
    ai_provider = Column(String(30), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def steps(self) -> Optional[List[str]]:
        """Deserialize JSON steps column into Python list."""
        if not self.steps_json:
            return None
        try:
            return json.loads(self.steps_json)
        except Exception:
            return []

    @steps.setter
    def steps(self, steps_list: List[str]):
        """Serialize Python list into JSON text column."""
        self.steps_json = json.dumps(steps_list) if steps_list is not None else None
