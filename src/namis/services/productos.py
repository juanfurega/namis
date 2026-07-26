from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.orm import Session

from namis.exceptions import ProductoNoEncontradoError
from namis.models.producto import Producto
from namis.models.receta import Receta
from namis.models.detalle_venta import DetalleVenta
from namis.models.promocion_requisito import PromocionRequisito


def crear_producto(
    session: Session,
    nombre_producto: str,
    precio_actual: Decimal,
    tamano_g: int,
    *,
    es_endulzado: bool | None = None,
    costo_actual: Decimal | None = None,
) -> Producto:
    """
    Crea un producto vendible. El costo_actual inicial puede ser 0 y
    se recalcula al armar / modificar su receta.
    """
    producto = Producto(
        nombre_producto=nombre_producto.strip(),
        tamano_g=tamano_g,
        es_endulzado=es_endulzado,
        precio_actual=precio_actual,
        costo_actual=costo_actual if costo_actual is not None else Decimal("0.00"),
    )
    session.add(producto)
    session.flush()
    return producto


def obtener_producto(session: Session, id_producto: int) -> Producto:
    producto = session.get(Producto, id_producto)
    if producto is None:
        raise ProductoNoEncontradoError(id_producto)
    return producto


def actualizar_precios_producto(
    session: Session,
    id_producto: int,
    precio_actual: Decimal,
) -> Producto:
    """Actualiza el precio de venta sin tocar la receta ni el costo_actual."""
    if not isinstance(precio_actual, Decimal):
        precio_actual = Decimal(precio_actual)
    if precio_actual < 0:
        raise ValueError("El precio de venta no puede ser negativo.")

    producto = obtener_producto(session, id_producto)
    producto.precio_actual = precio_actual
    session.flush()
    return producto


def eliminar_producto(session: Session, id_producto: int) -> None:
    """Marca un producto como inactivo (soft delete) para no afectar el balance de ventas anteriores.
    También elimina referencias en promociones y recetas donde es componente."""
    producto = session.get(Producto, id_producto)
    if producto is None:
        raise ProductoNoEncontradoError(id_producto)
    
    # Marcar producto como inactivo
    producto.activo = False
    
    # Eliminar requisitos de promoción asociados
    session.execute(
        delete(PromocionRequisito).where(PromocionRequisito.id_producto == id_producto)
    )
    
    # Eliminar recetas donde este producto es usado como componente
    session.execute(
        delete(Receta).where(Receta.id_producto_componente == id_producto)
    )
    
    # Eliminar la receta del propio producto
    session.execute(
        delete(Receta).where(Receta.id_producto == id_producto)
    )
    
    session.flush()
