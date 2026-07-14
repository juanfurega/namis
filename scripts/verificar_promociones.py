"""Verifica descuentos por sets completos de promoción."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import select

from namis.database import session_scope
from namis.models.producto import Producto
from namis.schemas.ventas import ItemVentaInput
from namis.services.ventas import calcular_presupuesto_venta, registrar_venta

CASOS = {
    2: (0, 2000),
    3: (600, 2400),
    4: (600, 3400),
    6: (1200, 4800),
}


def main() -> int:
    with session_scope() as session:
        yogurt = session.scalar(
            select(Producto).where(Producto.nombre_producto == "Yogurt promo demo")
        )
        if yogurt is None:
            print("FALLO: no existe 'Yogurt promo demo'")
            return 1

        print("=== calcular_presupuesto_venta ===")
        ok = True
        for qty, (desc_esperado, total_esperado) in CASOS.items():
            p = calcular_presupuesto_venta(
                session,
                [ItemVentaInput(id_producto=yogurt.id_producto, cantidad=qty)],
            )
            desc = float(p.monto_descontado)
            total = float(p.total_cobrado)
            match = desc == desc_esperado and total == total_esperado
            ok = ok and match
            estado = "OK" if match else "FALLO"
            print(
                f"{estado} qty={qty} descuento={desc} (esp {desc_esperado}) "
                f"total={total} (esp {total_esperado})"
            )

        venta = registrar_venta(
            session,
            nombre_cliente="Verificacion promo",
            items=[ItemVentaInput(id_producto=yogurt.id_producto, cantidad=6)],
            medio_pago="efectivo",
            red_social="wsp",
        )
        v_ok = float(venta.monto_descontado) == 1200 and float(venta.total_cobrado) == 4800
        print("=== registrar_venta (6 unidades) ===")
        print(
            f"{'OK' if v_ok else 'FALLO'} venta #{venta.id_venta} "
            f"descuento={venta.monto_descontado} total={venta.total_cobrado}"
        )

        if ok and v_ok:
            print("=== RESULTADO: TODO OK ===")
            return 0
        print("=== RESULTADO: HAY FALLOS ===")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
