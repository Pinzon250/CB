import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = {"schema": "shipping"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"))

    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable = False)
    postal_code = Column(String)
    phone = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="addresses")