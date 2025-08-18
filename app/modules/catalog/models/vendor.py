import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class Vendor(Base):
    __tablename__ = "vendors"
    __table_args__ = {"schema": "catalog"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False) # Nombre del proveedor minusculas (CODIGO)
    name = Column(String, nullable=False) # Nombre normal
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)

    api_base_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    webhook_secret = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    