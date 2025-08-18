import uuid 

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class Wishlist(Base):
    __tablename__ = "wishlists"
    __table_args__ = {
        "schema": "catalog",
        "comment":"User ←→ Product favorites",
        "postgresql_partition_by": None
        }
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Avoid Duplicates
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
        {"schema": "catalog"}
    )

    user = relationship("User", back_populates="wishlist")
    product = relationship("Product")
