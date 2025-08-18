from sqlalchemy import create_engine
from .models import *
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from .base import *

# Load environment variables
load_dotenv()

# Import DB URL
SQLALCHEMY_DATABASE = os.getenv("SQLALCHEMY_DATABASE")

# Create an engine
engine = create_engine(SQLALCHEMY_DATABASE)


# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()