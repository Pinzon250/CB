from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import verify_password, create_access_token, hash_password, create_purpose_token, decode_purpose_token
from .repository import UserRepositoy
from .schemas.public import LoginRequest, RegisterRequest, ForgotPasswordRequest, ResetPasswordRequest
from typing import Tuple
from datetime import datetime, timezone

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepositoy(db)

    # ----------- LOGIN ----------- 
    def login(self, data: LoginRequest) ->  Tuple[str, object, list[str]]:
        user = self.users.get_by_email(data.email)

        # Mensaje generico para no filtrar si existe o no
        cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

        if not user or not verify_password(data.password, user.password):
            raise cred_exc
        
        # Estados de el usuario
        if getattr(user, "deleted_at", None):
            raise HTTPException(status_code=403, detail="Cuenta eliminada")
        
        if not getattr(user, "is_active", True):
            raise HTTPException(status_code=403, detail="Cuenta deshabilitada")
        
        if not getattr(user, "verified", False):
            raise HTTPException(status_code=403, detail="Cuenta no verificada")
        
        if getattr(user, "banned_until", None) and user.banned_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=403, detail="Cuenta baneada")
        
        roles = self.users.get_roles(user.id)

        # Se crean JWT con los roles[]
        access = create_access_token(user_id=str(user.id), roles=roles)

        # Actualziar last_login_at
        self.users.update_last_login(user)

        return access, user, roles
    
    # ----------- REGISTER -----------
    def register(self, data: RegisterRequest):
        if self.users.email_exists(data.email):
            raise HTTPException(status_code=400, detail="Correo ya registrado")
        
        user = self.users.create_user(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=hash_password(data.password),
            verified=False,
            is_active=True
        )
        # Rol predeterminado
        self.users.add_role_by_name(user.id, "customer")

        self.db.commit()
        self.db.refresh(user)
        
        # Token de verificacion (Esa monda no se guarda en la bd)
        token = create_purpose_token(sub=data.email, purpose="verify", minutes=60*24)
        
        return user, token
    # ----------- PASSWORDS -----------
    def request_password_reset(self, data: ForgotPasswordRequest) -> str | None:
        """Devolver un token si el usuario existe; si no, None(No se revela su existencia)""" 
        user = self.users.get_by_email(data.email)
        if not user:
            return None
        # Verificar estados (is_active, deleted_at, banned_until...)
        token = create_purpose_token(sub=user.email, purpose="reset", minutes=15)
        return token
    
    def reset_password(self, data: ResetPasswordRequest) -> None:
        try:
            payload = decode_purpose_token(data.token, expected_purpose="reset")
        except ValueError:
            raise HTTPException(status_code=400, detail="Token invalido o expirado")
        
        email = payload["sub"]
        user = self.users.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        self.user.set_password(user, hash_password(data.new_password))
        self.db.commit()
     
    # ----------- VERIFY EMAIL -----------
    def verify_email(self, token: str):
        payload = decode_purpose_token(token, expected_purpose="verify")
        email = payload["sub"]
        user = self.users.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        self.users.set_verified(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    # ----------- GOOGLE -----------
    def google_upsert_and_token(self, info: dict):
        email = info.get("email")
        sub = info.get("sub")
        if not email or not sub:
            raise HTTPException(status_code=400, detail="Perfil de google invalido")
        
        # Primero busca por google_sub
        user = self.users.get_by_google_sub(sub)
        
        # Si no, busca por el email (es el primer vinculo SSO)
        if not user:
            user = self.users.get_by_email(email)
            if user:
                # Vincula SSO a la cuenta existente
                self.users.link_google_sub(user, sub)
            else:
                # Crea la cuenta nueva
                user = self.user.create_user(
                    email=email,
                    first_name=info.get("given_name"),
                    last_name=info.get("family_name"),
                    verified=bool(info.get("email_verified", False)),
                    is_active=True,
                    google_sub=sub
                )

                # Rol predeterminado
                self.users.add_role_by_name(user.id, "customer")

        # Se actualiza el perfil y sus estados
        self.users.update_profile_from_google(
            user,
            first_name=info.get("given_name"),
            last_name=info.get("family_name"),
            picture_url=info.get("picture"),
            email_verified=info.get("email_verified"),
        )

        # Declaramos las reglas de acceso
        if getattr(user, "deleted_at", None):
            raise HTTPException(status_code=403, detail="Cuenta eliminada")
        if not getattr(user, "is_active", True):
            raise HTTPException(status_code=403, detail="Cuenta deshabilitada")
        
        # Actualizar cambios en la base de datos
        self.db.commit()
        self.db.refresh(user)

        # Token con sus roles
        roles = self.users.get_roles(user.id)
        access = create_access_token(user_id=str(user.id), roles=roles)

        return access, user, roles