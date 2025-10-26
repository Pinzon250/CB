from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.deps import get_current_user
from app.modules.catalog.models import Product
from .repository import CartRepository, OrderRepository
from .schemas.public import CartItemIn, CartOut, CartItemOut, CheckoutIn, OrderItemOut, OrderOut
from app.modules.orders.models import *

class CartService:
    @staticmethod
    def get_cart(db: Session, user_id: str) -> CartOut:
        cart = CartRepository.get_or_create_for_user(db, user_id)
        items = CartRepository.get_items(db, cart.id)
        subtotal = sum(float(i.line_total) for i in items)
        out_items = []
        for i in items:
            prod = db.get(Product, i.product_id)
            out_items.append(CartItemOut(
                id=i.id, product_id=i.product_id,
                product_name=getattr(prod, "name", "Product"),
                quantity=i.quantity,
                unit_price=float(i.unit_price),
                line_total=float(i.line_total),
                created_at=i.created_at, updated_at=i.updated_at
            ))
        return CartOut(id=cart.id, items=out_items, subtotal=subtotal)
    
    @staticmethod
    def add_item(db: Session, user_id: str, dto: CartItemIn) -> CartOut:
        cart = CartRepository.get_or_create_for_user(db, user_id)
        prod = db.get(Product, dto.product_id)
        if not prod or not getattr(prod, "is_active", True):
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if getattr(prod, "stock", 0) < dto.quantity:
            raise HTTPException(status_code=400, detail="Insuficiente stock")
        CartRepository.add_item(db, cart, prod, dto.quantity)
        db.commit()
        return CartService.get_cart(db, user_id)
    
    @staticmethod
    def update_item(db: Session, user_id: str, item_id: str, quantity: int) -> CartOut:
        item = CartRepository.update_item_qty(db, item_id, quantity)
        db.commit()
        return CartService.get_cart(db, user_id, item)
    
    @staticmethod
    def remove_item(db: Session, user_id: str, item_id: str) -> CartOut:
        CartRepository.remove_item(db, item_id)
        db.commit()
        return CartService.get_cart(db, user_id)
    
    @staticmethod
    def checkout(db: Session, user_id: str, dto: CheckoutIn) -> OrderOut:
        cart = CartRepository.get_or_create_for_user(db, user_id)
        items = CartRepository.get_items(db, cart.id)
        if not items:
            raise HTTPException(status_code=400, detail="El carrito esta vacio")
        
        # Validamos stock antes de crear el pedido
        for i in items:
            prod = db.get(Product, i.product_id)
            if not prod or not getattr(prod, "is_active", True):
                raise HTTPException(status_code=400, detail="Producto invalido en el carrito")
            if getattr(prod, "stock", 0) < i.quantity:
                raise HTTPException(status_code=400, detail=f"Insuficiente stock por {prod.name}")
            
        order = OrderRepository.create_from_cart(db, user_id, cart, dto.currency, status_code="pending")
        CartRepository.clear(db, cart.id)
        db.commit()

        # map aa orderout
        o_items = []
        for oi in db.query(OrderItem).filter(OrderItem.order_id == order.id).all():
            o_items.append(OrderItemOut(
                product_id=oi.product_id,
                product_name=oi.product_name,
                quantity=oi.quantity,
                unit_price=float(oi.unit_price),
                line_total=float(oi.line_total)
            ))
        # status name si existe
        status_name = None
        if hasattr(order, "status") and order.status:
            status_name = getattr(order.status, "code", None) or getattr(order.status, "name", None)

        return OrderOut(
            id=order.id,
            order_number=order.order_number,
            status=status_name,
            subtotal=float(order.subtotal),
            shipping_total=float(order.shipping_total),
            tax_total=float(order.tax_total),
            grand_total=float(order.grand_total),
            currency=order.currency,
            placed_at=order.placed_at,
            items=o_items
        )

class AdminOrderService:
    @staticmethod
    def list_admin(db: Session, page: int, size: int):
        items, total = OrderRepository.list_admin(db, page, size)
        # Mapeo rapido tin
        out = []
        for o in items:
            status_name = None
            if hasattr(o, "status") and o.status:
                status_name = getattr(o.status, "code", None) or getattr(o.status, "name", None)
            out.append({
                "id": o.id, "order_number": o.order_number, "user_id": o.user_id,
                "status":status_name, "grand_total": float(o.grand_total),
                "currency": o.currency, "placed_at": o.placed_at
            })
        return out, total
    
    @staticmethod
    def set_status(db: Session, order_id: str, status_code: str):
        o = db.get(Order, order_id)
        if not o:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        try:
            OrderRepository.set_status_by_code(db, o, status_code)
            db.commit()
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return {"ok": True}