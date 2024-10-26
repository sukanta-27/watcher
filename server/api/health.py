# server/api/health.py

from fastapi import APIRouter, status
from typing import Dict
from sqlalchemy.sql import text
from server.db.session import engine

router = APIRouter()


@router.get(
    "/health",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Endpoint to check API and database health"
)
async def health_check() -> Dict[str, str]:
    health_status = {
        "status": "healthy",
        "api": "ok",
        "database": "ok"
    }

    # Check database connectivity
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as e:
        health_status["database"] = "error"
        health_status["status"] = "unhealthy"
        health_status["database_error"] = str(e)

    return health_status
