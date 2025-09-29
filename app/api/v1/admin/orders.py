from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.deps import require_admin
from app.database.session import get_db
from app.modules.orders.service import AdminOrderService

router = APIRouter(
    prefix=("/api/v1/admin/orders"),
    tags=["Admin: Orders"],
    dependencies=[Depends(require_admin)]
)

@router.get("/")
def list_orders(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = AdminOrderService.list_admin(db, page, size)
    return {"meta": {"page": page, "size": size, "total": total}, "items": items}

@router.post("/{order_id}/status")
def set_status(order_id: str, status_code: str, db: Session = Depends(get_db)):
    return AdminOrderService.set_status(db, order_id, status_code)