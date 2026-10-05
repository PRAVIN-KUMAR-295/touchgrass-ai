"""Abstract Base Provider for AI outdoor mission generation."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from app.schemas.plan import MissionPlan


class BaseAIProvider(ABC):
    """Abstract interface defining outdoor mission generation capability."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier name."""
        pass

    @abstractmethod
    async def generate_outdoor_mission(self, preferences: Dict[str, Any]) -> MissionPlan:
        """
        Generate a structured, safe outdoor mission plan matching user preferences.
        Raises an exception if generation or schema validation fails.
        """
        pass
