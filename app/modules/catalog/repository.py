from typing import Optional, Tuple, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.modules.catalog.models import *

def _slugify(text: str) -> str:
    return "-".join(text.lower().strip().split())

class ProductRepository:
    @staticmethod
    def list(
        db: Session, 
        *,
        page: int = 1,
        size: int = 20,
        q: Optional[str] = None,
        brand_id: Optional[str] = None,
        category_id: Optional[str] = None,
        min_price: Optional[str] = None,
        max_price: Optional[str] = None,
        only_active: bool = False,
        order: str = "relevance"
    ) -> Tuple[List[Product], int]:
        """
        Se devuelve (items, total) con filtros y paginacion.
        order (relevance, price_desc, name, newest)
        """
        query = (
            db.query(Product).options(
                joinedload(Product.brand),
                joinedload(Product.category)
            )
        )

        if only_active:
            query = query.filter(Product.is_active.is_(True))

        if q:
            like = f"%{q.strip()}"
            query = query.filter(or_(Product.name.ilike(like), Product.description.ilike(like)))
        
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        # Orden
        if order == "price_asc":
            query = query.order_by(Product.price.asc(), Product.created_at.desc())
        elif order == "price_desc":
            query = query.order_by(Product.price.desc(), Product.created_at.desc())
        elif order == "name":
            query = query.order_by(Product.name.asc())
        elif order == "newest":
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.updated_at.desc())

        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()

        # Adjuntamos la primera imagne por producto
        try:
            if items and ProductImage is not None:
                ids = [p.id for p in items]
                rows = (
                    db.query(ProductImage.product_id, ProductImage.image_url)
                    .filter(ProductImage.product_id.in_(ids))
                    .order_by(ProductImage.created_at.asc())
                    .all()
                )
                first_img = {}
                for pid, url in rows:
                    first_img.setdefault(pid, url)
                for p in items:
                    setattr(p, "_first_image_url", first_img.get(p.id))
        except Exception:
            pass

        return items, total
    
    @staticmethod
    def get_by_id(db: Session, product_id: str) -> Optional[Product]:
        return (
            db.query(Product).options(
                joinedload(Product.brand),
                joinedload(Product.category)
            )
            .filter(Product.id == product_id)
            .first()
        )
    
    @staticmethod
    def get_by_slug(db: Session, slug: str, *, only_active: bool = False) -> Optional[Product]:
        q = (
            db.query(Product)
            .options(
                joinedload(Product.brand),
                joinedload(Product.category)
            )
            .filter(Product.slug == slug)
        )
        if only_active:
            q = q.filter(Product.is_active.is_(True))
        return q.first()
    
    @staticmethod
    def get_images(db: Session, product_id: str) -> List[str]:
        if ProductImage is None:
            return []
        rows = (
            db.query(ProductImage.image_url)
            .filter(ProductImage.product_id == product_id)
            .order_by(ProductImage.created_at.asc())
            .all()
        )
        return [r[0] for r in rows]
    
    @staticmethod
    def get_attributes(db: Session, product_id: str) -> List[tuple[str, str]]:
        """
        Devuelve la lista [(attr_name, value, etc.)...]
        """
        if not (ProductAttribute and Attribute):
            return []
        rows = (
            db.query(Attribute.name, ProductAttribute.value)
            .join(ProductAttribute, ProductAttribute.attribute_id == Attribute.id)
            .filter(ProductAttribute.product_id == product_id)
            .order_by(Attribute.name.asc())
            .all()
        )
        return [(name, value) for name, value in rows]
    
    @staticmethod
    def exists_slug(db: Session, slug: str, exclude_id: Optional[str] = None) -> bool:
        q = db.query(func.count(Product.id)).filter(Product.slug == slug)
        if exclude_id:
            q = q.filter(Product.id != exclude_id)
        return db.scalar(q) > 0
    
    @staticmethod
    def ensure_brand(db: Session, brand_id: Optional[str]) -> Optional[Brand]:
        if not brand_id:
            return None
        brand = db.get(Brand, brand_id)
        if not brand:
            raise ValueError("Marca no encontrada")
        return brand
    
    @staticmethod
    def ensure_category(db: Session, category_id: Optional[str]) -> Optional[Category]:
        if not category_id:
            return None
        cat = db.get(Category, category_id)
        if not cat:
            raise ValueError("Categoria no encontrada")
        return cat
    
    @staticmethod
    def create(
        db: Session,
        *,
        name: str,
        slug: Optional[str],
        description: Optional[str] = None,
        price: float,
        stock: int,
        is_active: bool,
        brand_id: Optional[str],
        category_id: Optional[str]
    ) -> Product:
        #slug
        final_slug = slug or _slugify(name)
        # Evitar duplicados
        base = final_slug
        i = 1
        while ProductRepository.exists_slug(db, final_slug):
            i += 1
            final_slug = f"{base}-{i}"

        # validaciones FK
        ProductRepository.ensure_brand(db, brand_id)
        ProductRepository.ensure_category(db, category_id)

        p = Product(
            name=name,
            slug=final_slug,
            description=description,
            price=price,
            stock=stock,
            is_active=is_active,
            brand_id=brand_id,
            category_id=category_id
        )
        db.add(p)
        db.flush()
        return p
    
    @staticmethod
    def update(
        db: Session,
        product: Product,
        *,
        name: Optional[str],
        slug: Optional[str],
        description: Optional[str],
        price: Optional[float],
        stock: Optional[int],
        is_active: Optional[bool],
        brand_id: Optional[str],
        category_id: Optional[str],
    ) -> Product:
        if name is not None:
            product.name = name
        
        if slug is not None:
            new_slug = slug or _slugify(product.name)
            if ProductRepository.exists_slug(db, new_slug, exclude_id=product.id):
                raise ValueError("Slug ya existente")
            product.slug = new_slug

        if description is not None:
            product.Description = description
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        if is_active is not None:
            product.is_active = is_active
        
        if brand_id is not None:
            ProductRepository.ensure_brand(db, brand_id)
            product.brand_id = brand_id
        
        if category_id is not None:
            ProductRepository.ensure_category(db, category_id)
            product.category_id = category_id

        db.flush()
        return product
    
    @staticmethod
    def add_image(db: Session, product_id: str, url: str) -> ProductImage:
        if ProductImage is None:
            raise ValueError("ProductImage modelo no disponible")
        img = ProductImage(product_id=product_id, image_url=url)
        db.add(img)
        db.flush()
        return img

    @staticmethod
    def remove_image(db: Session, product_id: str, image_id: str) -> None:
        if ProductImage is None:
            return
        img = db.get(ProductImage, image_id)
        if img and str(img.product_id) == str(product_id):
            db.delete(img)
            db.flush()

    @staticmethod
    def set_images(db: Session, product_id: str, urls: List[str]) -> None:
        if ProductImage is None:
            return
        db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
        db.flush()
        for u in urls:
            db.add(ProductImage(product_id=product_id, image_url=u))
        db.flush()

    @staticmethod
    def soft_delete(db: Session, product: Product) -> None:
        product.is_active = False
        db.flush()

