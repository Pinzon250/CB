from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
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
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc
    
    user = db.query(User).get(user_id)
    if not user:
        raise credentials_exc
    return user

def require_roles(allowed: list[str]):
    def _dep(user: User = Depends(get_current_user)):
        # Si se usa relacion de many-to-many, adaptar a set(user.roles)
        role = getattr(user, "role", None) # o calcular desde user.roles
        if role not in allowed:
            raise HTTPException(status_code=4043, detail="Forbidden")
        return user
    return _dep