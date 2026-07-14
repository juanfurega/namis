from __future__ import annotations

import calendar
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from namis.exceptions import VentaNoEncontradaError
from namis.models.detalle_venta import DetalleVenta
from namis.models.venta import Venta
from namis.schemas.balance import (
    ClienteHistorialDia,
    DiaCalendario,
    HistorialDiaPorCliente,
    LineaVentaHistorial,
    ResumenDia,
    ResumenMesCalendario,
    VentaHistorialConCliente,
    VentaHistorialDetalle,
)
from namis.utils.money import money


def _metricas_venta(venta: Venta) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    subtotal_bruto = Decimal("0.00")
    costo_productos = Decimal("0.00")
    for det in venta.detalles:
        subtotal_bruto += det.precio_unitario_cobrado * det.cantidad
        costo_productos += det.costo_unitario_historico * det.cantidad

    subtotal_bruto = money(subtotal_bruto)
    costo_productos = money(costo_productos)
    total_cobrado = money(venta.total_cobrado)
    ganancia = money(total_cobrado - costo_productos)
    return subtotal_bruto, costo_productos, total_cobrado, ganancia


def _a_historial(venta: Venta) -> VentaHistorialDetalle:
    subtotal_bruto, costo_productos, total_cobrado, ganancia = _metricas_venta(venta)
    lineas = [
        LineaVentaHistorial(
            id_detalle=d.id_detalle,
            id_producto=d.id_producto,
            nombre_producto=d.producto.nombre_producto,
            cantidad=d.cantidad,
            precio_unitario_cobrado=d.precio_unitario_cobrado,
            costo_unitario_historico=d.costo_unitario_historico,
            subtotal_cobrado=money(d.precio_unitario_cobrado * d.cantidad),
            subtotal_costo=money(d.costo_unitario_historico * d.cantidad),
        )
        for d in venta.detalles
    ]
    promo = venta.promocion
    return VentaHistorialDetalle(
        id_venta=venta.id_venta,
        id_cliente=venta.id_cliente,
        fecha=venta.fecha or datetime.now(),
        medio_pago=venta.medio_pago,
        red_social=venta.red_social,
        nombre_promocion=promo.nombre_promocion if promo else None,
        descuento_porcentaje=promo.descuento_porcentaje if promo else None,
        monto_descontado=money(venta.monto_descontado),
        costo_envio=money(venta.costo_envio or Decimal("0.00")),
        subtotal_bruto=subtotal_bruto,
        total_cobrado=total_cobrado,
        costo_productos=costo_productos,
        ganancia=ganancia,
        lineas=lineas,
    )


def _cargar_venta(session: Session, id_venta: int) -> Venta:
    venta = session.scalar(
        select(Venta)
        .where(Venta.id_venta == id_venta)
        .options(
            selectinload(Venta.cliente),
            selectinload(Venta.promocion),
            selectinload(Venta.detalles).selectinload(DetalleVenta.producto),
        )
    )
    if venta is None:
        raise VentaNoEncontradaError(id_venta)
    return venta


def _ventas_en_rango(session: Session, desde: date, hasta: date) -> list[Venta]:
    return list(
        session.scalars(
            select(Venta)
            .where(
                func.date(Venta.fecha) >= desde,
                func.date(Venta.fecha) <= hasta,
            )
            .options(
                selectinload(Venta.cliente),
                selectinload(Venta.promocion),
                selectinload(Venta.detalles).selectinload(DetalleVenta.producto),
            )
            .order_by(Venta.fecha.desc(), Venta.id_venta.desc())
        ).all()
    )


def _agrupar_ventas_por_cliente(
    ventas: list[VentaHistorialDetalle],
    nombres: dict[int, str],
) -> list[ClienteHistorialDia]:
    por_cliente: dict[int, list[VentaHistorialDetalle]] = {}
    for v in ventas:
        por_cliente.setdefault(v.id_cliente, []).append(v)

    clientes: list[ClienteHistorialDia] = []
    for id_cliente, ventas_cliente in por_cliente.items():
        total_cobrado = money(sum((v.total_cobrado for v in ventas_cliente), Decimal("0.00")))
        total_ganancia = money(sum((v.ganancia for v in ventas_cliente), Decimal("0.00")))
        clientes.append(
            ClienteHistorialDia(
                id_cliente=id_cliente,
                nombre_cliente=nombres[id_cliente],
                ventas=ventas_cliente,
                total_cobrado=total_cobrado,
                total_ganancia=total_ganancia,
            )
        )

    return sorted(clientes, key=lambda c: c.nombre_cliente.lower())


