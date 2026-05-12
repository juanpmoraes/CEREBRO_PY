from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.connection import get_db
from ..engines.graph_engine import GraphEngine
from ..models.schemas import EdgeCreate

router = APIRouter()

@router.post("/")
async def create_edge(edge: EdgeCreate, db: AsyncSession = Depends(get_db)):
    engine = GraphEngine(db)
    edge_id = await engine.create_edge(edge.dict())
    return {"id": edge_id, "message": "Aresta criada com sucesso"}
