import os
import pymysql
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def init_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Erro: DATABASE_URL não encontrada no .env")
        return

    # Extrair componentes da URL (espera formato mysql+aiomysql://user:pass@host:port/db)
    # Para o pymysql, precisamos limpar a URL
    url = database_url.replace("mysql+aiomysql://", "mysql://")
    parsed = urlparse(url)
    
    db_config = {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip('/').split('?')[0], # Limpar query params do nome do banco
        "charset": 'utf8mb4',
        "cursorclass": pymysql.cursors.DictCursor
    }

    # Ativar SSL se especificado na URL
    if "ssl=true" in database_url.lower():
        db_config["ssl"] = {"fake_flag_to_enable_ssl": True} # SSL genérico para pymysql

    print(f"Conectando ao banco de dados em {db_config['host']} (SSL: {'Sim' if 'ssl' in db_config else 'Não'})...")

    connection = pymysql.connect(**db_config)


    try:
        with connection.cursor() as cursor:
            # Tabela NODES
            print("Criando tabela 'nodes'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id           CHAR(36)     NOT NULL PRIMARY KEY,
                    name         VARCHAR(512) NOT NULL,
                    node_type    VARCHAR(64)  NOT NULL,
                    mime_type    VARCHAR(128),
                    file_ext     VARCHAR(32),
                    vault_path   VARCHAR(1024),
                    raw_value    TEXT,
                    content_hash CHAR(64),
                    summary      MEDIUMTEXT,
                    thumbnail    VARCHAR(1024),
                    size_bytes   BIGINT,
                    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
                    updated_at   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    tags         JSON,
                    extra_meta   JSON,
                    INDEX idx_node_type  (node_type),
                    INDEX idx_file_ext   (file_ext),
                    INDEX idx_content_hash (content_hash),
                    FULLTEXT INDEX ft_search (name, summary)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            # Tabela EDGES
            print("Criando tabela 'edges'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id           CHAR(36)     NOT NULL PRIMARY KEY,
                    source_id    CHAR(36)     NOT NULL,
                    target_id    CHAR(36)     NOT NULL,
                    relationship VARCHAR(128) NOT NULL,
                    label        VARCHAR(512),
                    weight       FLOAT        DEFAULT 1.0,
                    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
                    FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE,
                    UNIQUE KEY uq_edge (source_id, target_id, relationship),
                    INDEX idx_source (source_id),
                    INDEX idx_target (target_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

            """)
        
        connection.commit()
        print("Banco de dados inicializado com sucesso!")

    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    init_db()
