"""
Comprueba que la base namis_yogur (u otra URL) tiene las tablas esperadas según schema.sql.

Uso:
  set DATABASE_URL=mysql+pymysql://usuario:clave@127.0.0.1:3307/namis_yogur?charset=utf8mb4
  python scripts/check_db_tables.py

Si no existe .env ni DATABASE_URL, intenta valores por defecto del docker-compose del repo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from sqlalchemy import inspect, text, create_engine
    from sqlalchemy.exc import OperationalError
except ModuleNotFoundError as e:
    print(
        "Instala dependencias: python -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1) from e


EXPECTED = frozenset(
    {"clientes", "productos", "promociones", "ventas", "detalle_ventas", "insumos", "recetas"}
)

DEFAULT_FALLBACK = (
    "mysql+pymysql://namis:namis_secret@127.0.0.1:3307/namis_yogur?charset=utf8mb4"
)


def main() -> int:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    from namis.config import DATABASE_URL as cfg_url

    url = (os.environ.get("DATABASE_URL") or cfg_url).strip()
    if not url or "user:password@" in url:
        url = DEFAULT_FALLBACK

    engine = create_engine(url, pool_pre_ping=True)

    print("URL (sin contraseña):", _redacted(url))

    try:
        with engine.connect() as conn:
            name = conn.execute(text("SELECT DATABASE()")).scalar()
            ver = conn.execute(text("SELECT VERSION()")).scalar()
            print(f"BD actual: {name}")
            print(f"MySQL/MariaDB: {ver}")

        insp = inspect(engine)
        found = frozenset(insp.get_table_names())
    except OperationalError as e:
        print("ERROR: no se pudo conectar.", file=sys.stderr)
        print(e.orig if getattr(e, "orig", None) else e, file=sys.stderr)
        print(
            "\nAsegúrate de tener el servidor activo "
            "(p. ej. docker compose up -d en la raíz del proyecto) "
            "y DATABASE_URL correcto en .env.",
            file=sys.stderr,
        )
        return 1

    missing = sorted(EXPECTED - found)
    extra = sorted(found - EXPECTED)

    print("\nTablas en la BD:", sorted(found))
    if not missing and not extra:
        print("\nOK: las 7 tablas esperadas coinciden con schema.sql.")
        return 0

    if missing:
        print("\nFaltan:", missing)
    if extra:
        print("\nExtras (no en schema esperado):", extra)
    return 2


def _redacted(url: str) -> str:
    if "@" not in url:
        return url
    scheme, rest = url.split("://", 1)
    tail = rest.split("@", 1)[-1]
    return f"{scheme}://***@{tail}"


if __name__ == "__main__":
    raise SystemExit(main())
