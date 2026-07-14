from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.insumo import Insumo
    from namis.models.producto import Producto


class Receta(Base):
    __tablename__ = "recetas"
    __table_args__ = (
        CheckConstraint(
            "(id_insumo IS NOT NULL AND id_producto_componente IS NULL) "
            "OR (id_insumo IS NULL AND id_producto_componente IS NOT NULL)",
            name="chk_receta_linea",
        ),
    )

    id_receta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("productos.id_producto", ondelete="CASCADE"),
        nullable=False,
    )
    id_insumo: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("insumos.id_insumo", ondelete="RESTRICT"),
        nullable=True,
    )
    id_producto_componente: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("productos.id_producto", ondelete="RESTRICT"),
        nullable=True,
    )
    cantidad_necesaria: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    producto: Mapped[Producto] = relationship(
        back_populates="recetas",
        foreign_keys=[id_producto],
    )
    insumo: Mapped[Insumo | None] = relationship(back_populates="recetas")
    producto_componente: Mapped[Producto | None] = relationship(
        back_populates="usado_en_recetas",
        foreign_keys=[id_producto_componente],
    )
