"""
Ejemplo de uso de servicios de materia prima.

  python scripts/ejemplo_insumos.py
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from namis.database import session_scope
from namis.services.insumos import (
    crear_insumo,
    listar_insumos_actuales,
    obtener_precio_vigente_insumo,
    registrar_compra_insumo,
)


def main() -> None:
    with session_scope() as session:
        insumo = crear_insumo(session, "Leche entera", "ml")
        compra = registrar_compra_insumo(
            session,
            insumo.id_insumo,
            cantidad=Decimal("1000"),
            precio_pagado=Decimal("850.00"),
        )
        vigente = obtener_precio_vigente_insumo(session, insumo.id_insumo)

        print("Insumo creado:", insumo.id_insumo, insumo.nombre_insumo)
        print("Compra registrada:", compra.id_historial)
        print("Productos con costo actualizado:", compra.productos_costo_actualizado)
        print("Precio unitario vigente:", vigente.precio_unitario)

        for item in listar_insumos_actuales(session):
            pv = item.precio_vigente
            precio = f"{pv.precio_paquete} / {pv.cantidad_paquete}" if pv else "sin compras"
            print(f"- {item.nombre_insumo} ({item.unidad_medida}): {precio}")


if __name__ == "__main__":
    main()
