from fastapi import FastAPI

from app.api.middleware import LoggingMiddleware
from app.api.health import router as health_router

app = FastAPI(
    title="Analytics Service API"
)

app.add_middleware(LoggingMiddleware)

app.include_router(health_router, prefix="/api/v1")
