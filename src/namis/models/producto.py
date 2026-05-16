from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.detalle_venta import DetalleVenta
    from namis.models.promocion import Promocion
    from namis.models.receta import Receta


class Producto(Base):
    __tablename__ = "productos"

    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_producto: Mapped[str] = mapped_column(String(100), nullable=False)
    tamano_g: Mapped[int | None] = mapped_column(Integer)
    es_endulzado: Mapped[bool | None] = mapped_column(Boolean)
    precio_actual: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    precio_mayorista: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    costo_actual: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    detalles_venta: Mapped[list[DetalleVenta]] = relationship(back_populates="producto")
    recetas: Mapped[list[Receta]] = relationship(
        back_populates="producto",
        cascade="all, delete-orphan",
    )
    promociones_como_requisito: Mapped[list[Promocion]] = relationship(
        back_populates="producto_requerido",
    )
