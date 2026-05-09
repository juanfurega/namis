from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.insumo import Insumo
    from namis.models.producto import Producto


class Receta(Base):
    __tablename__ = "recetas"

    id_receta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("productos.id_producto", ondelete="CASCADE"),
        nullable=False,
    )
    id_insumo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("insumos.id_insumo", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad_necesaria: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    producto: Mapped[Producto] = relationship(back_populates="recetas")
    insumo: Mapped[Insumo] = relationship(back_populates="recetas")
