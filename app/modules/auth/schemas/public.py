from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID


# ------- LOGIN -------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AuthResponse(TokenResponse):
    user_id: UUID | str
    email: EmailStr
    first_name: str
    last_name: str
    roles: List[str] = []

# ------- REGISTER -------
class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)

class UserPublic(BaseModel):
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    verified: bool

    model_config = {
        "from_attributes": True
    }

# ------- FORGOT/RESET PASSWORD -------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)