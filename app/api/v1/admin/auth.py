from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.modules.auth.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "role_names": list(getattr(user, "role_names", [])),  # ["admin", ...]
        "roles": [ {"id": str(r.id), "name": r.name} for r in getattr(user, "roles", []) ],
    }
