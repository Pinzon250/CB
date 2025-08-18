import uuid
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class CouponProduct(Base):
    __tablename__ = "coupon_product"
    __table_args__ = (
        UniqueConstraint("coupon_id", "product_id", name="uq_coupon_product"),
        {"schema": "promotions"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("promotions.coupons.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="CASCADE"), nullable=False)

