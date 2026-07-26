from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from namis.exceptions import (
    InsumoSinPrecioVigenteError,
    ProductoNoEncontradoError,
    RecetaCiclicaError,
)
from namis.models.producto import Producto
from namis.models.receta import Receta
from namis.services.insumo_precios import obtener_precio_vigente_insumo
from namis.utils.money import money


def costo_linea_insumo(
    cantidad_necesaria: Decimal,
    cantidad_paquete: Decimal,
    precio_paquete: Decimal,
) -> Decimal:
    if cantidad_paquete <= 0:
        raise ValueError("La cantidad del paquete debe ser mayor a cero.")
    return money((cantidad_necesaria / cantidad_paquete) * precio_paquete)


# Compatibilidad con el nombre anterior usado en insumos
costo_linea_receta = costo_linea_insumo


def _calcular_costo_receta_base(
    session: Session,
    id_producto: int,
    _stack: frozenset[int] | None = None,
) -> tuple[Decimal, Decimal]:
    """
    Calcula el costo base de la receta y el tamaño total de la receta.
    Retorna (costo_receta, tamano_receta).
    Esta función NO ajusta el costo al tamaño del producto final.
    """
    if session.get(Producto, id_producto) is None:
        raise ProductoNoEncontradoError(id_producto)

    stack = _stack or frozenset()
    if id_producto in stack:
        raise RecetaCiclicaError(id_producto, id_producto)

    stack = stack | {id_producto}
    lineas = session.scalars(
        select(Receta).where(Receta.id_producto == id_producto)
    ).all()

    total = Decimal("0.00")
    tamano_receta = Decimal("0.00")
    
    for linea in lineas:
        tamano_receta += linea.cantidad_necesaria
        if linea.id_insumo is not None:
            vigente = obtener_precio_vigente_insumo(session, linea.id_insumo)
            total += costo_linea_insumo(
                linea.cantidad_necesaria,
                vigente.cantidad_paquete,
                vigente.precio_paquete,
            )
        elif linea.id_producto_componente is not None:
            if linea.id_producto_componente in stack:
                raise RecetaCiclicaError(id_producto, linea.id_producto_componente)
            # Usar el costo base del componente (sin ajuste final al tamaño)
            costo_comp, _ = _calcular_costo_receta_base(
                session,
                linea.id_producto_componente,
                stack,
            )
            # Obtener el tamaño del producto componente para calcular costo por gramo
            componente = session.get(Producto, linea.id_producto_componente)
            assert componente is not None
            costo_por_gramo = costo_comp / Decimal(str(componente.tamano_g))
            total += money(linea.cantidad_necesaria * costo_por_gramo)
        else:
            raise ValueError(f"Línea de receta {linea.id_receta} sin componente.")

    return money(total), tamano_receta


def calcular_costo_producto(
    session: Session,
    id_producto: int,
    _stack: frozenset[int] | None = None,
) -> Decimal:
    """
    Calcula el costo total del producto como la suma de los costos de sus componentes.
    """
    costo_receta, _ = _calcular_costo_receta_base(session, id_producto, _stack)
    return costo_receta


def actualizar_costo_producto(session: Session, id_producto: int) -> Decimal:
    producto = session.get(Producto, id_producto)
    if producto is None:
        raise ProductoNoEncontradoError(id_producto)

    costo = calcular_costo_producto(session, id_producto)
    producto.costo_actual = costo
    return costo


def _productos_que_usan_como_componente(session: Session, id_producto: int) -> list[int]:
    return list(
        session.scalars(
            select(Receta.id_producto)
            .where(Receta.id_producto_componente == id_producto)
            .distinct()
        ).all()
    )


def actualizar_costos_en_cascada(
    session: Session,
    ids_productos: list[int],
) -> list[int]:
    """Recalcula productos y luego todos los que los usan como sub-receta."""
    cola = list(ids_productos)
    vistos: set[int] = set()
    actualizados: list[int] = []

    while cola:
        id_producto = cola.pop(0)
        if id_producto in vistos:
            continue
        vistos.add(id_producto)

        try:
            actualizar_costo_producto(session, id_producto)
        except (InsumoSinPrecioVigenteError, RecetaCiclicaError):
            continue

        actualizados.append(id_producto)
        for padre in _productos_que_usan_como_componente(session, id_producto):
            if padre not in vistos:
                cola.append(padre)

    return actualizados


def actualizar_costos_productos_afectados_por_insumo(
    session: Session,
    id_insumo: int,
) -> list[int]:
    ids_directos = list(
        session.scalars(
            select(Receta.id_producto)
            .where(Receta.id_insumo == id_insumo)
            .distinct()
        ).all()
    )
    return actualizar_costos_en_cascada(session, ids_directos)
