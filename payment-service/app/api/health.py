from aiokafka import AIOKafkaClient
from fastapi import APIRouter
from sqlalchemy import text
from starlette import status
from starlette.responses import JSONResponse

from app.api.dependencies import DBDep
from app.core.config import settings
from app.core.logger import logger

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
async def ping():
    logger.info("healthcheck_called")
    return {"status": "ok"}


@router.get("/ready")
async def ready(db: DBDep) -> JSONResponse:
    logger.info("ready_called")

    checks = {"postgresql": "ok", "kafka": "ok"}
    status_code = status.HTTP_200_OK

    try:
        await db.session.execute(text("SELECT 1"))
    except Exception:
        checks["postgresql"] = "Unavailable"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    client = AIOKafkaClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_URL)
    try:
        await client.bootstrap()
    except Exception:
        checks["kafka"] = "Unavailable"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    finally:
        await client.close()

    return JSONResponse(status_code=status_code, content=checks)
