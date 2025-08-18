from sqlalchemy.ext.declarative import declarative_base

# Create a base class
Base = declarative_base()

from app.database import models as _models