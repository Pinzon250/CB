from fastapi import APIRouter, Depends, Query, Body, Path, status
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.database.session import get_db

from app.modules.catalog.schemas import Page, PageMeta
from app.modules.catalog.schemas.admin import AdminProductDetail, AdminProductCreate, AdminProductImageIn, AdminProductUpdate, AdminCategoryOut, AdminCategoryCreate, AdminBrandOut, AdminBrandCreate
from app.modules.catalog.service import ProductService

router = APIRouter(
    prefix="/api/v1/admin/catalog",
    tags=["Admin:Catalog"],
    dependencies=[Depends(require_admin)]
)

@router.get("/products", response_model=Page)
def list_products_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    brand_id: str | None = None,
    category_id: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    order: str = Query("relevance", pattern="^(relevance|price_asc|price_desc|name|newest)$"),
    db: Session = Depends(get_db)
):
    items, total = ProductService.list_admin(
        db, page=page, size=size, q=q,
        brand_id=brand_id, category_id=category_id,
        min_price=min_price, max_price=max_price, order=order
    )
    return Page(meta=PageMeta(page=page, size=size, total=total), items=items)

@router.get("/product/{product_id}", response_model=AdminProductDetail)
def get_product_admin_detail(
    product_id: str,
    db: Session = Depends(get_db)
):
    return ProductService.get_admin_detail(db, product_id)

# Crear Producto
@router.post("/products/create", response_model=AdminProductDetail, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: AdminProductCreate,
    db: Session = Depends(get_db)
):
    return ProductService.create_product(db, payload)

# Actualizar Producto
@router.patch("/products/update/{product_id}", response_model=AdminProductDetail)
def update_product(
    product_id: str = Path(...),
    payload: AdminProductUpdate = Body(...),
    db: Session = Depends(get_db)
):
    return ProductService.update_product(db, product_id, payload)

# Añadir imagen
@router.post("/products/{product_id}/images", response_model=list[str], status_code=status.HTTP_201_CREATED)
def add_product_image(
    product_id: str,
    body: AdminProductImageIn,
    db: Session = Depends(get_db)
):
    return ProductService.add_image_product(db, product_id, body.url)

# Remover imagen
@router.delete("/products/{product_id}/images/{image_id}", response_model=list[str], status_code=status.HTTP_200_OK)
def remove_product_image(
    product_id: str,
    image_id: str,
    db: Session = Depends(get_db)
):
    return ProductService.remove_image_product(db, product_id, image_id)

# Desactiivar producto
@router.delete("/products/delete/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    ProductService.soft_delete_product(db, product_id)
    return None

# CATEGORIAS ---------
# Crear categoria
@router.post("/categories/create", response_model=AdminCategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: AdminProductCreate, db: Session = Depends(get_db)):
    return ProductService.create_category(db, payload)

# eliminar Categoria
@router.delete("/categories/delete/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: Session = Depends(get_db)):
    ProductService.delete_category(db, category_id)
    return None

# Marcas ---------
# Crear marca
@router.post("/brands/create", response_model=AdminBrandOut, status_code=status.HTTP_201_CREATED)
def create_brand(payload: AdminBrandCreate, db: Session = Depends(get_db)):
    return ProductService.create_brand(db, payload)

# eliminar Marca
@router.delete("/brands/delete/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(brand_id: str, db: Session = Depends(get_db)):
    ProductService.delete_brand(db, brand_id)
    return None