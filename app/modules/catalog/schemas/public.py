from typing import Optional, List
from pydantic import BaseModel, UUID4
from datetime import datetime

class PublicProductListItem(BaseModel):
    id: UUID4
    name: str
    slug: str
    price: float
    stock: int
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {
        'from_attributes' : True
    }

class PublicProductAttribute(BaseModel):
    name: str
    value: str

class PublicProductDetail(BaseModel):
    id: UUID4
    name: str
    description: Optional[str] = None
    slug: str
    price: float
    stock: int
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    images: List[PublicProductAttribute] = []
    attributes: List[PublicProductAttribute] = []

    model_config = {
        "from_attributes" : True
    }