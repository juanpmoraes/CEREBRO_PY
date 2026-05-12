from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.connection import get_db
from ..engines.graph_engine import GraphEngine

router = APIRouter()

@router.get("/")
async def search(q: str, db: AsyncSession = Depends(get_db)):
    engine = GraphEngine(db)
    return await engine.search_nodes(q)
