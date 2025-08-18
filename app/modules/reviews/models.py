import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class ReviewComment(Base):
    __tablename__ = "comments"
    __table_args__ = {"schema": "reviews"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.reviews.id", ondelete="CASCADE"), nullable=False)
    user_id   = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True)

    body = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="approved")  # approved, pending y aja

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    review = relationship("Review", back_populates="comments")
    user = relationship("User")

class ReviewImage(Base):
    __tablename__ = "review_images"
    __table_args__ = {"schema": "reviews"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.reviews.id", ondelete="CASCADE"), nullable=False)

    image_url = Column(String, nullable=False)
    alt_text  = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("Review", back_populates="images")

class ReviewVote(Base):
    __tablename__ = "review_votes"
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_vote_user"),
        {"schema": "reviews"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.reviews.id", ondelete="CASCADE"), nullable=False)
    user_id   = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)

    # Investigar mas a fondo
    helpful = Column(Boolean, nullable=False, default=True)  # o se podria usar +1/1 (Segun chatgpt)
    # Con helpful=True, mantener reviews.reviews.helpful_count sumando/restando en el servicio (o mediante trigger).

    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("Review", back_populates="votes")
    user = relationship("User")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        # Rating valido
        CheckConstraint("rating BETWEEN 1 AND 5", name="chk_review_rating_1_5"),
        # En tal caso que se usen variantes se exige el product XOR variant (una o la otra)
        CheckConstraint(
            "(product_id IS NOT NULL AND variant_id IS NULL) OR (product_id IS NULL AND variant_id IS NOT NULL)",
            name="chk_review_product_xor_variant"
        ),
        {"schema": "reviews"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id    = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="CASCADE"), nullable=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("catalog.product_variants.id", ondelete="CASCADE"), nullable=True)

    # Esto enlaza al item comprado para marcar “compra verificada”, (Funcionalidad opcional segun chatgpt)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("orders.order_items.id", ondelete="SET NULL"), nullable=True)
    
    rating = Column(Integer, nullable=False) # 1 - 5 Si son todos 1 somos basura
    title = Column(String, nullable=True)
    body = Column(Text, nullable=True)

    # Moderacion y/o visibilidad
    status = Column(String, nullable=False, default="pending")
    reported_count = Column(Integer, nullable=False, default=0)

    # Contador cacheado, investigar mas a fondo para mejor uso porq ni idea
    helpful_count = Column(Integer, nullable=False, default=0) 

    # VERIFICACIONES
    is_verified = Column(Boolean, nullable=False, default=False)
    veified_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # SI USO VARIANTES
    variant = relationship("ProductVariant")
    order_item = relationship("OrderItem")

    user = relationship("User")
    product = relationship("Product")

    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")
    comments = relationship("ReviewComment", back_populates="review", cascade="all, delete-orphan")
    votes = relationship("ReviewVote", back_populates="review", cascade="all, delete-orphan")