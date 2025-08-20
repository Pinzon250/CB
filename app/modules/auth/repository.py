from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone

from app.modules.auth.models import  User, Role, UserRole

class UserRepositoy:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def email_exists(self, email:str) -> bool:
        return self.db.query(User.id).filter(User.email == email).first() is not None

    def create_user(self, **data) -> User:
        user = User(**data)
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
    
    def add_role_by_name(self, user_id: str, role_name: str = "customer"):
        role = self.db.query(Role).filter(Role.name == role_name).first()
        if role is None:
            role = Role(name=role_name)
            self.db.add(role)
            self.db.flush()
            self.db.refresh(role)
        link = UserRole(user_id=user_id, role_id=role.id)
        self.db.add(link)

    def get_roles(self, user_id: str) -> List[str]:
        # Sentencia SQL
        # SELECT r.name FROM roles r JOIN user_roles ur ON ur.role_id = r.id WHERE ur.user_id=:user_id
        rows = (
            self.db.query(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .all()
        )
        return [r[0] for r in rows]
    
    def update_last_login(self, user: User):
        user.last_login_at = datetime.now(timezone.utc)

    def set_verified(self, user: User):
        user.verified = True

    def set_password(self, user: User, password_hash: str) -> None:
        user.password = password_hash

    # Un helper para flags de estado
    def is_banned(self, user: User) -> bool:
        return bool(user.banned_until and user.banned_until > datetime.now(timezone.utc))
    
    # ------------------ GOOGLE AUTH ------------------
    def get_by_google_sub(self, sub: str) -> Optional[User]:
        return self.db.query(User).filter(User.google_sub == sub).first()
    
    def update_profile_from_google(
            self,
            user: User,
            *,
            first_name: str|None,
            last_name: str|None,
            picture_url: str|None,
            email_verified: bool|None
        ):
        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        if picture_url is not None and hasattr(user, "picture_url"):
            user.picture_url = picture_url
        if email_verified is True:
            user.verified = True
        user.last_login_at = datetime.now(timezone.utc)

    def link_google_sub(self, user: User, sub: str):
        user.google_sub = sub

