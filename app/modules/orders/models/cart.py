import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class Cart(Base):
    __tablename__ = "carts"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_cart_user"), 
        {"schema": "orders"}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")