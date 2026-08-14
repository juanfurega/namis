"""Crea el detalle histórico de bolsas utilizadas en cada venta."""

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
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'detalle_bolsas_venta'
            """,
            (mysql["database"],),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE detalle_bolsas_venta (
                    id_detalle_bolsa INT AUTO_INCREMENT PRIMARY KEY,
                    id_venta INT NOT NULL,
                    id_insumo INT NULL,
                    cantidad INT NOT NULL,
                    precio_unitario_historico DECIMAL(10, 2) NOT NULL,
                    costo_total DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
                    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) ON DELETE SET NULL
                )
                """
            )
    conexion.commit()
    print("Migración de detalle de bolsas completada.")
finally:
    conexion.close()
