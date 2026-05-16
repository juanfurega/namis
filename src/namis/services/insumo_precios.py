from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from namis.exceptions import InsumoNoEncontradoError, InsumoSinPrecioVigenteError
from namis.models.insumo import Insumo
from namis.models.insumo_historial import InsumoHistorialPrecio
from namis.schemas.insumos import PrecioVigenteInsumo
from namis.utils.money import money


def obtener_precio_vigente_insumo(session: Session, id_insumo: int) -> PrecioVigenteInsumo:
    if session.get(Insumo, id_insumo) is None:
        raise InsumoNoEncontradoError(id_insumo)

    max_fecha = (
        select(func.max(InsumoHistorialPrecio.fecha_registro))
        .where(InsumoHistorialPrecio.id_insumo == id_insumo)
        .scalar_subquery()
    )

    historial = session.scalars(
        select(InsumoHistorialPrecio)
        .where(
            InsumoHistorialPrecio.id_insumo == id_insumo,
            InsumoHistorialPrecio.fecha_registro == max_fecha,
        )
        .order_by(InsumoHistorialPrecio.id_historial.desc())
        .limit(1)
    ).first()

    if historial is None:
        raise InsumoSinPrecioVigenteError(id_insumo)

    precio_unitario = money(historial.precio_paquete / historial.cantidad_paquete)

    return PrecioVigenteInsumo(
        id_insumo=id_insumo,
        id_historial=historial.id_historial,
        cantidad_paquete=historial.cantidad_paquete,
        precio_paquete=historial.precio_paquete,
        precio_unitario=precio_unitario,
        fecha_registro=historial.fecha_registro,
    )
