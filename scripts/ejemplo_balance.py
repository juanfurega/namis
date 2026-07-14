"""
Ejemplo: balance diario agrupado por cliente.

  python scripts/ejemplo_balance.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from namis.database import session_scope
from namis.services.balance import (
    listar_historial_dia_por_cliente,
    obtener_detalle_venta,
    obtener_resumen_dia,
    obtener_resumen_mes_calendario,
)
from namis.models.venta import Venta
from sqlalchemy import select


def main() -> None:
    with session_scope() as session:
        hoy = date.today()
        resumen = obtener_resumen_dia(session, hoy)
        print(f"=== Ganancia del dia {resumen.fecha} ===")
        print(f"Ventas: {resumen.cantidad_ventas}")
        print(f"Total cobrado: ${resumen.total_cobrado}")
        print(f"Ganancia: ${resumen.total_ganancia}")

        historial = listar_historial_dia_por_cliente(session, hoy)
        if historial.clientes:
            print(f"\n=== Historial por cliente ===")
            for cliente in historial.clientes:
                print(f"\n{cliente.nombre_cliente}")
                print(f"  Total cliente: cobrado ${cliente.total_cobrado} | ganancia ${cliente.total_ganancia}")
                for v in cliente.ventas:
                    promo = v.nombre_promocion or "sin promo"
                    print(
                        f"  Venta #{v.id_venta} | bruto ${v.subtotal_bruto} "
                        f"| desc ${v.monto_descontado} | envio ${v.costo_envio} "
                        f"| cobrado ${v.total_cobrado} | ganancia ${v.ganancia} | {promo}"
                    )
                    for ln in v.lineas:
                        print(
                            f"    - {ln.nombre_producto} x{ln.cantidad} "
                            f"@ ${ln.precio_unitario_cobrado}"
                        )

        cal = obtener_resumen_mes_calendario(session, hoy.year, hoy.month)
        print(f"\n=== Calendario {cal.mes}/{cal.anio} ===")
        print(f"Ganancia mensual: ${cal.total_ganancia} ({cal.cantidad_ventas} ventas)")

        ultima = session.scalar(select(Venta.id_venta).order_by(Venta.id_venta.desc()).limit(1))
        if ultima:
            det = obtener_detalle_venta(session, ultima)
            print(f"\n=== Detalle venta #{det.venta.id_venta} ===")
            print(f"Cliente: {det.nombre_cliente}")
            print(f"Promo: {det.venta.nombre_promocion or '-'}")
            print(f"Ganancia: ${det.venta.ganancia}")


if __name__ == "__main__":
    main()
