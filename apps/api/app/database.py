from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_schema() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "app_settings" in tables:
        setting_cols = {item["name"] for item in inspector.get_columns("app_settings")}
        if "seed_lang" not in setting_cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE app_settings ADD COLUMN seed_lang VARCHAR(8) DEFAULT ''"))
    if "avatars" in tables:
        avatar_cols = {item["name"] for item in inspector.get_columns("avatars")}
        with engine.begin() as conn:
            if "use_global_endpoint" not in avatar_cols:
                conn.execute(text("ALTER TABLE avatars ADD COLUMN use_global_endpoint BOOLEAN DEFAULT 1"))
            if "use_global_api_key" not in avatar_cols:
                conn.execute(text("ALTER TABLE avatars ADD COLUMN use_global_api_key BOOLEAN DEFAULT 1"))
    if "players" not in tables:
        return
    columns = {item["name"] for item in inspector.get_columns("players")}
    with engine.begin() as conn:
        if "password_hash" not in columns:
            conn.execute(text("ALTER TABLE players ADD COLUMN password_hash VARCHAR(64) DEFAULT ''"))
        if "temperature" not in columns:
            conn.execute(text("ALTER TABLE players ADD COLUMN temperature FLOAT DEFAULT 0.4"))
