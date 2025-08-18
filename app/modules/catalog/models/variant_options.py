import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class VariantOptions(Base):
    __tablename__ = "variant_options"
    __table_args__ = (
        UniqueConstraint("variant_id", "attribute_id", name="uq_variant_attr"),
        {"schema": "catalog"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("catalog.product_variants.id", ondelete="CASCADE"), nullable=False)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("catalog.attributes.id", ondelete="RESTRICT"), nullable=False)

    value = Column(String, nullable=False) # Valor elegido para ese atributo en esa variante, Ej: "M", "Negro", etc

    variant = relationship("ProductVariant", back_populates="options")
    attribute = relationship("Attribute")