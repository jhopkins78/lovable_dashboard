from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/forecast/generate")
async def generate_forecast(request: Request):
    data = await request.json()
    return {
        "message": "Forecast generation executed",
        "status": "success"
    }
