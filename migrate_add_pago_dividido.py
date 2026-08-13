"""Agrega importes de efectivo y transferencia a las ventas existentes."""

import os
from pathlib import Path
import tomllib

import pymysql
from dotenv import load_dotenv
from sqlalchemy.engine import make_url


raiz = Path(__file__).resolve().parent
secrets_path = raiz / ".streamlit" / "secrets.toml"

if secrets_path.exists():
    with secrets_path.open("rb") as secrets_file:
        mysql = tomllib.load(secrets_file)["mysql"]
    host = mysql["host"]
    puerto = int(mysql["port"])
    usuario = mysql["user"]
    contrasena = mysql["password"]
    base = mysql["database"]
else:
    load_dotenv(raiz / ".env")
    url = make_url(os.environ["DATABASE_URL"])
    host = url.host
    puerto = url.port or 3306
    usuario = url.username
    contrasena = url.password
    base = url.database

conexion = pymysql.connect(
    host=host,
    port=puerto,
    user=usuario,
    password=contrasena,
    database=base,
)

try:
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'ventas'
              AND COLUMN_NAME IN ('monto_efectivo', 'monto_transferencia')
            """,
            (base,),
        )
        existentes = {fila[0] for fila in cursor.fetchall()}
        if "monto_efectivo" not in existentes:
            cursor.execute("ALTER TABLE ventas ADD COLUMN monto_efectivo DECIMAL(10, 2) NULL")
        if "monto_transferencia" not in existentes:
            cursor.execute("ALTER TABLE ventas ADD COLUMN monto_transferencia DECIMAL(10, 2) NULL")

        cursor.execute(
            """
            UPDATE ventas
            SET monto_efectivo = CASE WHEN medio_pago = 'efectivo' THEN total_cobrado ELSE 0.00 END,
                monto_transferencia = CASE WHEN medio_pago = 'transferencia' THEN total_cobrado ELSE 0.00 END
            WHERE monto_efectivo IS NULL OR monto_transferencia IS NULL
            """
        )
    conexion.commit()
    print("Migración de pago dividido completada.")
finally:
    conexion.close()
