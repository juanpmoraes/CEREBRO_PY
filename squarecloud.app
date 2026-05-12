MAIN=backend/main.py
MEMORY=512
VERSION=recommended
DISPLAY_NAME=Cérebro Digital
DESCRIPTION=Knowledge Graph Database & Second Brain
AUTORESTART=true
START=python -m uvicorn backend.main:app --host 0.0.0.0 --port 80
