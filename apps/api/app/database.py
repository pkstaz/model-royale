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
    if "players" not in inspector.get_table_names():
        return
    columns = {item["name"] for item in inspector.get_columns("players")}
    if "password_hash" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE players ADD COLUMN password_hash VARCHAR(64) DEFAULT ''"))
