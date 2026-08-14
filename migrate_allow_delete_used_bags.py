"""Permite eliminar una bolsa sin borrar su costo histórico de las ventas."""

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
            SELECT kcu.CONSTRAINT_NAME, rc.DELETE_RULE, columns_info.IS_NULLABLE
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu
            JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS AS rc
              ON rc.CONSTRAINT_SCHEMA = kcu.CONSTRAINT_SCHEMA
             AND rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
             AND rc.TABLE_NAME = kcu.TABLE_NAME
            JOIN INFORMATION_SCHEMA.COLUMNS AS columns_info
              ON columns_info.TABLE_SCHEMA = kcu.TABLE_SCHEMA
             AND columns_info.TABLE_NAME = kcu.TABLE_NAME
             AND columns_info.COLUMN_NAME = kcu.COLUMN_NAME
            WHERE kcu.TABLE_SCHEMA = %s
              AND kcu.TABLE_NAME = 'detalle_bolsas_venta'
              AND kcu.COLUMN_NAME = 'id_insumo'
              AND kcu.REFERENCED_TABLE_NAME = 'insumos'
            """,
            (mysql["database"],),
        )
        referencias = cursor.fetchall()

        if not referencias:
            raise RuntimeError(
                "No se encontró la referencia de detalle_bolsas_venta a insumos."
            )

        if not all(
            regla_borrado == "SET NULL" and permite_null == "YES"
            for _, regla_borrado, permite_null in referencias
        ):
            for nombre_restriccion, _, _ in referencias:
                nombre_seguro = nombre_restriccion.replace("`", "``")
                cursor.execute(
                    f"ALTER TABLE detalle_bolsas_venta "
                    f"DROP FOREIGN KEY `{nombre_seguro}`"
                )

            cursor.execute(
                "ALTER TABLE detalle_bolsas_venta MODIFY id_insumo INT NULL"
            )
            cursor.execute(
                """
                ALTER TABLE detalle_bolsas_venta
                ADD CONSTRAINT fk_detalle_bolsas_insumo
                FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo)
                ON DELETE SET NULL
                """
            )

    conexion.commit()
    print("Migración para eliminar bolsas utilizadas completada.")
finally:
    conexion.close()
