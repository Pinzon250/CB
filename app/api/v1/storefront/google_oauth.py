from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth, OAuthError
from app.core.config import settings
from app.database.session import get_db
from app.modules.auth.service import AuthService

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth:Google"]
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

def _backend_cb_url() -> str:
    base = (getattr(settings, "BACKEND_PUBLIC_URL", None) or "https://localhost:8000").rstrip("/")
    return f"{base}/api/v1/auth/google/callback"

@router.get("/google")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, redirect_uri=_backend_cb_url())

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e.error}")
    
    # se puede usar userinfo endpoint o parse_id_token:
    resp = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
    info = resp.json()

    access, user, roles = AuthService(db).google_upsert_and_token(info)

    # Se redirige al front con el token
    front = (settings.FRONT_URL or "").rstrip("/")
    if front:
        url = f"{front}/auth/callback?token={token}"
        return RedirectResponse(url)
    
    return JSONResponse({"access_token": access, "roles": roles, "email": user.email})