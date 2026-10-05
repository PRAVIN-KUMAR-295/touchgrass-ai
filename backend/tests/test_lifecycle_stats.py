"""Tests for Mission Lifecycle (Start, Complete, Invalid States), Stats, and History."""

from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.models import Mission

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


@pytest.mark.asyncio
async def test_start_ready_mission(override_get_db, test_db):
    """Test starting a ready mission transitions to in_progress with started_at timestamp."""
    mission = Mission(
        duration_minutes=30,
        activity_type="walking",
        difficulty="easy",
        mode="solo",
        status="ready",
        title="Walk outside",
        steps=["Step 1", "Step 2", "Step 3"],
        safety_note="Watch path",
        ai_provider="fallback",
    )
    test_db.add(mission)
    test_db.commit()
    test_db.refresh(mission)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/start")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "in_progress"
        assert data["started_at"] is not None

    db_record = test_db.query(Mission).filter(Mission.id == mission.id).first()
    assert db_record.status == "in_progress"
    assert db_record.started_at is not None


@pytest.mark.asyncio
async def test_start_missing_mission(override_get_db):
    """Test starting a non-existent mission returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/missions/non-existent-id/start")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_start_invalid_state_completed(override_get_db, test_db):
    """Test that starting an already completed mission returns 400."""
    mission = Mission(
        duration_minutes=15,
        activity_type="walking",
        difficulty="easy",
        mode="solo",
        status="completed",
        title="Walk",
        steps=["1", "2", "3"],
        safety_note="Safe",
        completed_at=datetime.now(timezone.utc),
    )
    test_db.add(mission)
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/start")
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_start_invalid_state_pending_generation(override_get_db, test_db):
    """Test starting a mission without generated steps returns 400."""
    mission = Mission(
        duration_minutes=15,
        activity_type="walking",
        difficulty="easy",
        mode="solo",
        status="pending_generation",
    )
    test_db.add(mission)
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/start")
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_complete_in_progress_mission(override_get_db, test_db):
    """Test completing an in_progress mission transitions to completed with completed_at timestamp."""
    mission = Mission(
        duration_minutes=30,
        activity_type="nature",
        difficulty="easy",
        mode="solo",
        status="in_progress",
        title="Nature walk",
        steps=["Step 1", "Step 2", "Step 3"],
        started_at=datetime.now(timezone.utc),
    )
    test_db.add(mission)
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/complete")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    db_record = test_db.query(Mission).filter(Mission.id == mission.id).first()
    assert db_record.status == "completed"
    assert db_record.completed_at is not None


@pytest.mark.asyncio
async def test_complete_missing_mission(override_get_db):
    """Test completing a non-existent mission returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/missions/non-existent-id/complete")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_complete_invalid_state_not_started(override_get_db, test_db):
    """Test completing a ready mission before starting returns 400."""
    mission = Mission(
        duration_minutes=30,
        activity_type="nature",
        difficulty="easy",
        mode="solo",
        status="ready",
        title="Nature",
        steps=["1", "2", "3"],
    )
    test_db.add(mission)
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/complete")
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_complete_already_completed(override_get_db, test_db):
    """Test completing an already completed mission returns 400."""
    mission = Mission(
        duration_minutes=30,
        activity_type="nature",
        difficulty="easy",
        mode="solo",
        status="completed",
        title="Nature",
        steps=["1", "2", "3"],
        completed_at=datetime.now(timezone.utc),
    )
    test_db.add(mission)
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/api/missions/{mission.id}/complete")
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_stats_and_streak_calculation(override_get_db, test_db):
    """Test GET /api/stats accurately calculates completed missions, minutes, and streaks."""
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    # Mission 1 completed today (30 min)
    m1 = Mission(
        duration_minutes=30,
        activity_type="nature",
        difficulty="easy",
        mode="solo",
        status="completed",
        completed_at=now,
    )
    # Mission 2 completed yesterday (15 min)
    m2 = Mission(
        duration_minutes=15,
        activity_type="walking",
        difficulty="easy",
        mode="solo",
        status="completed",
        completed_at=yesterday,
    )
    # Mission 3 pending (should not count)
    m3 = Mission(
        duration_minutes=60,
        activity_type="exercise",
        difficulty="hard",
        mode="solo",
        status="in_progress",
    )
    test_db.add_all([m1, m2, m3])
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/stats")
        assert res.status_code == 200
        data = res.json()
        assert data["completed_missions"] == 2
        assert data["total_outdoor_minutes"] == 45
        assert data["current_streak"] == 2


@pytest.mark.asyncio
async def test_history_list_filter(override_get_db, test_db):
    """Test GET /api/missions?status=completed returns only completed missions."""
    m_done = Mission(
        duration_minutes=30,
        activity_type="photography",
        difficulty="easy",
        mode="solo",
        status="completed",
        title="Photo walk",
    )
    m_pending = Mission(
        duration_minutes=15,
        activity_type="walking",
        difficulty="easy",
        mode="solo",
        status="pending_generation",
    )
    test_db.add_all([m_done, m_pending])
    test_db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/missions?status=completed")
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 1
        assert items[0]["status"] == "completed"
        assert items[0]["title"] == "Photo walk"
