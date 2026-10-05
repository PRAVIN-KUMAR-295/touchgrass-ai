"""TouchGrass AI Backend Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import Base, engine
from app.api.health import router as health_router
from app.api.missions import router as missions_router
from app.api.stats import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables and apply backward-compatible column migrations."""
    Base.metadata.create_all(bind=engine)

    # Ensure added AI columns exist for SQLite local databases
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            existing_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(missions)")).fetchall()]
            new_columns = [
                ("title", "VARCHAR(150)"),
                ("steps_json", "TEXT"),
                ("safety_note", "TEXT"),
                ("ai_provider", "VARCHAR(30)"),
            ]
            for col_name, col_type in new_columns:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE missions ADD COLUMN {col_name} {col_type}"))
            conn.commit()
    except Exception:
        pass
    yield


app = FastAPI(
    title="TouchGrass AI Backend",
    description="Backend API powering the TouchGrass AI outdoor mission planner.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router, prefix="/api", tags=["System"])
app.include_router(missions_router, prefix="/api", tags=["Missions"])
app.include_router(stats_router, prefix="/api", tags=["Stats"])


@app.get("/")
async def root():
    """Root redirect / information endpoint."""
    return {
        "name": "TouchGrass AI",
        "description": "Put down your phone, step outside, and touch grass.",
        "health": "/api/health",
        "ai_status": "/api/ai-status",
        "missions": "/api/missions",
        "stats": "/api/stats",
    }
