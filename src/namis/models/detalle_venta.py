from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.producto import Producto
    from namis.models.venta import Venta


class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"

    id_detalle: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_venta: Mapped[int] = mapped_column(Integer, ForeignKey("ventas.id_venta", ondelete="CASCADE"), nullable=False)
    id_producto: Mapped[int] = mapped_column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    precio_unitario_cobrado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    costo_unitario_historico: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    venta: Mapped[Venta] = relationship(back_populates="detalles")
    producto: Mapped[Producto] = relationship(back_populates="detalles_venta")
