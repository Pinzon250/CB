from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import *
from .base import *

from app.core.config import settings

# Create an engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True
)


# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()