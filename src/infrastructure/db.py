import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "mercado_nfe")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return url


engine = create_engine(
    _get_database_url(),
    echo=False,
    connect_args={"options": "-c client_encoding=utf8"},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Session:
    return SessionLocal()


def create_tables() -> None:
    from src.infrastructure.persistence.sqlalchemy.models.models import Base

    Base.metadata.create_all(bind=engine)
