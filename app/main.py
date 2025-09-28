from fastapi import FastAPI
from sqlalchemy import text
from app.database.session import engine
from app.database.base import Base

from app.database.models import *

# Routers fastapi
from app.api.v1.storefront import *

# admin routers
from app.api.v1.admin import catalog as catalog_adm
from app.api.v1.admin import auth

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

# Inicializacion de fastapi
app = FastAPI(
    title="Cibercity API v1.0.0-alpha.1",
    description=description,
    summary="Deadpool's favorite app. Nuff said.",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Santiago Pinzon",
        "url": "http://x-force.example.com/contact/",
        "email": "cibercitycolombia@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
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

# Routers admin
app.include_router(catalog_adm.router)
app.include_router(auth.router)