# models/promotions/coupon_redemption.py
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class CouponRedemption(Base):
    __tablename__ = "coupon_redemptions"
    __table_args__ = (
        UniqueConstraint("coupon_id", "order_id", name="uq_coupon_order_once"),
        {"schema": "promotions"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    coupon_id = Column(UUID(as_uuid=True), ForeignKey("promotions.coupons.id", ondelete="CASCADE"), nullable=False)
    order_id  = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE"), nullable=False)
    user_id   = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True)

    amount_applied = Column(Numeric(12,2), nullable=False, default=0)  # La cantidad que se desconto
    created_at = Column(DateTime, default=datetime.utcnow)
