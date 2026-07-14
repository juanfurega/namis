from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from namis.exceptions import ProductoNoEncontradoError, VentaInvalidaError
from namis.models.detalle_venta import DetalleVenta
from namis.models.producto import Producto
from namis.models.venta import Venta
from namis.schemas.ventas import (
    MEDIOS_COMUNICACION,
    MEDIOS_PAGO,
    ItemVentaInput,
    LineaVentaCalculada,
    PresupuestoVenta,
    VentaRegistrada,
)
from namis.services.clientes import obtener_o_crear_cliente
from namis.services.promociones import evaluar_promocion_aplicable
from namis.utils.money import money


def calcular_presupuesto_venta(
    session: Session,
    items: list[ItemVentaInput],
    *,
    costo_envio: Decimal = Decimal("0.00"),
) -> PresupuestoVenta:
    """
    Calcula el coste que debe pagar el cliente (sin persistir).
    Aplica automáticamente la mejor promoción activa que califique.
    """
    if not items:
        raise VentaInvalidaError("La venta debe incluir al menos un producto.")
    if costo_envio < 0:
        raise VentaInvalidaError("El costo de envío no puede ser negativo.")

    lineas: list[LineaVentaCalculada] = []
    for item in items:
        if item.cantidad <= 0:
            raise VentaInvalidaError(
                f"La cantidad del producto {item.id_producto} debe ser mayor a cero."
            )
        producto = session.get(Producto, item.id_producto)
        if producto is None:
            raise ProductoNoEncontradoError(item.id_producto)

        precio = producto.precio_actual
        subtotal = money(precio * item.cantidad)
        lineas.append(
            LineaVentaCalculada(
                id_producto=producto.id_producto,
                nombre_producto=producto.nombre_producto,
                cantidad=item.cantidad,
                precio_unitario=precio,
                costo_unitario=producto.costo_actual,
                subtotal=subtotal,
            )
        )

    subtotal_productos = money(sum((ln.subtotal for ln in lineas), Decimal("0.00")))
    envio = money(costo_envio)
    promocion = evaluar_promocion_aplicable(session, items, lineas)
    monto_descontado = promocion.monto_descontado if promocion else Decimal("0.00")

    return PresupuestoVenta(
        lineas=lineas,
        subtotal_productos=subtotal_productos,
        costo_envio=envio,
        monto_descontado=monto_descontado,
        total_cobrado=money(subtotal_productos - monto_descontado + envio),
        promocion=promocion,
    )


def registrar_venta(
    session: Session,
    *,
    nombre_cliente: str,
    items: list[ItemVentaInput],
    medio_pago: str | None = None,
    red_social: str | None = None,
    costo_envio: Decimal = Decimal("0.00"),
    fecha: datetime | None = None,
    observaciones: str | None = None,
) -> VentaRegistrada:
    """
    Registra una venta con uno o más productos.

    - red_social: medio de comunicación informativo (wsp / ig / msn).
    - medio_pago: informativo (efectivo / transferencia).
    - costo_envio: lo fija el usuario a mano; 0 = sin envío.
    - La promoción se detecta y aplica automáticamente si el carrito califica.
    """
    if medio_pago is not None:
        medio_pago = medio_pago.strip().lower()
        if medio_pago not in MEDIOS_PAGO:
            raise VentaInvalidaError(
                f"Medio de pago inválido '{medio_pago}'. Usá: {sorted(MEDIOS_PAGO)}."
            )

    if red_social is not None:
        red_social = red_social.strip().lower()
        if red_social not in MEDIOS_COMUNICACION:
            raise VentaInvalidaError(
                f"Medio de comunicación inválido '{red_social}'. "
                f"Usá: {sorted(MEDIOS_COMUNICACION)}."
            )

    presupuesto = calcular_presupuesto_venta(
        session,
        items,
        costo_envio=costo_envio,
    )
    cliente = obtener_o_crear_cliente(session, nombre_cliente)

    venta = Venta(
        id_cliente=cliente.id_cliente,
        fecha=fecha if fecha is not None else datetime.now(),
        medio_pago=medio_pago,
        red_social=red_social,
        requiere_envio=presupuesto.costo_envio > 0,
        costo_envio=presupuesto.costo_envio,
        id_promocion=presupuesto.promocion.id_promocion if presupuesto.promocion else None,
        monto_descontado=presupuesto.monto_descontado,
        total_cobrado=presupuesto.total_cobrado,
        observaciones=observaciones,
    )
    session.add(venta)
    session.flush()

    for linea in presupuesto.lineas:
        session.add(
            DetalleVenta(
                id_venta=venta.id_venta,
                id_producto=linea.id_producto,
                cantidad=linea.cantidad,
                precio_unitario_cobrado=linea.precio_unitario,
                costo_unitario_historico=linea.costo_unitario,
            )
        )
    session.flush()

    return VentaRegistrada(
        id_venta=venta.id_venta,
        id_cliente=cliente.id_cliente,
        nombre_cliente=cliente.nombre,
        fecha=venta.fecha or datetime.now(),
        medio_pago=venta.medio_pago,
        red_social=venta.red_social,
        costo_envio=presupuesto.costo_envio,
        monto_descontado=presupuesto.monto_descontado,
        total_cobrado=presupuesto.total_cobrado,
        promocion=presupuesto.promocion,
        lineas=presupuesto.lineas,
    )
