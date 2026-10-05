"""Health and AI status endpoints."""

from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app": "TouchGrass AI Backend",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@router.get("/ai-status")
async def ai_status():
    """Verify configured AI provider state without exposing secrets."""
    is_configured = bool(settings.HOSTED_API_BASE_URL and settings.HOSTED_API_KEY)
    return {
        "provider": settings.AI_PROVIDER,
        "model": settings.HOSTED_MODEL_NAME,
        "configured": is_configured,
        "fallback_available": True,
        "message": (
            "Gemma hosted endpoint configured"
            if is_configured
            else "Running in fallback mode (AI credentials not set)"
        ),
    }
