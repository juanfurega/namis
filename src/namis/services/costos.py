from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from namis.exceptions import InsumoSinPrecioVigenteError, ProductoNoEncontradoError
from namis.models.producto import Producto
from namis.models.receta import Receta
from namis.services.insumo_precios import obtener_precio_vigente_insumo
from namis.utils.money import money


def costo_linea_receta(
    cantidad_necesaria: Decimal,
    cantidad_paquete: Decimal,
    precio_paquete: Decimal,
) -> Decimal:
    if cantidad_paquete <= 0:
        raise ValueError("La cantidad del paquete debe ser mayor a cero.")
    return money((cantidad_necesaria / cantidad_paquete) * precio_paquete)


def calcular_costo_producto(session: Session, id_producto: int) -> Decimal:
    recetas = session.scalars(
        select(Receta).where(Receta.id_producto == id_producto)
    ).all()

    total = Decimal("0.00")
    for receta in recetas:
        vigente = obtener_precio_vigente_insumo(session, receta.id_insumo)
        total += costo_linea_receta(
            receta.cantidad_necesaria,
            vigente.cantidad_paquete,
            vigente.precio_paquete,
        )
    return money(total)


def actualizar_costo_producto(session: Session, id_producto: int) -> Decimal:
    producto = session.get(Producto, id_producto)
    if producto is None:
        raise ProductoNoEncontradoError(id_producto)

    costo = calcular_costo_producto(session, id_producto)
    producto.costo_actual = costo
    return costo


def actualizar_costos_productos_afectados_por_insumo(
    session: Session,
    id_insumo: int,
) -> list[int]:
    ids_productos = session.scalars(
        select(Receta.id_producto)
        .where(Receta.id_insumo == id_insumo)
        .distinct()
    ).all()

    actualizados: list[int] = []
    for id_producto in ids_productos:
        try:
            actualizar_costo_producto(session, id_producto)
        except InsumoSinPrecioVigenteError:
            continue
        actualizados.append(id_producto)

    return actualizados
