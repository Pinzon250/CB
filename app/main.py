from fastapi import FastAPI
from sqlalchemy import text
from app.database.session import engine
from app.database.base import Base

from app.database.models import *

# Routers fastapi
from app.api.v1.storefront import *

# admin routers
from app.api.v1.admin import catalog as catalog_adm
from app.api.v1.admin import auth, orders

description = """
Cibercity API es el núcleo del ecosistema de comercio electrónico **Cibercity**. 🚀  

## Catálogo
Puedes:
* **Listar productos** con filtros avanzados.
* **Consultar categorías** y marcas.
* **Ver detalles de un producto** con imágenes, precios y stock.  

## Usuarios
Podrás:
* **Registrar y autenticar usuarios** con seguridad JWT.
* **Gestionar perfiles y direcciones de envío**.
* **Administrar roles y permisos** (cliente, administrador).  

## Órdenes y Pagos
Incluye:
* **Creación de carritos y pedidos**.
* **Pagos contra entrega** y otros métodos configurables.
* **Gestión de estados de orden** y transacciones.  

## Envíos
Soporta:
* **Direcciones de envío registradas por el usuario**.
* **Integración con módulo de logística** (estado del envío, guía de entrega).  
"""

app = FastAPI(
    title="Cibercity API",
    description=description,
    summary="Plataforma backend modular para Cibercity E-commerce.",
    version="1.0.0-alpha.1",
    terms_of_service="https://cibercity.com/terms/",
    contact={
        "name": "Santiago Pinzon",
        "url": "https://cibercity.com/contact/",
        "email": "cibercitycolombia@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "identifier": "Apache-2.0",
    },
)


def create_schemas():
    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "auth"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "catalog"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "content"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "orders"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "payments"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "reviews"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "shipping"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "promotions"'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "support"'))

@app.on_event("startup")
def on_startup():
    create_schemas()
    Base.metadata.create_all(bind=engine)

# Routers public
app.include_router(account.router)
app.include_router(google_oauth.router)
app.include_router(catalog.router)
app.include_router(cart.router)

# Routers admin
app.include_router(catalog_adm.router)
app.include_router(orders.router)
app.include_router(auth.router)