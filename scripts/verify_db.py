"""
Verifica modelos SQLAlchemy con MySQL o, en modo --sqlite, una BD SQLite temporal.

MySQL (ejemplo con docker-compose de este repo):
  set DATABASE_URL=mysql+pymysql://namis:namis_secret@127.0.0.1:3307/namis_yogur?charset=utf8mb4
  python scripts/verify_db.py

SQLite (sin servidor; crea tablas con metadata del ORM):
  python scripts/verify_db.py --sqlite
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from sqlalchemy import create_engine, inspect, select, text  # noqa: E402
    from sqlalchemy.exc import OperationalError  # noqa: E402
    from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
except ModuleNotFoundError as e:
    req = ROOT / "requirements.txt"
    print(
        "Faltan dependencias (p. ej. SQLAlchemy). Desde la raiz del proyecto ejecuta:\n"
        f"  python -m pip install -r {req}\n"
        "O crea un venv, activalo y vuelve a instalar.",
        file=sys.stderr,
    )
    raise SystemExit(1) from e

from namis.config import DATABASE_URL  # noqa: E402
from namis.database import engine as mysql_engine, session_scope as mysql_session_scope  # noqa: E402
from namis.models import Base, Cliente  # noqa: E402

EXPECTED_TABLES = frozenset(
    {"clientes", "productos", "promociones", "ventas", "detalle_ventas", "insumos", "recetas"}
)


def _redacted_url(url: str) -> str:
    if "@" not in url:
        return url
    scheme, rest = url.split("://", 1)
    tail = rest.split("@", 1)[-1]
    return f"{scheme}://***@{tail}"


def _crud_cliente(session_scope_ctx, tag: str) -> None:
    with session_scope_ctx() as session:
        cliente = Cliente(nombre=tag)
        session.add(cliente)
        session.flush()
        cid = cliente.id_cliente

    with session_scope_ctx() as session:
        found = session.scalars(select(Cliente).where(Cliente.nombre == tag)).one()
        assert found.id_cliente == cid
        session.delete(found)


def run_sqlite_verify_impl() -> int:
    from contextlib import contextmanager

    db_path = ROOT / ".verify_namis.sqlite"
    url = f"sqlite:///{db_path.as_posix()}"
    print("Modo SQLite:", db_path.name, "(se borra al terminar)")

    if db_path.exists():
        db_path.unlink()

    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    @contextmanager
    def session_scope_sqlite():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    tag = f"__verify_{uuid.uuid4().hex[:10]}__"
    _crud_cliente(session_scope_sqlite, tag)

    engine.dispose()
    db_path.unlink(missing_ok=True)
    print("OK: SQLite - tablas creadas desde ORM y CRUD Cliente OK.")
    return 0


def run_mysql_verify() -> int:
    url = os.environ.get("DATABASE_URL", DATABASE_URL)
    print("Probando:", _redacted_url(url))

    try:
        with mysql_engine.connect() as conn:
            assert conn.scalar(text("SELECT 1")) == 1
    except OperationalError as e:
        print("ERROR: no se pudo conectar al servidor MySQL.")
        print(e.orig if hasattr(e, "orig") else e)
        print(
            "Sugerencia: levanta la base con `docker compose up -d` en la raiz del proyecto "
            "y exporta DATABASE_URL (puerto 3307, usuario namis, BD namis_yogur). "
            "O ejecuta `python scripts/verify_db.py --sqlite` para probar solo el ORM."
        )
        return 1

    insp = inspect(mysql_engine)
    tables = set(insp.get_table_names())
    missing = EXPECTED_TABLES - tables
    if missing:
        print("ERROR: faltan tablas en la base:", sorted(missing))
        print("Tablas vistas:", sorted(tables))
        return 1

    tag = f"__verify_{uuid.uuid4().hex[:10]}__"
    _crud_cliente(mysql_session_scope, tag)

    print("OK: MySQL - conexion, tablas y ORM (Cliente insert/select/delete) funcionaron.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica SQLAlchemy / MySQL o SQLite.")
    parser.add_argument(
        "--sqlite",
        action="store_true",
        help="Usar SQLite temporal y create_all (no requiere MySQL).",
    )
    args = parser.parse_args()
    if args.sqlite:
        return run_sqlite_verify_impl()
    return run_mysql_verify()


if __name__ == "__main__":
    raise SystemExit(main())
