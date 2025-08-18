import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "subtotal >= 0 AND discount_total >= 0 AND shipping_total >= 0 AND tax_total >= 0 AND grand_total >= 0",
            name="chk_order_totals_nonneg"
        ),
        Index("idx_orders_user_placed", "user_id", "placed_at"),
        {"schema": "orders"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="SET NULL"))
    status_id = Column(UUID(as_uuid=True), ForeignKey("orders.order_status.id", ondelete="RESTRICT"), nullable=False)


    # Vinculo con el carrito de origen
    cart_id = Column(UUID(as_uuid=True), ForeignKey("orders.carts.id", ondelete="SET NULL"), nullable=True)

    # Id legible 
    order_number = Column(String, unique=True, nullable=True)

    # Totales (snapshots)
    subtotal = Column(Numeric(12, 2), nullable=False, default=0)
    discount_total = Column(Numeric(12, 2), nullable=False, default=0)
    shipping_total = Column(Numeric(12, 2), nullable=False, default=0)
    tax_total = Column(Numeric(12, 2), nullable=False, default=0)
    grand_total = Column(Numeric(14, 2), nullable=False, default=0)

    currency = Column(String(3), default="COP") 
    coupon_code = Column(String, nullable=True)

    placed_at = Column(DateTime, default=datetime.utcnow)   # fecha de creación/confirmación
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Datos de envío/billing "congelados" (snapshot) para mantener historial aunque cambien en la tabla de shipping.addresses
    shipping_full_name = Column(String, nullable=True)
    shipping_address = Column(String, nullable=True)
    shipping_city = Column(String, nullable=True)
    shipping_state = Column(String, nullable=True)
    shipping_country = Column(String, nullable=True)
    shipping_postal_code = Column(String, nullable=True)
    shipping_phone = Column(String, nullable=True)

    billing_full_name = Column(String, nullable=True)
    billing_address = Column(String, nullable=True)
    billing_city = Column(String, nullable=True)
    billing_state = Column(String, nullable=True)
    billing_country = Column(String, nullable=True)
    billing_postal_code = Column(String, nullable=True)
    billing_phone = Column(String, nullable=True)

    # relaciones con pagos
    payment_status = Column(String, default="pending")
    paid_at = Column(DateTime, nullable=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payments.payment_methods.id", ondelete="SET NULL"), nullable=True)
    payment_provider = Column(String, nullable=True)
    total_paid = Column(Numeric(14,2 ), nullable=False, default=0)
    payment_failure_reason = Column(String, nullable=True)

    # Estados, relaciones
    status = relationship("OrderStatus")
    cart = relationship("Cart")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    transactions = relationship("Transaction", primaryjoin="Order.id == foreign(Transaction.order_id)", viewonly=True)