from fastapi import HTTPException, status
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.modules.catalog.repository import ProductRepository, CategoryRepository, BrandRepository
from app.modules.catalog.schemas.admin import AdminProductListItem, AdminProductDetail, AdminProductAttribute, AdminProductCreate, AdminProductImageIn, AdminProductUpdate, AdminBrandCreate, AdminBrandOut, AdminCategoryCreate, AdminCategoryOut
from app.modules.catalog.schemas.public import PublicProductListItem, PublicProductAttribute, PublicProductDetail

class ProductService:

    # Servicios admin
    @staticmethod
    def list_admin(
        db: Session,
        *,
        page: int,
        size: int,
        q: Optional[str],
        brand_id: Optional[str],
        category_id: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        order: str
    ) -> Tuple[List[AdminProductListItem], int]:
        items, total = ProductRepository.list(
            db,
            page=page, size=size, q=q,
            brand_id=brand_id, category_id=category_id,
            min_price=min_price, max_price=max_price,
            only_active=False, order=order
        )
        mapped = [
            AdminProductListItem(
                id=p.id,
                name=p.name,
                slug=getattr(p, "slug", str(p.id)),
                price=float(p.price),
                stock=getattr(p, "stock", 0),
                is_active=p.is_active,
                brand_name=getattr(getattr(p, "brand", None), "name", None),
                category_name=getattr(getattr(p, "category", None), "name", None),
                image_url=getattr(p, "_first_image_url", None),
                created_at=p.created_at,
                updated_at=p.updated_at,
            ) for p in items
        ]
        return mapped, total
    
    # Servicios publicos
    @staticmethod
    def list_public(
        db: Session,
        *,
        page: int,
        size: int,
        q: Optional[str],
        brand_id: Optional[str],
        category_id: Optional[str],
        min_price: Optional[str],
        max_price: Optional[str],
        order: str,
        in_stock: Optional[bool],
    ) -> Tuple[List[PublicProductListItem], int]:
        items, total = ProductRepository.list(
            db,
            page=page, size=size, q=q,
            brand_id=brand_id, category_id=category_id,
            min_price=min_price, max_price=max_price,
            only_active=True, order=order
        )

        if in_stock is not None:
            items = [p for p in items if (getattr(p, "stock", 0) > 0) == in_stock]
            total = len(items)

        mapped = [
            PublicProductListItem(
                id=p.id,
                name=p.name,
                slug=getattr(p, "slug", str(p.id)),
                price=float(p.price),
                stock=getattr(p, "stock", 0),
                brand_name=getattr(getattr(p, "brand", None), "name", None),
                category_name=getattr(getattr(p, "category", None), "name", None),
                image_url=getattr(p, "_first_image_url", None),
            ) for p in items
        ]
        return mapped, total
    
    # Visualizar detalles del producto admin
    @staticmethod
    def get_admin_detail(db: Session, product_id: str) -> AdminProductDetail:
        p = ProductRepository.get_by_id(db, product_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        
        images = ProductRepository.get_images(db, p.id)
        attrs_pairs = ProductRepository.get_attributes(db, p.id)
        attrs = [AdminProductAttribute(name=n, value=v) for n, v in attrs_pairs]

        return AdminProductDetail(
            id=p.id,
            name=p.name,
            slug=getattr(p, "slug", str(p.id)),
            description=getattr(p, "description", None),
            price=float(p.price),
            stock=getattr(p, "stock", 0),
            is_active=p.is_active,
            brand_name=getattr(getattr(p, "brand", None), "name", None),
            category_name=getattr(getattr(p, "category", None), "name", None),
            images=images,
            attributes=attrs,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
    
    # Visualizar detalles del producto publico
    @staticmethod
    def get_public_detail_by_slug(db: Session, slug: str) -> PublicProductDetail:
        p = ProductRepository.get_by_slug(db, slug, only_active=True)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        images = ProductRepository.get_images(db, p.id)
        attrs_pairs = ProductRepository.get_attributes(db, p.id)
        attrs = [PublicProductAttribute(name=n, value=v) for n, v in attrs_pairs]

        return PublicProductDetail(
            id=p.id,
            name=p.name,
            slug=getattr(p, "slug", slug),
            description=getattr(p, "description", None),
            price=float(p.price),
            stock=getattr(p, "stock", 0),
            brand_name=getattr(getattr(p, "brand", None), "name", None),
            category_name=getattr(getattr(p, "category", None), "name", None),
            images=images,
            attributes=attrs
        )
    
    @staticmethod
    def create_product(db: Session, dto: AdminProductCreate) -> AdminProductDetail:
        try:
            p = ProductRepository.create(
                db,
                name=dto.name,
                slug=dto.slug,
                price=dto.price,
                stock=dto.stock,
                is_active=dto.is_active,
                brand_id=str(dto.brand_id) if dto.brand_id else None,
                category_id=str(dto.category_id) if dto.category_id else None
            )
            if dto.images:
                ProductRepository.set_images(db, p.id, dto.images)
            db.commit()
            db.refresh(p)
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        return ProductService.get_admin_detail(db, str(p.id))
    
    @staticmethod
    def update_product(db: Session, product_id: str, dto: AdminProductUpdate) -> AdminProductDetail:
        p = ProductRepository.get_by_id(db, product_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        
        try:
            ProductRepository.update(
                db,
                p,
                name=dto.name,
                slug=dto.slug,
                description=dto.Description,
                price=dto.price,
                stock=dto.stock,
                is_active=dto.is_active,
                brand_id=str(dto.brand_id) if dto.brand_id else None if dto.brand_id is not None else None,
                category_id=str(dto.category_id) if dto.category_id else None if dto.category_id is not None else None,
            )
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        return ProductService.get_admin_detail(db, str(p.id))
    
    @staticmethod
    def add_image_product(db: Session, product_id: str, url: str) -> List[str]:
        p = ProductRepository.get_by_id(db, product_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Producto no encontrado")
        ProductRepository.add_image(db, product_id, url)
        db.commit()
        return ProductRepository.get_images(db, product_id)
    
    @staticmethod
    def remove_image_product(db: Session, product_id: str, image_id: str) -> List[str]:
        p = ProductRepository.get_by_id(db, product_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Producto no encontrado")
        ProductRepository.remove_image(db, product_id, image_id)
        db.commit()
        return ProductRepository.get_images(db, product_id)
    
    @staticmethod
    def soft_delete_product(db: Session, product_id: str) -> None:
        p = ProductRepository.get_by_id(db, product_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        ProductRepository.soft_delete(db, p)
        db.commit()

    # Categorias
    @staticmethod
    def create_category(db: Session, dto: AdminCategoryCreate) -> AdminCategoryOut:
        try:
            c = CategoryRepository.create(db, name=dto.name, slug=dto.slug, parent_id=str(dto.parent_id) if dto.parent_id else None)
            db.commit(); db.refresh(c)
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return AdminCategoryOut.model_validate(c)
    
    @staticmethod
    def delete_category(db: Session, category_id: str) -> None:
        c = CategoryRepository.get(db, category_id)
        if not c:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
        if CategoryRepository.products_count(db, category_id) > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La categoria tiene productos asignados")
        if CategoryRepository.children_count(db, category_id) > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La categoria tiene categorias hijas")
        CategoryRepository.delete(db, c); db.commit()

    # Marcas
    def create_brand(db: Session, dto: AdminBrandCreate) -> AdminBrandOut:
        try:
            b = BrandRepository.create(db, name=dto.name, slug=dto.slug)
            db.commit(); db.refresh(b)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return AdminBrandOut.model_validate(b)
    
    @staticmethod
    def delete_brand(db: Session, brand_id: str) -> None:
        b = BrandRepository.get(db, brand_id)
        if not b:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
        if BrandRepository.products_count(db, brand_id) > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La marca tiene productos asociados a ella")
        BrandRepository.delete(db, b); db.commit()