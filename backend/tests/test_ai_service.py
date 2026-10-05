"""Tests for AI Service Abstraction, Gemma Provider, Fallback Provider, Safety, and API Generation."""

import json
import pytest
from httpx import AsyncClient, ASGITransport, Response
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.models import Mission
from app.schemas.plan import MissionPlan
from app.services.ai.gemma_provider import GemmaProvider
from app.services.ai.fallback import DeterministicFallbackProvider
from app.services.ai.safety import validate_mission_safety
from app.services.mission_service import MissionGenerationService

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(test_db):
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


# ==========================================
# 1. Safety Filter Unit Tests
# ==========================================
def test_safety_validation_safe():
    is_safe, _ = validate_mission_safety(
        title="Mindful Nature Walk",
        steps=["Step outside quietly.", "Observe three leaves.", "Sit on a public park bench."],
        safety_note="Watch your step on footpaths.",
    )
    assert is_safe is True


def test_safety_validation_trespassing():
    is_safe, reason = validate_mission_safety(
        title="Secret Explorer",
        steps=["Jump the fence onto private property.", "Walk quietly."],
        safety_note="Do not get caught.",
    )
    assert is_safe is False
    assert "private property" in reason.lower() or "fence" in reason.lower()


def test_safety_validation_dangerous_climbing():
    is_safe, reason = validate_mission_safety(
        title="High Altitude",
        steps=["Climbing crane or cliff without ropes.", "Look at view."],
        safety_note="Be careful.",
    )
    assert is_safe is False
    assert "climb" in reason.lower()


def test_safety_validation_screen_staring():
    is_safe, reason = validate_mission_safety(
        title="Digital Walk",
        steps=["Scroll Instagram while walking.", "Share live video."],
        safety_note="Watch the path.",
    )
    assert is_safe is False
    assert "screen-minimal" in reason.lower()


# ==========================================
# 2. Deterministic Fallback Unit Tests
# ==========================================
@pytest.mark.asyncio
async def test_deterministic_fallback_matches_preferences():
    provider = DeterministicFallbackProvider()
    for duration in [15, 30, 60]:
        for activity in ["walking", "nature", "photography", "exercise", "social"]:
            plan = await provider.generate_outdoor_mission({
                "duration_minutes": duration,
                "activity_type": activity,
                "difficulty": "medium",
                "mode": "solo",
            })
            assert plan.duration_minutes == duration
            assert plan.activity_type == activity
            assert len(plan.steps) >= 3 and len(plan.steps) <= 6
            assert len(plan.safety_note) >= 10


# ==========================================
# 3. Gemma Provider Unit Tests (Mocked)
# ==========================================
@pytest.mark.asyncio
async def test_gemma_provider_valid_response():
    provider = GemmaProvider(
        base_url="https://fake-endpoint.com/v1",
        api_key="fake-secret-key-for-mock",
        model_name="google/gemma-3-4b-it",
    )
    mock_payload = {
        "title": "30-Minute Tree Canopy Walk",
        "duration_minutes": 30,
        "activity_type": "nature",
        "difficulty": "easy",
        "mode": "solo",
        "steps": [
            "Walk into your nearest public park.",
            "Find three different tree types and inspect the leaves.",
            "Sit on a public bench and close your eyes for 3 minutes.",
        ],
        "safety_note": "Remain in open public areas and watch your footing.",
    }

    mock_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(mock_payload)
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        import httpx
        mock_req = httpx.Request("POST", "https://fake-endpoint.com/v1/chat/completions")
        mock_post.return_value = Response(200, json=mock_response, request=mock_req)
        plan = await provider.generate_outdoor_mission({
            "duration_minutes": 30,
            "activity_type": "nature",
            "difficulty": "easy",
            "mode": "solo",
        })

    assert plan.title == "30-Minute Tree Canopy Walk"
    assert plan.duration_minutes == 30
    assert len(plan.steps) == 3


