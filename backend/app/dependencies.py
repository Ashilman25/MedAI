from typing import Optional, Dict
from collections import defaultdict
from datetime import date
from fastapi import Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import firebase_admin
from firebase_admin import auth as firebase_auth
from .logging_config import logger

# Firebase init
try:
    firebase_admin.initialize_app()
except Exception as e:
    logger.warning("Firebase Admin SDK init failed: %s. Token verification will be unavailable.", e)


async def get_current_uid(authorization: str = Header(None)) -> Optional[str]:
    """Verify Firebase ID token from Authorization: Bearer <token> header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None  # guest/anonymous access
    token = authorization.split("Bearer ", 1)[1]
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def _rate_limit_key(request: Request) -> str:
    """Use authenticated UID if available, fall back to IP."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            token = auth.split("Bearer ", 1)[1]
            decoded = firebase_auth.verify_id_token(token)
            return decoded["uid"]
        except Exception:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key)


# In-memory per-user daily usage tracker
_daily_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: {"expand": 0, "ask": 0, "ingest": 0, "date": ""})

DAILY_LIMITS = {
    "expand": 25,
    "ask": 200,
    "ingest": 50,
}


def check_daily_limit(uid: str, operation: str):
    today = str(date.today())
    tracker = _daily_usage[uid or "anonymous"]
    if tracker["date"] != today:
        tracker.clear()
        tracker["date"] = today
    count = tracker.get(operation, 0)
    if count >= DAILY_LIMITS.get(operation, 999):
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached for {operation}. Try again tomorrow."
        )
    tracker[operation] = count + 1
