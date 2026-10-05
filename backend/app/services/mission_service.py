"""Unified Mission Generation Service coordinating primary AI and fallback."""

import logging
from typing import Dict, Any, Tuple
from app.config import settings
from app.services.ai.base import BaseAIProvider
from app.services.ai.gemma_provider import GemmaProvider
from app.services.ai.fallback import DeterministicFallbackProvider
from app.services.ai.safety import validate_mission_safety
from app.schemas.plan import MissionPlan

logger = logging.getLogger(__name__)


class MissionGenerationService:
    """Orchestrates mission generation with safety enforcement and graceful fallback."""

    def __init__(
        self,
        primary_provider: BaseAIProvider = None,
        fallback_provider: BaseAIProvider = None,
    ):
        self.primary_provider = primary_provider or GemmaProvider()
        self.fallback_provider = fallback_provider or DeterministicFallbackProvider()

    async def generate_mission(
        self, preferences: Dict[str, Any]
    ) -> Tuple[MissionPlan, str, bool]:
        """
        Generate mission plan.
        Returns (plan, provider_name, is_fallback).
        Guaranteed to not raise an unhandled exception to the caller.
        """
        # Step 1: Try primary provider if configured
        if hasattr(self.primary_provider, "is_configured") and self.primary_provider.is_configured():
            try:
                logger.info(f"Generating mission with primary provider: {self.primary_provider.provider_name}")
                plan = await self.primary_provider.generate_outdoor_mission(preferences)

                # Step 2: Validate safety
                is_safe, reason = validate_mission_safety(
                    title=plan.title,
                    steps=plan.steps,
                    safety_note=plan.safety_note,
                )
                if is_safe:
                    return plan, self.primary_provider.provider_name, False
                else:
                    logger.warning(f"Primary provider generation rejected by safety filter: {reason}")
            except Exception as e:
                # Log without exposing secrets
                logger.warning(f"Primary provider generation failed ({type(e).__name__}). Falling back.")

        # Step 3: Deterministic fallback provider
        logger.info(f"Using fallback provider: {self.fallback_provider.provider_name}")
        fallback_plan = await self.fallback_provider.generate_outdoor_mission(preferences)

        # Safety check fallback as an extra safeguard
        is_safe, _ = validate_mission_safety(
            title=fallback_plan.title,
            steps=fallback_plan.steps,
            safety_note=fallback_plan.safety_note,
        )
        if not is_safe:
            # Under impossible event fallback fails safety, sanitize steps
            fallback_plan.steps = [
                "Step outside into the fresh open air.",
                "Take a calm walk in your local public space.",
                "Notice the sky, trees, and earth around you.",
            ]

        return fallback_plan, self.fallback_provider.provider_name, True
