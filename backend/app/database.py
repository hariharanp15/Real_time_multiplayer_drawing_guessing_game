from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def ensure_development_schema() -> None:
    """Apply small additive upgrades for the local SQLite quick-start database.

    Production MySQL deployments should instead use `alembic upgrade head`.
    `create_all()` creates missing tables but intentionally does not add columns
    to an existing SQLite table, which is why this explicit compatibility step
    is needed after introducing a room admin.
    """
    if not settings.database_url.startswith("sqlite"):
        return
    columns = {column["name"] for column in inspect(engine).get_columns("game_rooms")}
    if "admin_player_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE game_rooms ADD COLUMN admin_player_id INTEGER"))
    if "round_seconds" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE game_rooms ADD COLUMN round_seconds INTEGER NOT NULL DEFAULT 75"))
    # Rooms made before the admin feature keep their original first player as admin.
    with engine.begin() as connection:
        connection.execute(text("UPDATE game_rooms SET admin_player_id = (SELECT p.id FROM players p WHERE p.room_id = game_rooms.id ORDER BY p.joined_at LIMIT 1) WHERE admin_player_id IS NULL"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
