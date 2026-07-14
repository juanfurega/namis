from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from namis.exceptions import (
    InsumoNoEncontradoError,
    LineaRecetaInvalidaError,
    LineaRecetaNoEncontradaError,
    ProductoNoEncontradoError,
    RecetaCiclicaError,
)
from namis.models.insumo import Insumo
from namis.models.producto import Producto
from namis.models.receta import Receta
from namis.schemas.recetas import LineaRecetaDetalle, RecetaDetalle
from namis.services.costos import (
    actualizar_costos_en_cascada,
    calcular_costo_producto,
    costo_linea_insumo,
)
from namis.services.insumo_precios import obtener_precio_vigente_insumo
from namis.utils.money import money


def _asegurar_producto(session: Session, id_producto: int) -> Producto:
    producto = session.get(Producto, id_producto)
    if producto is None:
        raise ProductoNoEncontradoError(id_producto)
    return producto


def _detectar_ciclo(
    session: Session,
    id_producto: int,
    id_producto_componente: int,
) -> None:
    """BFS: si id_producto aparece en el árbol de id_producto_componente, hay ciclo."""
    if id_producto == id_producto_componente:
        raise RecetaCiclicaError(id_producto, id_producto_componente)

    cola = [id_producto_componente]
    visitados: set[int] = set()
    while cola:
        actual = cola.pop(0)
        if actual in visitados:
            continue
        visitados.add(actual)
        hijos = session.scalars(
            select(Receta.id_producto_componente).where(
                Receta.id_producto == actual,
                Receta.id_producto_componente.is_not(None),
            )
        ).all()
        for hijo in hijos:
            if hijo == id_producto:
                raise RecetaCiclicaError(id_producto, id_producto_componente)
            if hijo is not None and hijo not in visitados:
                cola.append(hijo)


def agregar_insumo_a_receta(
    session: Session,
    id_producto: int,
    id_insumo: int,
    cantidad_necesaria: Decimal,
) -> Receta:
    _asegurar_producto(session, id_producto)
    if session.get(Insumo, id_insumo) is None:
        raise InsumoNoEncontradoError(id_insumo)
    if cantidad_necesaria <= 0:
        raise LineaRecetaInvalidaError("La cantidad necesaria debe ser mayor a cero.")

    linea = Receta(
        id_producto=id_producto,
        id_insumo=id_insumo,
        id_producto_componente=None,
        cantidad_necesaria=cantidad_necesaria,
    )
    session.add(linea)
    session.flush()
    actualizar_costos_en_cascada(session, [id_producto])
    return linea


def agregar_producto_a_receta(
    session: Session,
    id_producto: int,
    id_producto_componente: int,
    cantidad_necesaria: Decimal,
) -> Receta:
    """
    Incluye un producto ya existente (con su propia receta) como componente.
    cantidad_necesaria = cuántas unidades de ese producto entran en uno del dueño.
    """
    _asegurar_producto(session, id_producto)
    _asegurar_producto(session, id_producto_componente)
    if cantidad_necesaria <= 0:
        raise LineaRecetaInvalidaError("La cantidad necesaria debe ser mayor a cero.")

    _detectar_ciclo(session, id_producto, id_producto_componente)

    linea = Receta(
        id_producto=id_producto,
        id_insumo=None,
        id_producto_componente=id_producto_componente,
        cantidad_necesaria=cantidad_necesaria,
    )
    session.add(linea)
    session.flush()
    actualizar_costos_en_cascada(session, [id_producto])
    return linea


def eliminar_linea_receta(session: Session, id_receta: int) -> list[int]:
    linea = session.get(Receta, id_receta)
    if linea is None:
        raise LineaRecetaNoEncontradaError(id_receta)

    id_producto = linea.id_producto
    session.delete(linea)
    session.flush()
    return actualizar_costos_en_cascada(session, [id_producto])


def obtener_receta(session: Session, id_producto: int) -> RecetaDetalle:
    producto = _asegurar_producto(session, id_producto)
    lineas_orm = session.scalars(
        select(Receta).where(Receta.id_producto == id_producto).order_by(Receta.id_receta)
    ).all()

    lineas: list[LineaRecetaDetalle] = []
    for linea in lineas_orm:
        if linea.id_insumo is not None:
            insumo = session.get(Insumo, linea.id_insumo)
            assert insumo is not None
            vigente = obtener_precio_vigente_insumo(session, linea.id_insumo)
            costo_unitario = vigente.precio_unitario
            costo_linea = costo_linea_insumo(
                linea.cantidad_necesaria,
                vigente.cantidad_paquete,
                vigente.precio_paquete,
            )
            lineas.append(
                LineaRecetaDetalle(
                    id_receta=linea.id_receta,
                    tipo="insumo",
                    id_componente=linea.id_insumo,
                    nombre_componente=insumo.nombre_insumo,
                    unidad=insumo.unidad_medida,
                    cantidad_necesaria=linea.cantidad_necesaria,
                    costo_unitario_componente=costo_unitario,
                    costo_linea=costo_linea,
                )
            )
        else:
            assert linea.id_producto_componente is not None
            componente = session.get(Producto, linea.id_producto_componente)
            assert componente is not None
            costo_unitario = calcular_costo_producto(session, linea.id_producto_componente)
            costo_linea = money(linea.cantidad_necesaria * costo_unitario)
            lineas.append(
                LineaRecetaDetalle(
                    id_receta=linea.id_receta,
                    tipo="producto",
                    id_componente=linea.id_producto_componente,
                    nombre_componente=componente.nombre_producto,
                    unidad="unidad",
                    cantidad_necesaria=linea.cantidad_necesaria,
                    costo_unitario_componente=costo_unitario,
                    costo_linea=costo_linea,
                )
            )

    costo_total = money(sum((ln.costo_linea for ln in lineas), Decimal("0.00")))
    return RecetaDetalle(
        id_producto=producto.id_producto,
        nombre_producto=producto.nombre_producto,
        lineas=lineas,
        costo_total=costo_total,
    )
