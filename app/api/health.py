"""Health check."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "klara-greenhouse"}


@router.post("/api/log-event")
async def log_event():
    # Stub to prevent frontend sendBeacon 404 errors in the console
    return {"success": True}

