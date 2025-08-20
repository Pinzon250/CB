from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALG = settings.ALGORITHM

def hash_password(p: str) -> str: return pwd.hash(p)
def verify_password(p: str, h: str) -> bool: return pwd.verify(p, h)

def _encode(payload: dict, minutes: int):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes)
    to_encode = {**payload, "iat": now, "exp": exp}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALG)

def _decode(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALG])

def create_access_token(user_id: str, roles: list[str], minutes: int | None = None) -> str:
    return _encode(
        {"sub": user_id, "roles": roles, "type": "access"},
        minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

# Para reset/verify por proposito
def create_purpose_token(sub: str, purpose: str, minutes: int) -> str:
    return _encode(
        {"sub": sub, "purpose": purpose, "type": "oneoff"},
        minutes
    )

def decode_purpose_token(token: str, expected_purpose: str) -> dict:
    try:
        payload = _decode(token)
        if payload.get("purpose") != expected_purpose:
            raise JWTError("Invalid purpose")
        return payload
    except JWTError as e:
        raise ValueError("INVALID_TOKEN") from e