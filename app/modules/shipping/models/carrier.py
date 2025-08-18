import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class Carrier(Base):
    __tablename__ = "carriers"
    __table_args__ = {"schema": "shipping"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False) # Por ejemplo: servientrega, envia, etc (Todo EN MINUSCULAS)
    name = Column(String, nullable=False, unique=True)  # Por ejemplo: Servientrega, Envia, etc (aca si normal)
    tracking_url_template = Column(String, nullable=True)  # Enlace de seguimiento de la transportadora con su id de seguimiento
