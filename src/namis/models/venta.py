from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.cliente import Cliente
    from namis.models.detalle_venta import DetalleVenta
    from namis.models.promocion import Promocion


class Venta(Base):
    __tablename__ = "ventas"

    id_venta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_cliente: Mapped[int] = mapped_column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    fecha: Mapped[date | None] = mapped_column(Date, server_default=text("CURRENT_DATE"))
    medio_pago: Mapped[str | None] = mapped_column(String(50))
    requiere_envio: Mapped[bool | None] = mapped_column(Boolean, default=False)
    costo_envio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    id_promocion: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("promociones.id_promocion"),
        nullable=True,
    )
    es_precio_mayorista: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    total_cobrado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text)

    cliente: Mapped[Cliente] = relationship(back_populates="ventas")
    promocion: Mapped[Promocion | None] = relationship(back_populates="ventas")
    detalles: Mapped[list[DetalleVenta]] = relationship(
        back_populates="venta",
        cascade="all, delete-orphan",
    )
