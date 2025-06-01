from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/strategy/scan")
async def strategy_scan(request: Request):
    data = await request.json()
    return {
        "message": "Strategy scan executed",
        "status": "success"
    }