@pytest.mark.asyncio
async def test_gemma_provider_malformed_json():
    provider = GemmaProvider(
        base_url="https://fake-endpoint.com/v1",
        api_key="fake-key",
    )
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(200, json={"choices": [{"message": {"content": "Not a JSON"}}]})
        with pytest.raises(Exception):
            await provider.generate_outdoor_mission({
                "duration_minutes": 15,
                "activity_type": "walking",
                "difficulty": "easy",
                "mode": "solo",
            })


@pytest.mark.asyncio
async def test_gemma_provider_wrong_duration():
    provider = GemmaProvider(
        base_url="https://fake-endpoint.com/v1",
        api_key="fake-key",
    )
    mock_payload = {
        "title": "60-Min Walk",
        "duration_minutes": 60,  # Requested was 15!
        "activity_type": "walking",
        "difficulty": "easy",
        "mode": "solo",
        "steps": ["Step 1", "Step 2", "Step 3"],
        "safety_note": "Be safe.",
    }
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        import httpx
        mock_req = httpx.Request("POST", "https://fake-endpoint.com/v1/chat/completions")
        mock_post.return_value = Response(200, json={"choices": [{"message": {"content": json.dumps(mock_payload)}}]}, request=mock_req)
        with pytest.raises(ValueError, match="does not match"):
            await provider.generate_outdoor_mission({
                "duration_minutes": 15,
                "activity_type": "walking",
                "difficulty": "easy",
                "mode": "solo",
            })


@pytest.mark.asyncio
async def test_gemma_provider_timeout_or_error():
    provider = GemmaProvider(
        base_url="https://fake-endpoint.com/v1",
        api_key="fake-key",
    )
    with patch("httpx.AsyncClient.post", side_effect=Exception("Connection timed out")):
        with pytest.raises(Exception):
            await provider.generate_outdoor_mission({
                "duration_minutes": 30,
                "activity_type": "nature",
                "difficulty": "easy",
                "mode": "solo",
            })


# ==========================================
# 4. MissionGenerationService & API Integration
# ==========================================
@pytest.mark.asyncio
async def test_service_falls_back_when_gemma_fails(override_get_db):
    """When Gemma fails or is unconfigured, fallback must succeed seamlessly."""
    service = MissionGenerationService(
        primary_provider=GemmaProvider(base_url="https://fake-url", api_key="fake"),
        fallback_provider=DeterministicFallbackProvider(),
    )
    with patch.object(service.primary_provider, "generate_outdoor_mission", side_effect=Exception("API Down")):
        plan, provider, is_fallback = await service.generate_mission({
            "duration_minutes": 30,
            "activity_type": "nature",
            "difficulty": "easy",
            "mode": "solo",
        })

    assert is_fallback is True
    assert provider == "fallback"
    assert plan.duration_minutes == 30
    assert plan.activity_type == "nature"
    assert len(plan.steps) >= 3


@pytest.mark.asyncio
async def test_api_mission_generate_endpoint_and_persistence(override_get_db, test_db):
    """Test POST /api/missions/{id}/generate end-to-end with persistence."""
    # 1. Create a mission first
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/missions",
            json={
                "duration_minutes": 30,
                "activity_type": "photography",
                "difficulty": "easy",
                "mode": "solo",
            },
        )
        assert res.status_code == 201
        mission_id = res.json()["id"]

        # 2. Call generate endpoint (unconfigured in test, triggers deterministic fallback)
        gen_res = await ac.post(f"/api/missions/{mission_id}/generate")
        assert gen_res.status_code == 200
        gen_data = gen_res.json()

        assert gen_data["id"] == mission_id
        assert gen_data["status"] == "ready"
        assert gen_data["title"] is not None
        assert isinstance(gen_data["steps"], list)
        assert len(gen_data["steps"]) >= 3
        assert gen_data["safety_note"] is not None
        assert gen_data["is_fallback"] is True
        assert "ready-made mission" in gen_data["message"]

    # 3. Verify SQLite persistence of AI fields
    db_record = test_db.query(Mission).filter(Mission.id == mission_id).first()
    assert db_record is not None
    assert db_record.status == "ready"
    assert db_record.title == gen_data["title"]
    assert len(db_record.steps) == len(gen_data["steps"])
    assert db_record.safety_note == gen_data["safety_note"]
