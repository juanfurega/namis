from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.promocion_requisito import PromocionRequisito
    from namis.models.venta import Venta


class Promocion(Base):
    __tablename__ = "promociones"

    id_promocion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_promocion: Mapped[str] = mapped_column(String(50), nullable=False)
    descuento_porcentaje: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    requisitos: Mapped[list[PromocionRequisito]] = relationship(
        back_populates="promocion",
        cascade="all, delete-orphan",
    )
    ventas: Mapped[list[Venta]] = relationship(back_populates="promocion")
