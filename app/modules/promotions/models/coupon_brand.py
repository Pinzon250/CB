import uuid
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class CouponBrand(Base):
    __tablename__ = "coupon_brands"
    __table_args__ = (
        UniqueConstraint("coupon_id", "brand_id", name="uq_coupon_brand"),
        {"schema": "promotions"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("promotions.coupons.id", ondelete="CASCADE"), nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("catalog.brands.id", ondelete="CASCADE"), nullable=False)
