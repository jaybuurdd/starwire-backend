from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/health-check")
async def ping():
    return {"status": "OK"}