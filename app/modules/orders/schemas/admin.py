from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime

class AdminOrderListItem(BaseModel):
    id: UUID4
    order_number: str
    user_id: UUID4
    status: Optional[str] = None
    grand_total: float
    currency: str
    placed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {
        "from_attributes":True
    }

class AdminOrderDetail(BaseModel):
    id: UUID4
    order_number: str
    user_id: UUID4
    status: Optional[str] = None
    subtotal: float
    shipping_total: float
    tax_total: float
    grand_total:  float
    currency: str
    placed_at: Optional[datetime] = None
    items: List[dict]

    model_config = {
        "from_attributes": True
    }

class AdminOrderStatusUpdate(BaseModel):
    status_code: str