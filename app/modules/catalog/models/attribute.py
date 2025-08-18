import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class Attribute(Base):
    __tablename__ = "attributes"
    __table_args__ = {"schema": "catalog"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    product_attributes = relationship("ProductAttribute", back_populates="attribute", cascade="all, delete-orphan")