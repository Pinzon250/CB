from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Iterable
from app.core.config import settings
from app.database.session import get_db
from app.modules.auth.models import User


oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
ALG = settings.ALGORITHM

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db))-> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pueden validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALG])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exc
        
        try:
            uid: UUID | str = UUID(user_id)
        except Exception:
            uid = user_id
    except JWTError:
        raise credentials_exc
    
    user = db.get(User, uid)

    if not user:
        raise credentials_exc
    return user

def require_roles(allowed: Iterable[str]):
    allowed_norm = {r.strip().lower() for r in allowed}

    def _dep(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if getattr(user, "is_admin", False):
            return user
        
        names = [n.strip().lower() for n in getattr(user, "role_names", []) if isinstance(n, str)]
        if set(names) & allowed_norm:
            return user
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    
    return _dep

require_admin = require_roles({"admin", "superadmin"})