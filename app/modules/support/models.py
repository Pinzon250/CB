import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class SupportMessage(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "support"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support.tickets.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True)

    message = Column(Text, nullable=False)
    is_staff = Column(Boolean, default=False)  # Verdadero si el mensaje lo envia el soporte o el perro admin

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    ticket = relationship("SupportTicket", back_populates="messages")
    sender = relationship("User")

class SupportTicket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "support"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="SET NULL"), nullable=True)

    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="open")  # open, pending, resolved, closed
    priority = Column(String, nullable=True)  # low, medium, high, urgent

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Relaciones
    user = relationship("User")
    order = relationship("Order")
    messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan")