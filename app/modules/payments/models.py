import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database.base import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    __table_args__ = (
        # Alias unico por usuario
        UniqueConstraint("user_id", "alias", name="uq_payment_method_alias_per_user"),
        {"schema": "payments"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)

    # Presentacion 
    alias = Column(String, nullable=True) # Como Visa personal, Nequi, Daviplata, etc.
    method_type = Column(String, nullable=False) # Metodo de pago: Tarjeta, billetera, etc.
    provider = Column(String, nullable=False) # Como Mercadopago, paypal, payu, wompi, etc

    # Datos seguros o tokenizados
    external_token = Column(String, nullable=False) # token/id en el PSP
    last4 = Column(String(4), nullable=True)
    brand = Column(String, nullable=True) # Marca de la tarjeta (Mastercard, Visa, etc)
    exp_month = Column(String, nullable=True)
    exp_year = Column(String, nullable=True)

    # Estado del metodo
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class Refund(Base):
    __tablename__ = "refunds"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_refund_amount_nonneg"),
        {"schema": "payments"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # A que transaccion pertenece el reembolso
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("payments.transactions.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="COP", nullable=False)

    status = Column(String, nullable=False, default="pending") # Estados: pending, sucess, failed, refunded etc

    provider = Column(String, nullable=False) # PSP
    provider_refund_id = Column(String, nullable=True)
    failure_code = Column(String, nullable=True)
    failure_message = Column(String, nullable=True)
    raw_response = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    transaction = relationship("Transaction")
    order = relationship("Order")

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_tx_amount_nonneg"),
        Index("idx_tx_order_created", "order_id", "created_at"),
        {"schema": "payments"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Vinculos principales
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE"), nullable=False)
    user_id =  Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payments.payment_methods.id", ondelete="SET NULL"), nullable=True)

    # Monto y moneda
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="COP", nullable=False)

    # Estado de pago
    # Se encuentran los siguientes estados: pending → authorized → captured; failed; y refunded del total o parcial
    status = Column(String, nullable=False, default="pending")

    #PSP, GATEWAY
    provider = Column(String, nullable=True) # MercadoPago, PayU, Wompi, etc.
    provider_transaction_id = Column(String, nullable=True) # id del PSP
    idempotency_key = Column(String, nullable=True, unique=True) # Evitamos dobles cargos

    # Diagnosticos
    failure_code = Column(String, nullable=True)
    failure_message = Column(String, nullable=True)
    raw_request = Column(JSONB, nullable=True)
    raw_response = Column(JSONB, nullable=True)

    # Tiempos
    authorized_at = Column(DateTime, nullable=True)
    captured_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order")
    user = relationship("User")
    payment_method = relationship("PaymentMethod")