# Cérebro Digital — Plano de Implementação Real
 
> Versão crítica e expandida. Agnóstico a dados. Construído para durar.
 
---
 
## 0. Princípios Arquiteturais (não pule isso)
 
Antes de escrever uma linha de código, internaliza esses três pilares:
 
1. **Dado é Dado.** Um `.exe`, um `int`, um `PDF` e uma `foto` são todos nós com schema diferente — não casos especiais.
2. **Arquivo ≠ Banco.** O SQLite guarda *metadados e relações*. O arquivo físico fica no `vault/` no disco. Nunca coloque binário bruto no SQLite.
3. **Extensibilidade > Perfeição.** Cada tipo de dado tem seu próprio "Driver". Adicionar suporte a um novo tipo = adicionar um novo driver, sem tocar no core.
---
 
## 1. Arquitetura Geral
 
```
                        ┌─────────────────────┐
                        │     FRONTEND        │
                        │  (HTML + Force-Graph│
                        │   ou Python Dash)   │
                        └────────┬────────────┘
                                 │ HTTP / WebSocket
                        ┌────────▼────────────┐
                        │      FastAPI         │
                        │  (API REST + WS)    │
                        └──┬──────────┬───────┘
                           │          │
               ┌───────────▼──┐  ┌────▼──────────────┐
               │  Graph Engine│  │  Storage Engine    │
               │  (SQLite +   │  │  (vault/ no disco) │
               │   NetworkX)  │  │                    │
               └──────────────┘  └────────────────────┘
                           │
               ┌───────────▼──────────┐
               │   Driver System      │
               │  pdf | img | code |  │
               │  xlsx | zip | ...    │
               └──────────────────────┘
```
 
---
 
## 2. Schema do Banco de Dados (MySQL — SquareCloud)
 
> **⚠️ Segurança obrigatória:** a string de conexão vai **exclusivamente** no `.env`. Nunca em código, nunca em commit, nunca em chat.
 
### Conexão via SQLAlchemy Async
 
```python
# backend/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
 
# O driver aiomysql exige que a URL use "mysql+aiomysql://"
DATABASE_URL = os.getenv("DATABASE_URL")
# Exemplo no .env:
# DATABASE_URL=mysql+aiomysql://squarecloud:SUASENHA@square-cloud-db-xxxx.squareweb.app:7209/cerebro
 
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,           # conexões permanentes no pool
    max_overflow=10,       # conexões extras sob carga
    pool_timeout=30,       # segundos antes de dar timeout
    pool_recycle=1800,     # reconecta a cada 30min (evita "gone away" do MySQL)
    echo=False,
)
 
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```
 
> **Por que pool_recycle?** O MySQL da SquareCloud vai fechar conexões ociosas após certo tempo. Sem `pool_recycle`, você vai ter erros `2006: MySQL server has gone away` de forma aleatória.
 
---
 
