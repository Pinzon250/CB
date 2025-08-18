import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database.base import Base

class Coupon(Base):
    __tablename__ = "coupons"
    __table_args__ = (
        CheckConstraint(
            "(discount_type IN ('percent','fixed','free_shipping'))",
            name="chk_coupon_discount_type"
        ),
        CheckConstraint(
            "(discount_type <> 'percent') OR (percentage BETWEEN 0 AND 100)",
            name="chk_coupon_percentage_range"
        ),
        CheckConstraint(
            "(discount_type <> 'fixed') OR (amount >= 0)",
            name="chk_coupon_amount_nonneg"
        ),
        {"schema": "promotions"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    code = Column(String, unique=True, nullable=False) # 'CUPON2025'
    name = Column(String, nullable=True) # Nombre legible
    description = Column(String, nullable=True)

    discount_type = Column(String, nullable=False, default="percent")
    percentage = Column(Numeric(5,2), nullable=True)
    amount = Column(Numeric(12,2), nullable=True)
    max_discount = Column(Numeric(12,2), nullable=True)

    min_subtotal = Column(Numeric(12, 2), nullable=True) # Lo que debe tener el carrito minimo para aplicar el cupon
    currency = Column(String(3),nullable=True, default="COP")

    start_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
    is_stackable = Column(Boolean, default=False) # Puede combinar con otros cupones

    max_redemptions_total = Column(Integer, nullable=True)
    max_redemptions_per_user = Column(Integer, nullable=True)

    extras = Column(JSONB, nullable=True) # Extras
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)