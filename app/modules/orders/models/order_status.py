import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class OrderStatus(Base):
    __tablename__ = "order_status"
    __table_args__ = {"schema": "orders"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)   # Estado del pedido como pendiente, entragado y asi 
    name = Column(String, nullable=False)                
