import os
import asyncio
import httpx
from pathlib import Path
import json

API_URL = "http://localhost:8000/nodes/"

async def import_folder(folder_path: str):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Erro: Pasta {folder_path} não existe.")
        return

    async with httpx.AsyncClient() as client:
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                print(f"Importando: {file_path.name}...")
                try:
                    with open(file_path, 'rb') as f:
                        files = {'file': (file_path.name, f)}
                        data = {
                            'name': file_path.name,
                            'node_type': 'file',
                            'tags': json.dumps(['importado', folder.name])
                        }
                        response = await client.post(API_URL, data=data, files=files)
                        if response.status_code == 200:
                            print(f"Sucesso: {file_path.name}")
                        else:
                            print(f"Erro ao importar {file_path.name}: {response.text}")
                except Exception as e:
                    print(f"Falha crítica em {file_path.name}: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python import_vault.py <caminho_da_pasta>")
    else:
        asyncio.run(import_folder(sys.argv[1]))
