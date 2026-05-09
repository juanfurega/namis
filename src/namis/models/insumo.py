from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.receta import Receta


class Insumo(Base):
    __tablename__ = "insumos"

    id_insumo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_insumo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad_paquete: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    precio_paquete: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_ultima_actualizacion: Mapped[date | None] = mapped_column(
        Date,
        server_default=text("CURRENT_DATE"),
    )

    recetas: Mapped[list[Receta]] = relationship(back_populates="insumo")
