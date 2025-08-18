import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class ProductSupplier(Base):
    __tablename__ = "product_suppliers"
    # CheckConstraint: Reglas logicas a nivel de fila
    # UniqueConstraint: Evitar duplicados Logicos
    __table_args__ = (
        # Garantiza usara product_id O variant_id
        # Esto implementa un XOR: o apuntas al producto o apuntas a la variante, pero no a ambos ni a ninguno.
        # Evitar estados ambiguos (doble enlace o sin enlace).
        CheckConstraint(
            "(product_id IS NOT NULL AND variant_id IS NULL) OR (product_id IS NULL AND variant_id IS NOT NULL)",
            name="chk_supplier_product_xor_variant"
        ),
        # Evitamos duplicados por parte de los proveedores
        # Un mismo proveedor no puede registrar dos veces el mismo producto (cuando es a nivel producto).
        UniqueConstraint("vendor_id", "product_id", name="uq_vendor_product"),
        # Un mismo proveedor no puede registrar dos veces la misma variante (cuando es a nivel variante).
        UniqueConstraint("vendor_id", "variant_id", name="uq_vendor_variant"),
        {"schema": "catalog"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    vendor_id = Column(UUID(as_uuid=True), ForeignKey("catalog.vendors.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="CASCADE"),nullable=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("catalog.product_variants.id", ondelete="CASCADE"),nullable=True)

    # STOCK KEEPING UNIT: Identificador unico interno que usa el sistema para un item
    supplier_sku = Column(String, nullable=False)              # SKU en el sistema del proveedor
    cost = Column(Numeric(12, 2), nullable=False, default=0)   # Costo del proveedor
    msrp = Column(Numeric(12, 2), nullable=True)               # Costo sugerido por el proveedor
    min_order_qty = Column(Integer, nullable=True, default=1)  # Minimo de unidades por orden al proveedor
    lead_time_days = Column(Integer, nullable=True)            # Tiempo de despacho estimado
    product_url = Column(String, nullable=True)                # Enlace a la lista del producto por parte de el proveedor

    availability = Column(String, nullable=True)               # En stock, no tiene stock, etc
    last_synced_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)