# Repositorio de marcas
class BrandRepository:

    @staticmethod
    def exists_slug(db: Session, slug: str) -> bool:
        return db.scalar(db.query(func.count(Brand.id).filter(Brand.slug == slug))) > 0
    
    # Crear marca
    @staticmethod
    def create(db: Session, *, name: str, slug: Optional[str]) -> Brand:
        final_slug = slug or _slugify(name)
        base = final_slug
        i = 1
        while BrandRepository.exists_slug(db, final_slug):
            i += 1
            final_slug = f"{base}-{i}"
        
        b = Brand(name=name, slug=final_slug)
        db.add(b);
        db.flush()
        return b
    
    @staticmethod
    def get(db: Session, brand_id: str) -> Optional[Brand]:
        return db.get(Brand, brand_id)
    
    @staticmethod
    def products_count(db: Session, brand_id: str) -> int:
        return db.scalar(db.query(func.count(Product.id)).filter(Product.brand_id == brand_id)) or 0
    
    @staticmethod
    def delete(db: Session, brand: Brand) -> None:
        db.delete(brand); 
        db.flush()

# Repositorio de categorias
class CategoryRepository:

    @staticmethod
    def exists_slug(db: Session, slug: str) -> bool:
        return db.scalar(db.query(func.count(Category.id)).filter(Category.slug == slug)) > 0
    
    @staticmethod
    def ensure_parent(db: Session, parent_id: Optional[str]) -> None:
        if parent_id:
            if not db.get(Category, parent_id):
                raise ValueError("Categoria padre no encontrada")
            
    @staticmethod
    def create(db: Session, *, name: str, slug: Optional[str], parent_id: Optional[str]) -> Category:
        final_slug = slug or _slugify(name)
        base = final_slug
        i = 1
        while CategoryRepository.exists_slug(db, final_slug):
            i += 1
            final_slug = f"{base}-{i}"
        CategoryRepository.ensure_parent(db, parent_id)
        c = Category(name=name, slug=final_slug, parent_id=parent_id if hasattr(Category, "parent_id") else None)
        db.add(c); db.flush()
        return c
    
    @staticmethod
    def get(db: Session, category_id: str) -> Optional[Category]:
        return db.get(Category, category_id)
    
    @staticmethod
    def products_count(db: Session, category_id: str) -> int:
        return db.scalar(db.query(func.count(Product.id)).filter(Product.category_id == category_id)) or 0
    
    @staticmethod
    def children_count(db: Session, category_id: str) -> int:
        if not hasattr(Category, "parent_id"):
            return 0
        return db.scalar(db.query(func.count(Category.id)).filter(Category.parent_id == category_id)) or 0
    
    @staticmethod
    def delete(db: Session, category: Category) -> None:
        db.delete(category); db.flush()