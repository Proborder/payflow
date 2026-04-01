import random

from fastapi import APIRouter, FastAPI, HTTPException, status

app = FastAPI()
router = APIRouter()

@router.post("/process-payment")
async def read_users(data: dict):
    num = random.randint(0, 10)
    if num < 2:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return {
        "status": "success", 
        "transaction_id": "tx_123456789",
    }

app.include_router(router)