def obtener_detalle_venta(session: Session, id_venta: int) -> VentaHistorialConCliente:
    venta_orm = _cargar_venta(session, id_venta)
    return VentaHistorialConCliente(
        id_cliente=venta_orm.id_cliente,
        nombre_cliente=venta_orm.cliente.nombre,
        venta=_a_historial(venta_orm),
    )


def listar_historial_ventas_dia(
    session: Session,
    fecha: date,
) -> list[VentaHistorialDetalle]:
    """Lista plana de ventas del día (compatibilidad)."""
    ventas = _ventas_en_rango(session, fecha, fecha)
    return [_a_historial(v) for v in ventas]


def listar_historial_dia_por_cliente(
    session: Session,
    fecha: date,
) -> HistorialDiaPorCliente:
    """
    Historial del día agrupado por cliente: nombre del cliente y,
    debajo, el detalle de cada venta asociada.
    """
    ventas_orm = _ventas_en_rango(session, fecha, fecha)
    ventas = [_a_historial(v) for v in ventas_orm]
    nombres = {v.id_cliente: v.cliente.nombre for v in ventas_orm}
    clientes = _agrupar_ventas_por_cliente(ventas, nombres)
    return HistorialDiaPorCliente(fecha=fecha, clientes=clientes)


def obtener_resumen_dia(session: Session, fecha: date) -> ResumenDia:
    ventas = _ventas_en_rango(session, fecha, fecha)
    total_cobrado = Decimal("0.00")
    total_ganancia = Decimal("0.00")
    for v in ventas:
        _, _, cobrado, ganancia = _metricas_venta(v)
        total_cobrado += cobrado
        total_ganancia += ganancia
    return ResumenDia(
        fecha=fecha,
        cantidad_ventas=len(ventas),
        total_cobrado=money(total_cobrado),
        total_ganancia=money(total_ganancia),
    )


def obtener_resumen_mes_calendario(
    session: Session,
    anio: int,
    mes: int,
) -> ResumenMesCalendario:
    """
    Vista tipo calendario: ganancia por día del mes y totales mensuales.
    """
    if mes < 1 or mes > 12:
        raise ValueError("El mes debe estar entre 1 y 12.")

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    desde = date(anio, mes, 1)
    hasta = date(anio, mes, ultimo_dia)
    ventas = _ventas_en_rango(session, desde, hasta)

    ganancia_por_dia: dict[date, Decimal] = {}
    ventas_por_dia: dict[date, int] = {}

    total_cobrado = Decimal("0.00")
    total_ganancia = Decimal("0.00")

    for v in ventas:
        if v.fecha is None:
            continue
        dia = v.fecha.date()
        _, _, cobrado, ganancia = _metricas_venta(v)
        ganancia_por_dia[dia] = ganancia_por_dia.get(dia, Decimal("0.00")) + ganancia
        ventas_por_dia[dia] = ventas_por_dia.get(dia, 0) + 1
        total_cobrado += cobrado
        total_ganancia += ganancia

    dias: list[DiaCalendario] = []
    for d in range(1, ultimo_dia + 1):
        f = date(anio, mes, d)
        g = money(ganancia_por_dia.get(f, Decimal("0.00")))
        n = ventas_por_dia.get(f, 0)
        dias.append(
            DiaCalendario(
                fecha=f,
                cantidad_ventas=n,
                total_ganancia=g,
                tiene_ventas=n > 0,
            )
        )

    return ResumenMesCalendario(
        anio=anio,
        mes=mes,
        dias=dias,
        total_cobrado=money(total_cobrado),
        total_ganancia=money(total_ganancia),
        cantidad_ventas=len(ventas),
    )
