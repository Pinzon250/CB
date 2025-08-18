import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        # CheckConstraint: Reglas logicas a nivel de fila
        # UniqueConstraint: Evitar duplicados Logicos
        UniqueConstraint("product_id", "sku", name="uq_variant_product_sku"),
        CheckConstraint("price_override IS NULL OR price_override >= 0", name="chk_variant_price_nonneg"),
        CheckConstraint("stock >= 0", name="chk_variant_stock_nonneg"),
        {"schema": "catalog"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="CASCADE"), nullable=False)

    sku = Column(String, nullable=False) # ej: CAM-TSH-BLK-M (Camiseta, talla M, Negra)
    price_override = Column(Numeric(10, 2), nullable=True) # Precio alternativo, si no se usa, se toma el del producto
    stock = Column(Integer, nullable=False, default=0) # Para inventario de las variantes

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product")
    options = relationship("VariantOption", back_populates="variant", cascade="all, delete-orphan")
