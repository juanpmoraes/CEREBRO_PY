from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class NodeBase(BaseModel):
    name: str
    node_type: str
    mime_type: Optional[str] = None
    file_ext: Optional[str] = None
    raw_value: Optional[str] = None
    tags: List[str] = []
    extra_meta: Dict[str, Any] = {}

class NodeCreate(NodeBase):
    pass

class NodeResponse(NodeBase):
    id: str
    vault_path: Optional[str] = None
    content_hash: Optional[str] = None
    summary: Optional[str] = None
    thumbnail: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EdgeBase(BaseModel):
    source_id: str
    target_id: str
    relationship: str = "related_to"
    label: Optional[str] = None
    weight: float = 1.0

class EdgeCreate(EdgeBase):
    pass

class EdgeResponse(EdgeBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class GraphResponse(BaseModel):
    nodes: List[NodeResponse]
    links: List[EdgeResponse]
