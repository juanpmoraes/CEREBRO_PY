from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.connection import get_db
from ..engines.graph_engine import GraphEngine

router = APIRouter()

@router.get("/")
async def get_graph(db: AsyncSession = Depends(get_db)):
    engine = GraphEngine(db)
    return await engine.get_graph()

@router.get("/export")
async def export_graph(db: AsyncSession = Depends(get_db)):
    engine = GraphEngine(db)
    data = await engine.get_graph()
    return data # O FastAPI já retorna como JSON. Poderíamos formatar como arquivo se necessário.

