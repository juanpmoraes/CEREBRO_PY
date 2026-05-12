from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import uuid
import json
from typing import List, Optional, Dict, Any

from ..models.schemas import NodeCreate, EdgeCreate, NodeResponse, EdgeResponse

class GraphEngine:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_node(self, node_data: Dict[str, Any]) -> str:
        node_id = str(uuid.uuid4())
        columns = ", ".join(node_data.keys())
        placeholders = ", ".join([f":{k}" for k in node_data.keys()])
        
        query = text(f"""
            INSERT INTO nodes (id, {columns})
            VALUES (:id, {placeholders})
        """)
        
        await self.session.execute(query, {"id": node_id, **node_data})
        await self.session.commit()
        return node_id

    async def get_node(self, node_id: str) -> Optional[Dict]:
        query = text("SELECT * FROM nodes WHERE id = :id")
        result = await self.session.execute(query, {"id": node_id})
        row = result.mappings().first()
        return dict(row) if row else None

    async def list_nodes(self, limit: int = 100) -> List[Dict]:
        query = text("SELECT * FROM nodes LIMIT :limit")
        result = await self.session.execute(query, {"limit": limit})
        return [dict(row) for row in result.mappings().all()]

    async def create_edge(self, edge_data: Dict[str, Any]) -> str:
        edge_id = str(uuid.uuid4())
        columns = ", ".join(edge_data.keys())
        placeholders = ", ".join([f":{k}" for k in edge_data.keys()])
        
        query = text(f"""
            INSERT INTO edges (id, {columns})
            VALUES (:id, {placeholders})
        """)
        
        await self.session.execute(query, {"id": edge_id, **edge_data})
        await self.session.commit()
        return edge_id

    async def get_graph(self) -> Dict:
        nodes_query = text("SELECT * FROM nodes")
        edges_query = text("SELECT * FROM edges")
        
        nodes_result = await self.session.execute(nodes_query)
        edges_result = await self.session.execute(edges_query)
        
        return {
            "nodes": [dict(row) for row in nodes_result.mappings().all()],
            "links": [dict(row) for row in edges_result.mappings().all()]
        }

    async def search_nodes(self, term: str) -> List[Dict]:
        # Busca usando FULLTEXT INDEX do MySQL
        query = text("""
            SELECT *, MATCH(name, summary) AGAINST (:term IN BOOLEAN MODE) AS score
            FROM nodes
            WHERE MATCH(name, summary) AGAINST (:term IN BOOLEAN MODE)
            ORDER BY score DESC
            LIMIT 50
        """)
        result = await self.session.execute(query, {"term": f"*{term}*"})
        return [dict(row) for row in result.mappings().all()]

    async def suggest_links(self, node_id: str) -> List[Dict]:
        """Sugere links baseados em tags em comum."""
        node = await self.get_node(node_id)
        if not node or not node.get('tags'):
            return []
        
        tags = node['tags']
        if isinstance(tags, str):
            tags = json.loads(tags)
            
        if not tags: return []

        # Query para encontrar nós que compartilham tags
        # MySQL JSON_OVERLAPS é ideal aqui
        query = text("""
            SELECT * FROM nodes 
            WHERE id != :id 
            AND JSON_OVERLAPS(tags, :tags)
            LIMIT 10
        """)
        
        result = await self.session.execute(query, {"id": node_id, "tags": json.dumps(tags)})
        return [dict(row) for row in result.mappings().all()]

