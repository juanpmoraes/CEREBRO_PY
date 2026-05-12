from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json
from ..database.connection import get_db
from ..engines.graph_engine import GraphEngine
from ..engines.storage_engine import StorageEngine
from ..drivers.registry import get_driver
from ..models.schemas import NodeResponse

router = APIRouter()

@router.post("/", response_model=dict)
async def create_node(
    name: str = Form(...),
    node_type: str = Form(...),
    file: Optional[UploadFile] = File(None),
    raw_value: Optional[str] = Form(None),
    tags: str = Form("[]"),
    db: AsyncSession = Depends(get_db)
):
    engine = GraphEngine(db)
    node_data = {
        "name": name,
        "node_type": node_type,
        "raw_value": raw_value,
        "tags": json.loads(tags)
    }

    if file:
        content = await file.read()
        filename = file.filename
        ext = filename.split('.')[-1] if '.' in filename else ""
        
        # Armazenamento físico
        vault_path = await StorageEngine.save_file(content, filename)
        
        # Metadados e Driver
        driver = get_driver(file.content_type, ext)
        summary = driver.extract_summary(str(StorageEngine.VAULT_PATH / filename), content)
        meta = driver.extract_metadata(str(StorageEngine.VAULT_PATH / filename), content)
        
        # Gerar thumbnail se possível
        thumbnail_path = None
        if hasattr(driver, 'generate_thumbnail'):
            # Nome da thumbnail: hash.png
            content_hash = StorageEngine.calculate_hash(content)
            thumb_filename = f"{content_hash}.png"
            thumb_out_path = StorageEngine.THUMBNAIL_PATH / thumb_filename
            
            full_vault_path = StorageEngine.VAULT_PATH / filename
            if driver.generate_thumbnail(str(full_vault_path), str(thumb_out_path)):
                thumbnail_path = str(thumb_out_path.relative_to(StorageEngine.VAULT_PATH.parent.parent))

        node_data.update({
            "mime_type": file.content_type,
            "file_ext": ext,
            "vault_path": vault_path,
            "thumbnail": thumbnail_path,
            "content_hash": StorageEngine.calculate_hash(content),
            "summary": summary,
            "size_bytes": StorageEngine.get_file_size(content),
            "extra_meta": json.dumps(meta)
        })


    node_id = await engine.create_node(node_data)
    
    # Notificar via WebSocket
    from ..ws_manager import manager
    await manager.broadcast({"type": "node_created", "node_id": node_id, "name": name})
    
    return {"id": node_id, "message": "Node criado com sucesso"}



@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str, db: AsyncSession = Depends(get_db)):
    engine = GraphEngine(db)
    node = await engine.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node não encontrado")
    
    # Converter JSON do MySQL para dict/list
    if node.get("tags") and isinstance(node["tags"], str):
        node["tags"] = json.loads(node["tags"])
    if node.get("extra_meta") and isinstance(node["extra_meta"], str):
        node["extra_meta"] = json.loads(node["extra_meta"])
        
    return node

@router.get("/", response_model=List[NodeResponse])
async def list_nodes(limit: int = 100, db: AsyncSession = Depends(get_db)):
    engine = GraphEngine(db)
    nodes = await engine.list_nodes(limit)
    for node in nodes:
        if node.get("tags") and isinstance(node["tags"], str):
            node["tags"] = json.loads(node["tags"])
    return nodes

@router.get("/{node_id}/suggestions", response_model=List[NodeResponse])
async def suggest_links(node_id: str, db: AsyncSession = Depends(get_db)):
    engine = GraphEngine(db)
    return await engine.suggest_links(node_id)


