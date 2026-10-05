"""Tests for Mission validation, database persistence, and API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.models import Mission

# Use an isolated in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database schema for each test and tear it down after."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(test_db):
    """Override FastAPI dependency get_db with test database session."""
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_mission_valid(override_get_db):
    """Test mission creation with valid parameters."""
    payload = {
        "duration_minutes": 30,
        "activity_type": "nature",
        "difficulty": "easy",
        "mode": "solo",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/missions", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["duration_minutes"] == 30
    assert data["activity_type"] == "nature"
    assert data["difficulty"] == "easy"
    assert data["mode"] == "solo"
    assert data["status"] == "pending_generation"
    assert "id" in data
    assert "created_at" in data
    assert "Ready for AI generation" in data["message"]


@pytest.mark.asyncio
async def test_create_mission_invalid_duration(override_get_db):
    """Validation failure: duration not in [15, 30, 60]."""
    payload = {
        "duration_minutes": 45,  # Invalid
        "activity_type": "walking",
        "difficulty": "medium",
        "mode": "solo",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/missions", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_mission_invalid_activity(override_get_db):
    """Validation failure: arbitrary or unsupported activity string."""
    payload = {
        "duration_minutes": 15,
        "activity_type": "mountain_climbing",  # Invalid
        "difficulty": "hard",
        "mode": "solo",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/missions", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_mission_invalid_difficulty(override_get_db):
    """Validation failure: difficulty not easy, medium, or hard."""
    payload = {
        "duration_minutes": 30,
        "activity_type": "photography",
        "difficulty": "extreme",  # Invalid
        "mode": "solo",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/missions", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_mission_invalid_mode(override_get_db):
    """Validation failure: mode not solo or friends."""
    payload = {
        "duration_minutes": 60,
        "activity_type": "social",
        "difficulty": "medium",
        "mode": "online_clan",  # Invalid
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/missions", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_missions_list_and_persistence(override_get_db, test_db):
    """Test that missions are persisted in DB and returned newest first."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create first mission
        await ac.post(
            "/api/missions",
            json={
                "duration_minutes": 15,
                "activity_type": "walking",
                "difficulty": "easy",
                "mode": "solo",
            },
        )
        # Create second mission
        await ac.post(
            "/api/missions",
            json={
                "duration_minutes": 60,
                "activity_type": "exercise",
                "difficulty": "hard",
                "mode": "friends",
            },
        )

        # Query GET /api/missions
        res = await ac.get("/api/missions")
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 2
        # Verify ordering: newest created first
        assert items[0]["duration_minutes"] == 60
        assert items[0]["activity_type"] == "exercise"
        assert items[1]["duration_minutes"] == 15
        assert items[1]["activity_type"] == "walking"

    # Verify directly in SQLite test database
    db_count = test_db.query(Mission).count()
    assert db_count == 2
