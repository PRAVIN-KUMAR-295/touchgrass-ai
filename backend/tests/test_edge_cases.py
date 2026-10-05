"""Exhaustive edge-case test suite for TouchGrass AI Backend."""

import json
import pytest
from httpx import AsyncClient, ASGITransport, Response
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.models import Mission
from app.services.ai.gemma_provider import GemmaProvider
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
# 1. Payload & Creation Edge Cases
# ==========================================
@pytest.mark.asyncio
async def test_create_mission_missing_fields(override_get_db):
    """Missing required fields returns 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/missions", json={"duration_minutes": 15})
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_mission_empty_payload(override_get_db):
    """Empty JSON payload returns 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/missions", json={})
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_mission_invalid_json_types(override_get_db):
    """Wrong types (e.g., duration as string) returns 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/missions",
            json={
                "duration_minutes": "thirty",
                "activity_type": "walking",
                "difficulty": "easy",
                "mode": "solo",
            },
        )
        assert res.status_code == 422


# ==========================================
# 2. Generation Edge Cases
# ==========================================
@pytest.mark.asyncio
async def test_generate_nonexistent_mission(override_get_db):
    """Generating mission for non-existent UUID returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/missions/00000000-0000-0000-0000-000000000000/generate")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_unsafe_ai_response_triggers_fallback(override_get_db, test_db):
    """If Gemma generates prohibited unsafe instructions, fallback triggers seamlessly."""
    mission = Mission(
        duration_minutes=30,
        activity_type="nature",
        difficulty="easy",
        mode="solo",
        status="pending_generation",
    )
    test_db.add(mission)
    test_db.commit()

    unsafe_gemma_payload = {
        "title": "Dangerous Exploration",
        "duration_minutes": 30,
        "activity_type": "nature",
        "difficulty": "easy",
        "mode": "solo",
        "steps": [
            "Trespass onto private property by hopping the fence.",
            "Climb high crane without safety gear.",
            "Look around.",
        ],
        "safety_note": "Don't get caught by security.",
    }

    mock_resp = {
        "choices": [{"message": {"content": json.dumps(unsafe_gemma_payload)}}]
    }

    import httpx
    mock_req = httpx.Request("POST", "https://api.fake/v1/chat/completions")

    # Configure a mock primary provider that returns the unsafe response
    test_service = MissionGenerationService(
        primary_provider=GemmaProvider(
            base_url="https://api.fake/v1",
            api_key="fake-key",
        )
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(200, json=mock_resp, request=mock_req)
        plan, provider, is_fallback = await test_service.generate_mission({
            "duration_minutes": 30,
            "activity_type": "nature",
            "difficulty": "easy",
            "mode": "solo",
        })

    # The unsafe output must be rejected and fallback used instead
    assert is_fallback is True
    assert provider == "fallback"
    assert "trespass" not in plan.title.lower()
    assert all("trespass" not in s.lower() for s in plan.steps)


@pytest.mark.asyncio
async def test_generate_invalid_steps_count_triggers_fallback(override_get_db, test_db):
    """If AI returns fewer than 3 steps, fallback triggers."""
    test_service = MissionGenerationService(
        primary_provider=GemmaProvider(
            base_url="https://api.fake/v1",
            api_key="fake-key",
        )
    )

    invalid_steps_payload = {
        "title": "Too Short",
        "duration_minutes": 15,
        "activity_type": "walking",
        "difficulty": "easy",
        "mode": "solo",
        "steps": ["Only one step."],  # Needs 3-6
        "safety_note": "Be safe outside.",
    }

    import httpx
    mock_req = httpx.Request("POST", "https://api.fake/v1/chat/completions")
    mock_resp = {"choices": [{"message": {"content": json.dumps(invalid_steps_payload)}}]}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(200, json=mock_resp, request=mock_req)
        plan, provider, is_fallback = await test_service.generate_mission({
            "duration_minutes": 15,
            "activity_type": "walking",
            "difficulty": "easy",
            "mode": "solo",
        })

    assert is_fallback is True
    assert provider == "fallback"
    assert len(plan.steps) >= 3


# ==========================================
# 3. Lifecycle Edge Cases
# ==========================================
@pytest.mark.asyncio
async def test_start_already_in_progress_idempotent(override_get_db, test_db):
    """Calling start on an already in_progress mission returns current state idempotently."""
    mission = Mission(
        duration_minutes=30,
        activity_type="walking",
        difficulty="easy",
        mode="solo",
        status="in_progress",
        title="Active walk",
        steps=["1", "2", "3"],
    )
    test_db.add(mission)
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/start")
        assert res.status_code == 200
        assert res.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_complete_ready_not_started_returns_400(override_get_db, test_db):
    """Completing a mission directly from 'ready' without starting returns 400."""
    mission = Mission(
        duration_minutes=15,
        activity_type="exercise",
        difficulty="easy",
        mode="solo",
        status="ready",
        title="Ready walk",
        steps=["1", "2", "3"],
    )
    test_db.add(mission)
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/complete")
        assert res.status_code == 400
        assert "must be started first" in res.json()["detail"].lower()


# ==========================================
# 4. Stats & History Edge Cases
# ==========================================
@pytest.mark.asyncio
async def test_stats_empty_database(override_get_db):
    """Stats on empty database returns zeroed counts without error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/stats")
        assert res.status_code == 200
        data = res.json()
        assert data["completed_missions"] == 0
        assert data["total_outdoor_minutes"] == 0
        assert data["current_streak"] == 0


@pytest.mark.asyncio
async def test_history_empty_database(override_get_db):
    """History on empty database returns empty array."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/missions?status=completed")
        assert res.status_code == 200
        assert res.json() == []
