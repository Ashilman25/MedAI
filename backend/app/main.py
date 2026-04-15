from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded
from .config import get_settings
from .logging_config import logger
from .dependencies import limiter
from .routers import ask, ingest, expand

MAX_BODY_SIZE = 50 * 1024 * 1024  # 50MB

s = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    if s.OPENAI_API_KEY and not s.MOCK_COMPLETIONS:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=s.OPENAI_API_KEY)
            client.models.list()
            logger.info("OpenAI API key validated successfully")
        except Exception as e:
            logger.warning("OpenAI API key validation failed: %s", e)
            raise RuntimeError("Cannot start with invalid OPENAI_API_KEY")
    yield


app = FastAPI(title="MedAI‑RAG Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=s.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class LimitBodySizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_BODY_SIZE:
                    return JSONResponse(status_code=413, content={"detail": "Request body too large"})
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header"})
        return await call_next(request)


app.add_middleware(LimitBodySizeMiddleware)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
        headers={"Retry-After": str(getattr(exc, 'retry_after', 60))}
    )


app.include_router(ask.router)
app.include_router(ingest.router)
app.include_router(expand.router)
