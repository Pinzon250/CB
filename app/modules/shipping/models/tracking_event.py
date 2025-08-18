import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database.base import Base

class TrackingEvent(Base):
    __tablename__ = "tracking_events"
    __table_args__ = {"schema": "shipping"},

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipping.shipments.id", ondelete="CASCADE"), nullable=False)

    status_code = Column(String, nullable=True) # "PENDING", "DELIVERED" etc
    description = Column(String, nullable=True) # Se entrego en buen estado, esta en camino, etc
    location = Column(String, nullable=True)
    event_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    raw = Column(JSONB, nullable=True)

    shipment = relationship("Shipment", back_populates="tracking_events")

