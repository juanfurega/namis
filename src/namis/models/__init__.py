"""Modelos ORM alineados con schema.sql."""

from namis.models.base import Base
from namis.models.cliente import Cliente
from namis.models.detalle_venta import DetalleVenta
from namis.models.insumo import Insumo
from namis.models.producto import Producto
from namis.models.promocion import Promocion
from namis.models.receta import Receta
from namis.models.venta import Venta

__all__ = [
    "Base",
    "Cliente",
    "DetalleVenta",
    "Insumo",
    "Producto",
    "Promocion",
    "Receta",
    "Venta",
]
