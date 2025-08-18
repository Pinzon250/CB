# Para paginas modulares
# Este coso es opcional, si algo investigar mas a fondo para mejor uso
# Para construirp paginas con ssecciones, html seguro, json y toda la vuelta
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.base import Base

class PageBlock(Base):
    __tablename__ = "page_blocks"
    __table_args__ = {"schema": "content"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("content.pages.id", ondelete="CASCADE"), nullable=False)

    block_type = Column(String, nullable=False)   # 'rich_text', 'image', 'html', 'cta', 'grid', etc.
    position = Column(Integer, nullable=False, default=0)

    # contenido flexible
    text = Column(Text, nullable=True)            # para rich_text/html si se me da la gana
    image_url = Column(String, nullable=True)
    link_url = Column(String, nullable=True)
    data = Column(JSONB, nullable=True)          # payload flexible (botones, props, etc.)

    created_at = Column(DateTime, default=datetime.utcnow)

    page = relationship("Page", backref="blocks")
