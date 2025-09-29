from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.database.session import get_db
from app.modules.orders.service import CartService
from app.modules.orders.schemas.public import CartItemIn, CheckoutIn

router = APIRouter(
    prefix="/api/v1/storefront/cart",
    tags=["Cart"]
)

@router.get("/")
def get_cart(db: Session =Depends(get_db), user = Depends(get_current_user)):
    return CartService.get_cart(db, str(user.id))

@router.post("/items")
def add_item(payload: CartItemIn, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return CartService.add_item(db, str(user.id), payload)

@router.patch("/items/update/{item_id}")
def update_item(item_id: str, quantity: int = Query(..., ge=0, le=999), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return CartService.update_item(db, str(user.id), item_id, quantity)

@router.delete("/items/delete/{item_id}")
def remove_item(item_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return CartService.remove_item(db, str(user.id), item_id)

@router.post("/checkout")
def checkouut(payload: CheckoutIn, db: Session =  Depends(get_db), user = Depends(get_current_user)):
    return CartService.checkout(db, str(user.id), payload)