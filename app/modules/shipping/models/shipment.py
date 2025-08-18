import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class Shipment(Base):
    __tablename__ = "shipments"
    __table_args__ = (
        CheckConstraint("cost >= 0", name="chk_shipment_cost_nonneg"),
        Index("idx_shipment_order_created", "order_id", "created_at"),
        {"schema": "shipping"}
    )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # A que pedido pertenece el envio
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE"), nullable=False)

    # Transportadora y metodo
    carrier_id = Column(UUID(as_uuid=True), ForeignKey("shipping.carriers.id", ondelete="SET NULL"), nullable=True)
    carrier_code = Column(String, nullable=True) # snapshot
    service_code = Column(String, nullable=True) # Ej: Express

    # Tracking o seguimiento
    tracking_number = Column(String, nullable=True, unique=True)
    status = Column(String, nullable=False, default="pending") # Estados: pending, ready, shipped, in_transit, delivered, returned, o cancelled

    # Costos de envio facturado en la orden
    cost = Column(Numeric(14, 2), nullable=False, default=0)

    # Tiempos
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Destino
    to_address_id = Column(UUID(as_uuid=True), ForeignKey("shipping.addresses.id", ondelete="SET NULL"), nullable=True)

    order = relationship("Order")
    carrier = relationship("Carrier")
    to_address = relationship("Address")
    items = relationship("ShipmentItem", back_populates="shipment", cascade="all, delete-orphan")
    tracking_events = relationship("TrackingEvent", back_populates="shipment", cascade="all, delete-orphan")

