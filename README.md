# 🧠 Cérebro Digital — Knowledge Graph Database

O **Cérebro Digital** é um sistema de gerenciamento de conhecimento agnóstico a dados, inspirado no conceito de "Second Brain". Ele transforma arquivos heterogêneos (PDFs, imagens, códigos, notas) em nós de um grafo interativo, permitindo visualizar conexões e metadados de forma intuitiva.

---

## 🚀 Funcionalidades

- **Grafo em Tempo Real:** Visualização dinâmica de nós e conexões usando `force-graph`.
- **Sistema de Drivers:** Processamento inteligente de diferentes tipos de arquivos:
  - **PDF:** Extração de texto para busca.
  - **Imagens:** Geração automática de thumbnails.
  - **Código:** Identificação de linguagens e metadados.
  - **Texto/Markdown:** Suporte nativo.
- **Busca Full-Text:** Pesquisa potente utilizando índices nativos do MySQL.
- **Sugestão de Links:** Algoritmo que sugere conexões baseadas em interseção de tags.
- **WebSocket:** Atualizações instantâneas na interface quando novos dados são inseridos.

---

## 🛠️ Tecnologias

- **Backend:** FastAPI (Python 3.10+)
- **Banco de Dados:** MySQL (SQLAlchemy Async + aiomysql)
- **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
- **Visualização:** Force-Graph.js
- **Processamento:** PyMuPDF, Pillow, Pygments, python-magic

---

## 📦 Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/cerebro-digital.git
cd cerebro-digital
```

### 2. Instalar dependências
```bash
python -m pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base):
```env
DATABASE_URL=mysql+aiomysql://usuario:senha@host:porta/nome_do_banco?ssl=true
VAULT_PATH=./backend/vault
THUMBNAIL_PATH=./backend/vault/thumbnails
```

### 4. Inicializar o Banco de Dados
```bash
python -m backend.init_db
```

---

## 🏃 Como Rodar

### Iniciar o Servidor
```bash
python -m uvicorn backend.main:app --reload
```
Acesse: **[http://localhost:8000](http://localhost:8000)**

### Importação em Lote (Scripts)
Para importar uma pasta inteira de arquivos de uma vez:
```bash
python -m backend.scripts.import_vault <caminho_da_pasta>
```

---

## 📁 Estrutura do Projeto

```text
cerebro-digital/
├── backend/
│   ├── database/       # Conexão e Sessão
│   ├── drivers/        # Lógica de extração de cada arquivo
│   ├── engines/        # Motores de Grafo e Armazenamento
│   ├── routers/        # Endpoints da API (Nodes, Edges, Search)
│   ├── vault/          # Armazenamento físico dos arquivos
│   └── main.py         # Entry point da aplicação
├── frontend/
│   ├── css/            # Estilos (Premium Dark Theme)
│   ├── js/             # Lógica do Grafo e API
│   └── index.html      # Interface principal
└── requirements.txt    # Dependências do sistema
```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---
*Desenvolvido com ❤️ para ser o seu segundo cérebro.*
