from typing import Optional, Tuple, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.modules.catalog.models import Product
from .models import Cart, CartItem, Order, OrderItem, OrderStatus

class CartRepository:
    @staticmethod
    def get_or_create_for_user(db: Session, user_id: str) -> Cart:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart); db.flush()
        return cart
    
    @staticmethod
    def get_items(db: Session, cart_id: str) -> List[CartItem]:
        return (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart_id)
            .order_by(CartItem.created_at.asc())
            .all()
        )
    
    @staticmethod
    def add_item(db: Session, cart: Cart, product: Product, quantity: int) -> CartItem:
        item = (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id, CartItem.product_id == product.id)
            .first()
        )
        unit_price = float(product.price)
        if item:
            item.quantity += quantity
            item.unit_price = unit_price
            item.line_total = item.quantity * unit_price
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                line_total=quantity * unit_price
            )
            db.add(item)
        db.flush()
        return item
    
    @staticmethod
    def update_item_qty(db: Session, item_id: str, quantity: int) -> Optional[CartItem]:
        item = db.get(CartItem, item_id)
        if not item:
            return None
        if quantity <= 0:
            db.delete(item); db.flush()
            return None
        item.quantity = quantity
        item.line_total = quantity * float(item.unit_price)
        db.flush()
        return item
    
    @staticmethod
    def remove_item(db: Session, item_id: str) -> None:
        item = db.get(CartItem, item_id)
        if item:
            db.delete(item); db.flush()
        
    @staticmethod
    def clear(db: Session, cart_id: str) -> None:
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        db.flush()

class OrderRepository:
    @staticmethod
    def create_from_cart(
        db: Session, user_id: str, cart: Cart, currency: str, status_code: str = "pending"
    ) -> Order:
        # Todos los totakes
        items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        subtotal = sum(float(i.line_total) for i in items)
        shipping_total = 0.0
        tax_total = 0.0
        grand_total = subtotal + shipping_total + tax_total

        # status id si existe
        status_id = None
        if OrderStatus is not None:
            st = db.query(OrderStatus).filter(OrderStatus.code == status_code).first()
            status_id = st.id if st else None

        # se crea la orden
        order = Order(
            user_id=user_id,
            subtotal=subtotal,
            shipping_total=shipping_total,
            tax_total=tax_total,
            grand_total=grand_total,
            currency=currency,
            placed_at=func.now(),
            order_number=f"Ord-{int(func.random()*1000000)}",
            status_id=status_id
        )
        db.add(order); db.flush()

        for it in items:
            prod = db.get(Product, it.product_id)
            oi = OrderItem(
                order_id=order.id,
                product_id=it.product,
                product_name=getattr(prod, "name", "Product"),
                sku=getattr(prod, "sku", None),
                quantity=it.quantity,
                unit_price=float(it.unit_price),
                line_total=float(it.line_total)
            )
            db.add(oi)

            if hasattr(prod, "stock"):
                prod.stock = max(0, int(prod.stock or 0) - int(it.quantity))

        db.flush()
        return order
    
    @staticmethod
    def get_with_items(db: Session, order_id: str) -> Optional[Order]:
        return (
            db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.id == order_id)
            .first()
        )
    
    @staticmethod
    def list_admin(db: Session,  page: int, size: int) -> Tuple[List[Order], int]:
        q = db.query(Order).order_by(Order.placed_at.desc())
        total = q.count()
        items = q.offset((page-1)*size).limit(size).all()
        return items, total
    
    @staticmethod
    def set_status_by_code(db: Session, order: Order, status_code: str) -> None:
        if OrderStatus is None:
            return
        st = db.query(OrderStatus).filter(OrderStatus.code == status_code).first()
        if not st:
            raise ValueError("Codigo de estado invalido")
        order.status_id = st.id
        db.flush()