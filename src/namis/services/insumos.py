from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from namis.exceptions import (
    InsumoDuplicadoError,
    InsumoNoEncontradoError,
    InsumoSinPrecioVigenteError,
)
from namis.models.insumo import Insumo
from namis.models.insumo_historial import InsumoHistorialPrecio
from namis.schemas.insumos import (
    InsumoConPrecioVigente,
    PrecioVigenteInsumo,
    RegistroCompraInsumoResultado,
)
from namis.services.costos import actualizar_costos_productos_afectados_por_insumo
from namis.services.insumo_precios import obtener_precio_vigente_insumo

__all__ = [
    "crear_insumo",
    "listar_insumos_actuales",
    "obtener_precio_vigente_insumo",
    "registrar_compra_insumo",
]


def crear_insumo(session: Session, nombre: str, unidad_medida: str) -> Insumo:
    nombre_limpio = nombre.strip()
    unidad_limpia = unidad_medida.strip()

    existe = session.scalar(
        select(Insumo.id_insumo).where(Insumo.nombre_insumo == nombre_limpio)
    )
    if existe is not None:
        raise InsumoDuplicadoError(nombre_limpio)

    insumo = Insumo(nombre_insumo=nombre_limpio, unidad_medida=unidad_limpia)
    session.add(insumo)
    session.flush()
    return insumo


def registrar_compra_insumo(
    session: Session,
    id_insumo: int,
    cantidad: Decimal,
    precio_pagado: Decimal,
) -> RegistroCompraInsumoResultado:
    if session.get(Insumo, id_insumo) is None:
        raise InsumoNoEncontradoError(id_insumo)
    if cantidad <= 0 or precio_pagado < 0:
        raise ValueError("La cantidad debe ser mayor a cero y el precio no puede ser negativo.")

    historial = InsumoHistorialPrecio(
        id_insumo=id_insumo,
        cantidad_paquete=cantidad,
        precio_paquete=precio_pagado,
    )
    session.add(historial)
    session.flush()

    productos_actualizados = actualizar_costos_productos_afectados_por_insumo(
        session,
        id_insumo,
    )

    return RegistroCompraInsumoResultado(
        id_historial=historial.id_historial,
        id_insumo=id_insumo,
        productos_costo_actualizado=productos_actualizados,
    )


def listar_insumos_actuales(session: Session) -> list[InsumoConPrecioVigente]:
    insumos = session.scalars(
        select(Insumo).order_by(Insumo.nombre_insumo)
    ).all()

    resultado: list[InsumoConPrecioVigente] = []
    for insumo in insumos:
        try:
            precio: PrecioVigenteInsumo | None = obtener_precio_vigente_insumo(
                session, insumo.id_insumo
            )
        except InsumoSinPrecioVigenteError:
            precio = None

        resultado.append(
            InsumoConPrecioVigente(
                id_insumo=insumo.id_insumo,
                nombre_insumo=insumo.nombre_insumo,
                unidad_medida=insumo.unidad_medida,
                precio_vigente=precio,
            )
        )

    return resultado
