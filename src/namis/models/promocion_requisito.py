from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.producto import Producto
    from namis.models.promocion import Promocion


class PromocionRequisito(Base):
    __tablename__ = "promocion_requisitos"
    __table_args__ = (
        UniqueConstraint("id_promocion", "id_producto", name="uq_promo_producto"),
    )

    id_requisito: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_promocion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("promociones.id_promocion", ondelete="CASCADE"),
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("productos.id_producto", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad_requerida: Mapped[int] = mapped_column(Integer, nullable=False)

    promocion: Mapped[Promocion] = relationship(back_populates="requisitos")
    producto: Mapped[Producto] = relationship(back_populates="promociones_como_requisito")
