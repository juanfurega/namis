"""
Ejemplo: registrar una venta con varios productos, envío y medios informativos.

  python scripts/ejemplo_ventas.py
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from namis.database import session_scope
from namis.schemas.ventas import ItemVentaInput
from namis.services.productos import crear_producto
from namis.services.ventas import calcular_presupuesto_venta, registrar_venta


def main() -> None:
    with session_scope() as session:
        p1 = crear_producto(session, "Pote demo A", Decimal("2000.00"))
        p2 = crear_producto(session, "Pote demo B", Decimal("2500.00"))

        items = [
            ItemVentaInput(id_producto=p1.id_producto, cantidad=2),
            ItemVentaInput(id_producto=p2.id_producto, cantidad=1),
        ]

        presupuesto = calcular_presupuesto_venta(
            session,
            items,
            costo_envio=Decimal("500.00"),
        )
        print("Presupuesto (antes de guardar):")
        for ln in presupuesto.lineas:
            print(f"  {ln.nombre_producto} x{ln.cantidad} @ {ln.precio_unitario} = {ln.subtotal}")
        print(f"  Envío: {presupuesto.costo_envio}")
        if presupuesto.monto_descontado > 0 and presupuesto.promocion:
            print(f"  Promo: {presupuesto.promocion.nombre_promocion} (-{presupuesto.monto_descontado})")
        print(f"  TOTAL a cobrar: {presupuesto.total_cobrado}")

        venta = registrar_venta(
            session,
            nombre_cliente="Ana Pérez",
            items=items,
            medio_pago="transferencia",
            red_social="wsp",
            costo_envio=Decimal("500.00"),
        )
        print(f"\nVenta #{venta.id_venta} registrada para {venta.nombre_cliente}")
        print(f"  Canal: {venta.red_social} | Pago: {venta.medio_pago}")
        print(f"  Total cobrado: {venta.total_cobrado}")


if __name__ == "__main__":
    main()
