from fastapi import APIRouter

router = APIRouter(prefix="/healthz", include_in_schema=False)


@router.get("")
async def healthz():
    return {"status": "ok"}
