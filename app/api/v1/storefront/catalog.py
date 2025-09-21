from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.catalog.service import ProductService
from app.modules.catalog.schemas import Page, PageMeta
from app.modules.catalog.schemas.public import PublicProductDetail

router = APIRouter(
    prefix="/api/v1/storefront/catalog",
    tags=["Catalogo"]
)

@router.get("/products", response_model=Page)
def list_products_storefront(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=60),
    q: str | None = None,
    brand_id: str | None = None,
    category_id: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    order: str = Query("relevance", pattern="^(relevance|price_asc|price_desc|name|newest)$"),
    in_stock: bool | None = None,
    db: Session = Depends(get_db),
):
    items, total = ProductService.list_public(
        db, page=page, size=size, q=q,
        brand_id=brand_id, category_id=category_id,
        min_price=min_price, max_price=max_price,
        order=order, in_stock=in_stock
    )
    return Page(meta=PageMeta(page=page, size=size, total=total), items=items)

@router.get("/product/{slug}", response_model=PublicProductDetail)
def get_product_public_detail(
    slug: str,
    db: Session = Depends(get_db)
):
    return ProductService.get_public_detail_by_slug(db, slug)