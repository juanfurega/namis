from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.insumo_historial import InsumoHistorialPrecio
    from namis.models.detalle_bolsa_venta import DetalleBolsaVenta
    from namis.models.receta import Receta


class Insumo(Base):
    __tablename__ = "insumos"
    __table_args__ = {"extend_existing": True}

    id_insumo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_insumo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String(20), nullable=False)
    es_bolsa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    historial_precios: Mapped[list[InsumoHistorialPrecio]] = relationship(
        back_populates="insumo",
        cascade="all, delete-orphan",
    )
    recetas: Mapped[list[Receta]] = relationship(back_populates="insumo")
    bolsas_utilizadas: Mapped[list[DetalleBolsaVenta]] = relationship(back_populates="insumo")
