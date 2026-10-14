from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine, ensure_development_schema
from .routes import rooms, history, websocket

Base.metadata.create_all(bind=engine)  # Alembic owns production migrations.
ensure_development_schema()
app = FastAPI(title="Sketch & Guess API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(rooms.router); app.include_router(history.router); app.include_router(websocket.router)

@app.get("/health")
def health(): return {"status": "ok"}
