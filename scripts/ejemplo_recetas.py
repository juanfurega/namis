"""
Ejemplo: yogurth (insumos) usado dentro de postre (sub-receta + insumos).

  python scripts/ejemplo_recetas.py
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from namis.database import session_scope
from namis.services.insumos import crear_insumo, registrar_compra_insumo
from namis.services.productos import crear_producto
from namis.services.recetas import (
    agregar_insumo_a_receta,
    agregar_producto_a_receta,
    obtener_receta,
)


def main() -> None:
    with session_scope() as session:
        leche = crear_insumo(session, "Leche para receta", "ml")
        granola = crear_insumo(session, "Granola", "gramos")
        registrar_compra_insumo(session, leche.id_insumo, Decimal("1000"), Decimal("1000.00"))
        registrar_compra_insumo(session, granola.id_insumo, Decimal("500"), Decimal("2500.00"))

        yogurth = crear_producto(
            session,
            "Yogurth natural 350g",
            precio_actual=Decimal("2500.00"),
            tamano_g=350,
            es_endulzado=False,
        )
        agregar_insumo_a_receta(session, yogurth.id_producto, leche.id_insumo, Decimal("350"))

        postre = crear_producto(
            session,
            "Postre con granola",
            precio_actual=Decimal("4000.00"),
            tamano_g=400,
        )
        agregar_producto_a_receta(session, postre.id_producto, yogurth.id_producto, Decimal("1"))
        agregar_insumo_a_receta(session, postre.id_producto, granola.id_insumo, Decimal("50"))

        print("--- Receta yogurth ---")
        r_y = obtener_receta(session, yogurth.id_producto)
        for ln in r_y.lineas:
            print(f"  {ln.tipo}: {ln.nombre_componente} x {ln.cantidad_necesaria} -> ${ln.costo_linea}")
        print(f"  Costo total: ${r_y.costo_total} (guardado: {yogurth.costo_actual})")

        print("--- Receta postre (incluye yogurth) ---")
        r_p = obtener_receta(session, postre.id_producto)
        for ln in r_p.lineas:
            print(f"  {ln.tipo}: {ln.nombre_componente} x {ln.cantidad_necesaria} -> ${ln.costo_linea}")
        print(f"  Costo total: ${r_p.costo_total} (guardado: {postre.costo_actual})")


if __name__ == "__main__":
    main()
