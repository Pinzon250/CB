import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.database.base import Base
from datetime import datetime

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)

class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema" : "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("auth.roles.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="role_links")
    role = relationship("Role", lazy="joined")

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    phone = Column(String, nullable=True)
    phone_confirmed_at = Column(DateTime, nullable=True)
    verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    token_verification = Column(String(100), nullable=True)

    picture_url = Column(String, nullable=True)
    google_sub = Column(Text, unique=True, nullable=True)

    last_login_at = Column(DateTime, nullable=True)
    banned_until = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role_links = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    roles = association_proxy("role_links", "role")
    role_names = association_proxy("role_links", "role.name")

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")