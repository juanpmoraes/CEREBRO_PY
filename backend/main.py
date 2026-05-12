from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Cérebro Digital API",
    description="Sistema de Banco de Dados de Grafo Agnóstico a Dados",
    version="1.0.0"
)



from .ws_manager import manager


# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


from .routers import nodes, edges, graph, search

app.include_router(nodes.router, prefix="/nodes", tags=["Nodes"])
app.include_router(edges.router, prefix="/edges", tags=["Edges"])
app.include_router(graph.router, prefix="/graph", tags=["Graph"])
app.include_router(search.router, prefix="/search", tags=["Search"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
