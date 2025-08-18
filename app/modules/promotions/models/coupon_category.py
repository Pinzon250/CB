import uuid
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class CouponCategory(Base):
    __tablename__ = "coupon_categories"
    __table_args__ = (
        UniqueConstraint("coupon_id", "category_id", name="uq_coupon_category"),
        {"schema": "promotions"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id =Column(UUID(as_uuid=True), ForeignKey("promotions.coupons.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("catalog.categories.id", ondelete="CASCADE"), nullable=False)