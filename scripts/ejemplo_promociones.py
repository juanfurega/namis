"""
Ejemplo: promoción 3 yogurts con 20% de descuento, aplicada automáticamente.

  python scripts/ejemplo_promociones.py
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from namis.database import session_scope
from namis.schemas.promociones import RequisitoPromocionInput
from namis.schemas.ventas import ItemVentaInput
from namis.services.productos import crear_producto
from namis.services.promociones import crear_promocion
from namis.services.ventas import calcular_presupuesto_venta, registrar_venta


def main() -> None:
    with session_scope() as session:
        yogurt = crear_producto(session, "Yogurt promo demo", Decimal("1000.00"))

        promo = crear_promocion(
            session,
            "3 yogurts 20% off",
            Decimal("20.00"),
            [RequisitoPromocionInput(id_producto=yogurt.id_producto, cantidad_requerida=3)],
        )
        print(f"Promoción creada: {promo.nombre_promocion} ({promo.descuento_porcentaje}%)")

        for qty in [2, 3, 4, 5, 6]:
            p = calcular_presupuesto_venta(
                session,
                [ItemVentaInput(id_producto=yogurt.id_producto, cantidad=qty)],
            )
            promo_txt = p.promocion.nombre_promocion if p.promocion else "ninguna"
            print(
                f"{qty} yogurts -> subtotal {p.subtotal_productos}, "
                f"descuento {p.monto_descontado}, total {p.total_cobrado} ({promo_txt})"
            )


if __name__ == "__main__":
    main()
