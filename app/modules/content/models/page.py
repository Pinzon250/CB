import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class Page(Base):
    __tablename__ = "pages"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_page_slug"),
        {"schema": "content"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String, nullable=False)
    slug = Column(String, nullable=False) # como por ejemplo: "about-us", "terms"
    excerpt = Column(String, nullable=True) # resumen corto
    body = Column(Text, nullable=True) # si no usas blocks

    # SEO
    seo_title = Column(String, nullable=True)
    seo_description = Column(String, nullable=True)

    # Publicaciones
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)