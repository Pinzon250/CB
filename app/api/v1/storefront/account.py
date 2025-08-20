from fastapi import APIRouter, Depends, status, BackgroundTasks, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.utils.email import send_verification_email, send_reset_email
from app.database.session import get_db
from app.modules.auth.service import AuthService
from app.modules.auth.schemas.public import LoginRequest, TokenResponse, AuthResponse, RegisterRequest, UserPublic, ForgotPasswordRequest, ResetPasswordRequest

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)

@router.post("/token", response_model=TokenResponse)
def token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 password flow usa el "username" para el email
    access, _user, _roles = AuthService(db).login(LoginRequest(email=form.username, password=form.password))
    return TokenResponse(access_token=access)

@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    access, user, roles = AuthService(db).login(body)
    return AuthResponse(
        access_token=access,
        user_id = str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=roles
    )

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user, token = AuthService(db).register(body)
    background_tasks.add_task(send_verification_email, user.email, token)
    return UserPublic.model_validate(user)

@router.get("/verify", response_model=UserPublic)
def verify_account(token: str = Query(...), db: Session = Depends(get_db)):
    user = AuthService(db).verify_email(token)
    return UserPublic.model_validate(user)

@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(body: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    token = AuthService(db).request_password_reset(body)
    # No revelar si existe o no: siempre 204
    if token:
        background_tasks.add_task(send_reset_email, body.email, token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).reset_password(body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)