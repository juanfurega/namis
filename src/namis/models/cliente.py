from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.venta import Venta


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    fecha_registro: Mapped[date | None] = mapped_column(
        Date,
        server_default=text("CURRENT_DATE"),
    )

    ventas: Mapped[list[Venta]] = relationship(back_populates="cliente")
