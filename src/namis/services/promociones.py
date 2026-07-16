from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from namis.exceptions import (
    ProductoNoEncontradoError,
    PromocionInvalidaError,
    PromocionNoEncontradaError,
)
from namis.models.producto import Producto
from namis.models.promocion import Promocion
from namis.models.promocion_requisito import PromocionRequisito
from namis.schemas.promociones import (
    PromocionAplicada,
    PromocionDetalle,
    RequisitoPromocionDetalle,
    RequisitoPromocionInput,
)
from namis.schemas.ventas import ItemVentaInput, LineaVentaCalculada
from namis.utils.money import money


def crear_promocion(
    session: Session,
    nombre_promocion: str,
    descuento_porcentaje: Decimal,
    requisitos: list[RequisitoPromocionInput],
    *,
    activa: bool = True,
) -> PromocionDetalle:
    nombre = nombre_promocion.strip()
    if not nombre:
        raise PromocionInvalidaError("El nombre de la promoción no puede estar vacío.")
    if not requisitos:
        raise PromocionInvalidaError("La promoción debe incluir al menos un producto.")

    if not isinstance(descuento_porcentaje, Decimal):
        descuento_porcentaje = Decimal(descuento_porcentaje)
    if descuento_porcentaje <= 0 or descuento_porcentaje > 100:
        raise PromocionInvalidaError("El descuento debe ser mayor a 0 y hasta 100%.")

    ids_vistos: set[int] = set()
    for req in requisitos:
        if req.cantidad_requerida <= 0:
            raise PromocionInvalidaError(
                f"La cantidad requerida del producto {req.id_producto} debe ser mayor a cero."
            )
        if req.id_producto in ids_vistos:
            raise PromocionInvalidaError(
                f"El producto {req.id_producto} está repetido en los requisitos."
            )
        if session.get(Producto, req.id_producto) is None:
            raise ProductoNoEncontradoError(req.id_producto)
        ids_vistos.add(req.id_producto)

    promocion = Promocion(
        nombre_promocion=nombre,
        descuento_porcentaje=descuento_porcentaje,
        activa=activa,
    )
    session.add(promocion)
    session.flush()

    for req in requisitos:
        session.add(
            PromocionRequisito(
                id_promocion=promocion.id_promocion,
                id_producto=req.id_producto,
                cantidad_requerida=req.cantidad_requerida,
            )
        )
    session.flush()

    return obtener_promocion(session, promocion.id_promocion)


def obtener_promocion(session: Session, id_promocion: int) -> PromocionDetalle:
    promocion = session.scalar(
        select(Promocion)
        .where(Promocion.id_promocion == id_promocion)
        .options(selectinload(Promocion.requisitos).selectinload(PromocionRequisito.producto))
    )
    if promocion is None:
        raise PromocionNoEncontradaError(id_promocion)
    return _a_detalle(promocion)


def listar_promociones(session: Session, *, solo_activas: bool = False) -> list[PromocionDetalle]:
    stmt = select(Promocion).options(
        selectinload(Promocion.requisitos).selectinload(PromocionRequisito.producto)
    )
    if solo_activas:
        stmt = stmt.where(Promocion.activa.is_(True))
    promociones = session.scalars(stmt.order_by(Promocion.nombre_promocion)).all()
    return [_a_detalle(p) for p in promociones]


def eliminar_promocion(session: Session, id_promocion: int) -> None:
    """Elimina una promoción y sus requisitos."""
    promocion = session.get(Promocion, id_promocion)
    if promocion is None:
        raise PromocionNoEncontradaError(id_promocion)
    
    # Eliminar requisitos primero
    for requisito in promocion.requisitos:
        session.delete(requisito)
    
    # Eliminar promoción
    session.delete(promocion)
    session.flush()


def _a_detalle(promocion: Promocion) -> PromocionDetalle:
    requisitos = [
        RequisitoPromocionDetalle(
            id_requisito=r.id_requisito,
            id_producto=r.id_producto,
            nombre_producto=r.producto.nombre_producto,
            cantidad_requerida=r.cantidad_requerida,
        )
        for r in promocion.requisitos
    ]
    return PromocionDetalle(
        id_promocion=promocion.id_promocion,
        nombre_promocion=promocion.nombre_promocion,
        descuento_porcentaje=promocion.descuento_porcentaje,
        activa=promocion.activa,
        requisitos=requisitos,
    )


def _cantidades_carrito(items: list[ItemVentaInput]) -> dict[int, int]:
    cantidades: dict[int, int] = {}
    for item in items:
        cantidades[item.id_producto] = cantidades.get(item.id_producto, 0) + item.cantidad
    return cantidades


def _promocion_califica(promocion: Promocion, cantidades: dict[int, int]) -> bool:
    for req in promocion.requisitos:
        if cantidades.get(req.id_producto, 0) < req.cantidad_requerida:
            return False
    return True


def _sets_completos(promocion: Promocion, cantidades: dict[int, int]) -> int:
    """Cuántas veces se cumple el combo completo de la promoción en el carrito."""
    if not promocion.requisitos:
        return 0
    if not _promocion_califica(promocion, cantidades):
        return 0
    return min(
        cantidades[req.id_producto] // req.cantidad_requerida
        for req in promocion.requisitos
    )


def _precios_por_producto(lineas: list[LineaVentaCalculada]) -> dict[int, Decimal]:
    precios: dict[int, Decimal] = {}
    for ln in lineas:
        precios[ln.id_producto] = ln.precio_unitario
    return precios


def _subtotal_con_sets_completos(
    promocion: Promocion,
    cantidades: dict[int, int],
    lineas: list[LineaVentaCalculada],
) -> Decimal:
    """
    Subtotal sobre el que aplica el descuento: solo unidades que forman
    sets completos (ej. promo 3x: 4 unidades -> descuento sobre 3, no 4).
    """
    sets = _sets_completos(promocion, cantidades)
    if sets == 0:
        return Decimal("0.00")

    precios = _precios_por_producto(lineas)
    total = Decimal("0.00")
    for req in promocion.requisitos:
        unidades_con_descuento = sets * req.cantidad_requerida
        total += unidades_con_descuento * precios[req.id_producto]
    return money(total)


def evaluar_promocion_aplicable(
    session: Session,
    items: list[ItemVentaInput],
    lineas: list[LineaVentaCalculada],
) -> PromocionAplicada | None:
    """
    Busca promociones activas cuyos requisitos se cumplen en el carrito.
    El descuento aplica solo a unidades incluidas en sets completos del combo.
    Si varias califican, aplica la de mayor monto descontado.
    """
    cantidades = _cantidades_carrito(items)
    promociones = session.scalars(
        select(Promocion)
        .where(Promocion.activa.is_(True))
        .options(selectinload(Promocion.requisitos))
    ).all()

    mejor: PromocionAplicada | None = None
    for promo in promociones:
        if not _promocion_califica(promo, cantidades):
            continue

        subtotal_afectado = _subtotal_con_sets_completos(promo, cantidades, lineas)
        monto = money(subtotal_afectado * promo.descuento_porcentaje / Decimal("100"))

        candidata = PromocionAplicada(
            id_promocion=promo.id_promocion,
            nombre_promocion=promo.nombre_promocion,
            descuento_porcentaje=promo.descuento_porcentaje,
            monto_descontado=monto,
            subtotal_afectado=subtotal_afectado,
        )
        if mejor is None or candidata.monto_descontado > mejor.monto_descontado:
            mejor = candidata

    return mejor
