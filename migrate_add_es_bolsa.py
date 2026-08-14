"""Agrega la marca de bolsa a los insumos existentes."""

from pathlib import Path
import tomllib

import pymysql


raiz = Path(__file__).resolve().parent
with (raiz / ".streamlit" / "secrets.toml").open("rb") as secrets_file:
    mysql = tomllib.load(secrets_file)["mysql"]

conexion = pymysql.connect(
    host=mysql["host"],
    port=int(mysql["port"]),
    user=mysql["user"],
    password=mysql["password"],
    database=mysql["database"],
)

try:
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'insumos' AND COLUMN_NAME = 'es_bolsa'
            """,
            (mysql["database"],),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE insumos ADD COLUMN es_bolsa BOOLEAN NOT NULL DEFAULT FALSE"
            )
    conexion.commit()
    print("Migración de bolsa completada.")
finally:
    conexion.close()