### Tabela `nodes`
```sql
CREATE TABLE nodes (
    id           CHAR(36)     NOT NULL PRIMARY KEY,       -- UUID v4
    name         VARCHAR(512) NOT NULL,
    node_type    VARCHAR(64)  NOT NULL,                   -- 'file', 'concept', 'value', 'code_snippet'
    mime_type    VARCHAR(128),                            -- 'application/pdf', 'image/png'
    file_ext     VARCHAR(32),                             -- '.pdf', '.py'
    vault_path   VARCHAR(1024),                           -- path relativo em vault/ (NULL se não-arquivo)
    raw_value    TEXT,                                    -- para tipos simples: int, float, string, date
    content_hash CHAR(64),                               -- SHA-256 (deduplicação)
    summary      MEDIUMTEXT,                             -- texto extraído para busca full-text
    thumbnail    VARCHAR(1024),                          -- path do preview
    size_bytes   BIGINT,
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     DEFAULT CURRENT_TIMESTAMP
                              ON UPDATE CURRENT_TIMESTAMP,
    tags         JSON,                                   -- array nativo: ["python", "financeiro"]
    extra_meta   JSON,                                   -- metadados livres por driver
 
    INDEX idx_node_type  (node_type),
    INDEX idx_file_ext   (file_ext),
    INDEX idx_content_hash (content_hash),
    FULLTEXT INDEX ft_search (name, summary)             -- busca full-text (substitui FTS5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
 
### Tabela `edges`
```sql
CREATE TABLE edges (
    id           CHAR(36)     NOT NULL PRIMARY KEY,
    source_id    CHAR(36)     NOT NULL,
    target_id    CHAR(36)     NOT NULL,
    relationship VARCHAR(128) NOT NULL,   -- 'references', 'depends_on', 'related_to', 'custom'
    label        VARCHAR(512),
    weight       FLOAT        DEFAULT 1.0,
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
 
    FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE,
    UNIQUE KEY uq_edge (source_id, target_id, relationship),
    INDEX idx_source (source_id),
    INDEX idx_target (target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
 
### Diferenças críticas SQLite → MySQL
 
| Ponto | SQLite (antes) | MySQL (agora) |
|---|---|---|
| UUID | `TEXT` | `CHAR(36)` — tamanho fixo, mais eficiente |
| JSON | `TEXT` (manual) | `JSON` nativo — validado pelo banco |
| Full-text | `FTS5 VIRTUAL TABLE` | `FULLTEXT INDEX` com `MATCH...AGAINST` |
| Auto-update timestamp | manual | `ON UPDATE CURRENT_TIMESTAMP` |
| Charset | N/A | `utf8mb4` — suporta emoji e caracteres asiáticos |
| Conexão | arquivo local | pool TCP com `pool_recycle` obrigatório |
 
### Busca Full-Text no MySQL (substitui FTS5)
 
```python
# Busca usando FULLTEXT INDEX — sintaxe diferente do FTS5
query = """
    SELECT *, MATCH(name, summary) AGAINST (:termo IN BOOLEAN MODE) AS score
    FROM nodes
    WHERE MATCH(name, summary) AGAINST (:termo IN BOOLEAN MODE)
    ORDER BY score DESC
    LIMIT 50
"""
```
 
### Por que essa separação importa
- `vault_path` + `raw_value` separam arquivos físicos de valores puros (um nó pode ser o número `42` sem arquivo)
- `content_hash` permite deduplicação automática — mesmo arquivo enviado duas vezes = mesmo nó
- `JSON` nativo do MySQL valida estrutura e permite queries como `JSON_CONTAINS(tags, '"python"')`
- `pool_recycle=1800` é não-negociável em DB remota — sem isso você vai debugar erros de conexão sem fim
---
 
## 3. Sistema de Drivers (Coração da Extensibilidade)
 
Cada driver é responsável por um grupo de tipos. Interface obrigatória:
 
```python
# backend/drivers/base_driver.py
from abc import ABC, abstractmethod
 
class BaseDriver(ABC):
    SUPPORTED_EXTENSIONS: list[str] = []
    SUPPORTED_MIMES: list[str] = []
 
    @abstractmethod
    def extract_summary(self, file_path: str) -> str:
        """Texto para busca FTS."""
        ...
 
    @abstractmethod
    def extract_metadata(self, file_path: str) -> dict:
        """Metadados específicos do tipo (vai para extra_meta)."""
        ...
 
    def generate_thumbnail(self, file_path: str, out_path: str) -> bool:
        """Opcional. Retorna True se gerou thumbnail."""
        return False
```
 
### Drivers a implementar (por prioridade)
 
| Prioridade | Driver | Tipos | Bibliotecas |
|---|---|---|---|
| 1 | `text_driver` | `.txt`, `.md`, `.csv`, `.json`, `.yaml`, `.xml` | built-in |
| 2 | `code_driver` | `.py`, `.js`, `.ts`, `.rs`, `.go`, etc. | `pygments` |
| 3 | `pdf_driver` | `.pdf` | `PyMuPDF (fitz)` |
| 4 | `image_driver` | `.jpg`, `.png`, `.gif`, `.webp`, `.svg` | `Pillow` |
| 5 | `office_driver` | `.xlsx`, `.xls`, `.docx`, `.pptx` | `openpyxl`, `python-docx` |
| 6 | `archive_driver` | `.zip`, `.tar`, `.gz`, `.7z` | `zipfile`, `tarfile` |
| 7 | `binary_driver` | `.exe`, `.dll`, `.bin` | `python-magic`, `hashlib` |
| 8 | `value_driver` | int, float, string, date, bool | built-in (sem arquivo) |
| 9 | `video_driver` | `.mp4`, `.mkv`, `.mov` | `ffmpeg-python` |
 
**Registro de drivers:**
```python
# backend/drivers/registry.py
DRIVER_REGISTRY: dict[str, BaseDriver] = {}
 
def get_driver(mime_type: str, file_ext: str) -> BaseDriver:
    # Tenta MIME primeiro, depois extensão, fallback para BinaryDriver
    ...
```
 
---
 
## 4. Fases de Desenvolvimento
 
### FASE 0 — Ambiente (1-2 dias)
- [ ] Criar estrutura de pastas (ver seção 5)
- [ ] `requirements.txt` com dependências core
- [ ] `.env` com `DATABASE_URL` (nunca commitar — adicionar ao `.gitignore`)
- [ ] `.env.example` com placeholder sem credenciais reais
- [ ] `config.yaml` para paths do vault local
- [ ] Script `init_db.py` que conecta no MySQL remoto e executa o DDL das tabelas
- [ ] Testar conexão antes de subir qualquer coisa (`SELECT 1`)
### FASE 1 — Core Backend (1 semana)
- [ ] `StorageEngine`: salvar arquivo em `vault/` local, calcular hash, detectar MIME com `python-magic`
- [ ] `GraphEngine`: wrapper sobre MySQL (SQLAlchemy async + aiomysql) para CRUD de nós e arestas
- [ ] Driver `text_driver` e `value_driver` (mais simples, validam a arquitetura)
- [ ] API FastAPI com endpoints:
  - `POST /nodes` — criar nó (arquivo upload ou valor puro)
  - `GET /nodes/{id}` — ler nó
  - `DELETE /nodes/{id}` — deletar nó + arquivo físico
  - `POST /edges` — criar aresta
  - `GET /graph` — retorna JSON `{nodes: [], links: []}` para o frontend
**Critério de conclusão:** conseguir criar dois nós de texto, linká-los e ver o JSON do grafo.
 
### FASE 2 — Drivers (2 semanas)
- [ ] Implementar drivers por prioridade da tabela acima
- [ ] Cada driver tem seu próprio teste unitário
- [ ] Thumbnail generator para imagens e PDFs
**Critério de conclusão:** upload de um PDF extrai texto para busca; upload de imagem gera thumbnail.
 
### FASE 3 — Frontend do Grafo (1 semana)
- [ ] `index.html` com `force-graph` (https://github.com/vasturiano/force-graph)
- [ ] Consumir `GET /graph` e renderizar nós/arestas
- [ ] Cores/ícones por tipo de nó (`node_type`)
- [ ] Clique num nó abre painel lateral com metadados
- [ ] Drag para criar arestas entre nós
- [ ] Upload de arquivo diretamente no frontend
**Decisão:** usar `force-graph` em 2D primeiro. 3D é bonito mas tem custo de performance e UX ruim em telas pequenas. Adicione 3D depois se fizer sentido.
 
### FASE 4 — Busca (3-4 dias)
- [ ] Endpoint `GET /search?q=termo` usando MySQL `FULLTEXT` com `MATCH...AGAINST`
- [ ] Frontend com campo de busca que filtra o grafo em tempo real
- [ ] Filtros por `node_type`, `file_ext`, data de criação
- [ ] Suporte a busca booleana (`+obrigatório -excluído palavra*`)
### FASE 5 — Polish (contínuo)
- [ ] WebSocket para atualização em tempo real do grafo quando nó é adicionado
- [ ] Importação em lote (pasta inteira vira nós)
- [ ] Export do grafo como JSON, GraphML
- [ ] Sugestão de links (baseado em tags comuns — **não chame de "IA"**, é só interseção de sets)
---
 
## 5. Estrutura de Arquivos
 
```
cerebro-digital/
├── backend/
│   ├── main.py                  # Entry point FastAPI
│   ├── config.py                # Configurações (paths, limites)
│   ├── init_db.py               # Conecta no MySQL e cria tabelas
│   ├── database/
│   │   └── connection.py        # Engine SQLAlchemy + pool MySQL
│   ├── engines/
│   │   ├── storage_engine.py    # Gerencia vault/ e hashes
│   │   └── graph_engine.py      # CRUD de nós e arestas (MySQL)
│   ├── drivers/
│   │   ├── base_driver.py
│   │   ├── registry.py
│   │   ├── text_driver.py
│   │   ├── code_driver.py
│   │   ├── pdf_driver.py
│   │   ├── image_driver.py
│   │   ├── office_driver.py
│   │   ├── archive_driver.py
│   │   ├── binary_driver.py
│   │   └── value_driver.py
│   ├── routers/
│   │   ├── nodes.py
│   │   ├── edges.py
│   │   ├── graph.py
│   │   └── search.py
│   ├── models/
│   │   └── schemas.py
│   └── vault/                   # Arquivos físicos (gitignore)
│       └── thumbnails/
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── main.css
│   └── js/
│       ├── graph.js
│       ├── api.js
│       └── ui.js
├── tests/
│   ├── test_drivers.py
│   └── test_api.py
├── .env                         # ← CREDENCIAIS REAIS (no .gitignore)
├── .env.example                 # ← Placeholder público (commitável)
├── .gitignore                   # vault/, .env, __pycache__, *.pyc
├── requirements.txt
└── config.yaml
```
 
---
 
## 6. Dependências Core
 
```txt
# requirements.txt
fastapi>=0.110
uvicorn[standard]>=0.29
python-multipart          # upload de arquivos
aiofiles                  # I/O assíncrono de arquivos
pydantic>=2.0
python-dotenv
 
# Banco de dados — MySQL remoto
sqlalchemy>=2.0           # ORM async
aiomysql                  # driver async para MySQL
PyMySQL                   # driver síncrono (para init_db.py)
 
# Processamento de arquivos
python-magic              # detecção de MIME por magic bytes
Pillow                    # imagens e thumbnails
PyMuPDF                   # PDF — melhor que PyPDF2
python-docx               # .docx
openpyxl                  # .xlsx/.xls
pygments                  # syntax highlight de código
 
# Dev e testes
httpx
pytest
pytest-asyncio
```
 
### `.env.example` (commitar isso, nunca o `.env` real)
```
DATABASE_URL=mysql+aiomysql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
VAULT_PATH=./backend/vault
THUMBNAIL_PATH=./backend/vault/thumbnails
MAX_UPLOAD_MB=500
```
 
---
 
## 7. Decisões Técnicas e Trade-offs
 
| Decisão | Escolha | Por quê | Quando reconsiderar |
|---|---|---|---|
| Banco de dados | SQLite | Portátil, zero setup, suficiente para 1M+ nós | Se precisar de múltiplos usuários simultâneos → PostgreSQL |
| Grafo em memória | NetworkX (Python) | Para análises (caminho mais curto, clustering) | Se o grafo tiver 100k+ nós → graph DB dedicado (Neo4j/Memgraph) |
| Frontend | HTML puro | Sem build step, sem complexidade | Se quiser estado reativo complexo → adicione Alpine.js ou Svelte |
| Armazenamento de arquivos | Disco local (vault/) | Simples, rápido | Se quiser acesso remoto → S3/MinIO |
| Binários no banco | NÃO (só path) | SQLite não é feito pra blobs grandes | Nunca mude isso |
 
---
 
## 8. O que NÃO fazer (armadilhas comuns)
 
1. **Não tente suportar tudo de uma vez.** Comece com `text`, `value` e `pdf`. O sistema de drivers foi desenhado para crescer.
2. **Não armazene arquivos binários no SQLite.** Guarde o path. Sempre.
3. **Não chame de "Auto-Link com IA"** o que é na verdade "nós que compartilham as mesmas tags". Seja honesto sobre o que está implementando.
4. **Não construa o frontend antes do backend estar estável.** O contrato da API (`GET /graph`) precisa estar sólido primeiro.
5. **Não ignore o `content_hash`.** Ele previne duplicatas e vai te salvar mais cedo do que você pensa.
---
 
## 9. Primeiro Código a Escrever (Fase 0 + início da Fase 1)
 
Ordem exata:
1. `init_db.py` — schema do banco
2. `engines/storage_engine.py` — salvar arquivo, calcular hash
3. `drivers/value_driver.py` — o mais simples possível
4. `routers/nodes.py` + `main.py` — POST e GET funcionando
5. `GET /graph` retornando JSON válido para o force-graph
6. `index.html` mínimo consumindo `/graph` e mostrando dois nós na tela
Quando você ver dois nós aparecerem no grafo, a fundação está de pé. Tudo a partir daí é driver e UX.