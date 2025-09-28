from typing import List, Optional
from pydantic import BaseModel, UUID4, Field
from datetime import datetime

class CartItemIn(BaseModel):
    product_id: UUID4
    quantity: int = Field(ge=1, le=999)

class CartItemOut(BaseModel):
    id: UUID4
    product_id: UUID4
    product_name: str
    quantity: int
    unit_price: float
    line_total: float
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class CartOut(BaseModel):
    id: UUID4
    items: List[CartItemOut]
    subtotal: float
    currency: str = "COP"

    model_config = {
        "from_attributes": True
    }

class CheckoutIn(BaseModel):
    #  Agregar lo del shipping y billing en un futuuro
    currency: str = "COP"

class OrderItemOut(BaseModel):
    product_id: UUID4
    product_name: str
    quantity: int
    unit_price: float
    line_total: float

    model_config = {
        "from_attributes": True
    }

class OrderOut(BaseModel):
    id: UUID4
    order_number: str
    status: Optional[str] = None
    subtotal: float
    shipping_total: float
    tax_total: float
    grand_total: float
    currency: str
    placed_at: Optional[datetime] = None
    items: List[OrderItemOut]

    model_config = {
        "from_attributes": True
    }