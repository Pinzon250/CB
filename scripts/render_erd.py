from pathlib import Path
import sys, os, shutil

ROOT = Path(__file__).resolve().parents[1]  # carpeta del repo (cb/)
sys.path.insert(0, str(ROOT))               # hace importable 'app'

# 1) Carga Base y registra TODOS los modelos
from app.database.base import Base
from app.database import models as _models  # noqa: F401  # fuerza import de modelos

# 2) Se obtiene un SQLAlchemy Engine 
engine = None
try:
    # si ya tienes engine en tu código (ajusta el path según tu proyecto)
    from app.database.session import engine as _engine  # p.ej. session.py
    engine = _engine
except Exception:
    try:
        from app.database.session import engine as _engine  # alternativa
        engine = _engine
    except Exception:
        from sqlalchemy import create_engine
        DATABASE_URL = (
            os.getenv("DATABASE_URL")
            or os.getenv("SQLALCHEMY_DATABASE_URI")
            or "postgresql+psycopg2://user:password@localhost:5432/cibercity"
        )
        engine = create_engine(DATABASE_URL)

# 3) Diagnósticos útiles
print("🧪 Tablas en Base.metadata:", len(Base.metadata.tables))
print("   Ejemplos:", list(Base.metadata.tables.keys())[:8])
print("🧪 dot.exe:", shutil.which("dot") or "NO ENCONTRADO (instala Graphviz)")

# 4) Generar el diagrama
from sqlalchemy_schemadisplay import create_schema_graph

graph = create_schema_graph(
    metadata=Base.metadata,
    engine=engine,           
    show_datatypes=False,
    show_indexes=False,
    rankdir="LR",
    concentrate=False,
)
out = ROOT / "erd_from_models.png"
graph.write_png(out.as_posix())
print(f"✅ ERD generado: {out}")
