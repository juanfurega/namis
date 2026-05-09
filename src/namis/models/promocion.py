from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.producto import Producto
    from namis.models.venta import Venta


class Promocion(Base):
    __tablename__ = "promociones"

    id_promocion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_promocion: Mapped[str] = mapped_column(String(50), nullable=False)
    id_producto_requerido: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("productos.id_producto"),
        nullable=True,
    )
    cantidad_requerida: Mapped[int] = mapped_column(Integer, nullable=False)
    descuento_monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    descuento_porcentaje: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    producto_requerido: Mapped[Producto | None] = relationship(back_populates="promociones_como_requisito")
    ventas: Mapped[list[Venta]] = relationship(back_populates="promocion")
