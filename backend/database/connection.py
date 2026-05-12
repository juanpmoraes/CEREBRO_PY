from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada no arquivo .env")

# Configuração otimizada para SquareCloud/MySQL
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,           # conexões permanentes no pool
    max_overflow=10,       # conexões extras sob carga
    pool_timeout=30,       # segundos antes de dar timeout
    pool_recycle=1800,     # reconecta a cada 30min (evita "gone away" do MySQL)
    echo=False,
    connect_args={"ssl": True} # Força SSL como Booleano para evitar erro de string
)


AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
