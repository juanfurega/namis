from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.insumo import Insumo
    from namis.models.venta import Venta


class DetalleBolsaVenta(Base):
    """Costo histórico de una bolsa utilizada en una venta."""

    __tablename__ = "detalle_bolsas_venta"
    __table_args__ = {"extend_existing": True}

    id_detalle_bolsa: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_venta: Mapped[int] = mapped_column(
        Integer, ForeignKey("ventas.id_venta", ondelete="CASCADE"), nullable=False
    )
    id_insumo: Mapped[int] = mapped_column(
        Integer, ForeignKey("insumos.id_insumo"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario_historico: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    costo_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    venta: Mapped[Venta] = relationship(back_populates="bolsas")
    insumo: Mapped[Insumo] = relationship(back_populates="bolsas_utilizadas")
