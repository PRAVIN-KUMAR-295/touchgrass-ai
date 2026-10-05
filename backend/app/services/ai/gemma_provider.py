"""Gemma Provider using an OpenAI-compatible hosted endpoint."""

import json
import logging
import httpx
from typing import Dict, Any
from app.config import settings
from app.services.ai.base import BaseAIProvider
from app.schemas.plan import MissionPlan

logger = logging.getLogger(__name__)

GEMMA_SYSTEM_PROMPT = """You are the outdoor mission planner for TouchGrass AI.
Your job is to create short, practical, safe outdoor missions.
The purpose is to get the user OFF the screen.

Missions should encourage ordinary real-world activities such as:
- walking
- observing nature
- photography
- stretching
- visiting public outdoor spaces
- sitting outdoors
- talking with friends
- noticing surroundings

Never suggest:
- trespassing or private property
- dangerous roads, highways, or busy traffic
- unsafe climbing (trees, structures, cliffs)
- dangerous locations or abandoned buildings
- illegal activities
- risky physical challenges or stunts
- activities requiring specialized equipment
- extreme exercise without appropriate safety guidance

Output Requirements:
You must return ONLY a single valid JSON object strictly adhering to this schema:
{
  "title": "<string: inspiring title for the outdoor mission>",
  "duration_minutes": <integer: strictly matching user requested duration: 15, 30, or 60>,
  "activity_type": "<string: strictly matching user requested activity: walking, nature, photography, exercise, or social>",
  "difficulty": "<string: strictly matching user requested difficulty: easy, medium, or hard>",
  "mode": "<string: strictly matching user requested mode: solo or friends>",
  "steps": [
    "<string: concrete actionable outdoor step 1>",
    "<string: concrete actionable outdoor step 2>",
    "<string: concrete actionable outdoor step 3>"
  ],
  "safety_note": "<string: practical outdoor safety guidance for public spaces>"
}

The "steps" array must contain between 3 and 6 steps.
Do not return Markdown formatting (no ```json codeblocks).
Do not return conversational text, greetings, or explanations outside the JSON object.
"""


class GemmaProvider(BaseAIProvider):
    """OpenAI-compatible hosted inference provider for Gemma."""

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        model_name: str = None,
        timeout_seconds: float = 12.0,
    ):
        self.base_url = (base_url or settings.HOSTED_API_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.HOSTED_API_KEY
        self.model_name = model_name or settings.HOSTED_MODEL_NAME or "google/gemma-3-4b-it"
        self.timeout = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "gemma"

    def is_configured(self) -> bool:
        """Check if base URL and API key are configured."""
        return bool(self.base_url and self.api_key)

    async def generate_outdoor_mission(self, preferences: Dict[str, Any]) -> MissionPlan:
        """Call hosted Gemma endpoint and parse structured mission plan."""
        if not self.is_configured():
            raise ValueError("Gemma provider is not configured with base_url and api_key")

        prompt_user = (
            f"Generate an outdoor mission for:\n"
            f"- Available Duration: {preferences.get('duration_minutes')} minutes\n"
            f"- Activity Type: {preferences.get('activity_type')}\n"
            f"- Difficulty: {preferences.get('difficulty')}\n"
            f"- Mode: {preferences.get('mode')}\n"
            f"Respond with the required JSON object only."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": GEMMA_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_user},
            ],
            "temperature": 0.3,
            "max_tokens": 800,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"].strip()

        # Clean markdown codeblocks if model inadvertently added them
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        # Parse JSON
        parsed_json = json.loads(content)

        # Enforce exact preference alignment
        if parsed_json.get("duration_minutes") != preferences.get("duration_minutes"):
            raise ValueError("Generated duration does not match requested preference")
        if parsed_json.get("activity_type") != preferences.get("activity_type"):
            raise ValueError("Generated activity does not match requested preference")
        if parsed_json.get("difficulty") != preferences.get("difficulty"):
            raise ValueError("Generated difficulty does not match requested preference")
        if parsed_json.get("mode") != preferences.get("mode"):
            raise ValueError("Generated mode does not match requested preference")

        # Validate against strict Pydantic MissionPlan schema
        return MissionPlan.model_validate(parsed_json)
