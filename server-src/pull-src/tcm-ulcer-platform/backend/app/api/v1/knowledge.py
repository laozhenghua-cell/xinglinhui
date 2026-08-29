from fastapi import APIRouter

router = APIRouter()


@router.get("/ulcers")
async def list_ulcer_knowledge():
    """疮疡知识库列表（移到 ulcers.py 中已实现）"""
    pass
