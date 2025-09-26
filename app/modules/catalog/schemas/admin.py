from typing import Optional, List
from pydantic import BaseModel, UUID4, Field
from datetime import datetime

class AdminProductListItem(BaseModel):
    id: UUID4
    name: str
    slug: str
    price: float
    stock: int
    is_active: bool
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
class AdminProductAttribute(BaseModel):
    name: str
    value: str

class AdminProductDetail(BaseModel):
    id: UUID4
    name: str
    slug: str
    description: Optional[str] = None
    price: float
    stock: int
    is_active: bool
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    images: List[str] = []
    attributes: List[AdminProductAttribute] = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class AdminProductCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    price: float = Field(ge=0)
    stock: int = 0
    is_active: bool = True
    brand_id: Optional[UUID4] = None
    category_id: Optional[UUID4] = None
    images: Optional[List[str]] = None

class AdminProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    brand_id: Optional[UUID4] = None
    category_id: Optional[UUID4] = None

class AdminProductImageIn(BaseModel):
    url: str

# Marcas (Brands)
class AdminBrandCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: Optional[str] = None

class AdminBrandOut(BaseModel):
    id: UUID4
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# Categorias (Categories)
class AdminCategoryCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: Optional[str] = None
    parent_id: Optional[UUID4] = None

class AdminCategoryOut(BaseModel):
    id: UUID4
    name: str
    slug: str
    parent_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }