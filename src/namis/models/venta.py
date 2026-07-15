from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.cliente import Cliente
    from namis.models.detalle_venta import DetalleVenta
    from namis.models.promocion import Promocion


class Venta(Base):
    __tablename__ = "ventas"

    id_venta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_cliente: Mapped[int] = mapped_column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    fecha: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    medio_pago: Mapped[str | None] = mapped_column(String(50))
    red_social: Mapped[str | None] = mapped_column(String(50))
    requiere_envio: Mapped[bool | None] = mapped_column(Boolean, default=False)
    costo_envio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    id_promocion: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("promociones.id_promocion"),
        nullable=True,
    )
    monto_descontado: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    total_cobrado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text)
    es_deudor: Mapped[bool | None] = mapped_column(Boolean, default=False)

    cliente: Mapped[Cliente] = relationship(back_populates="ventas")
    promocion: Mapped[Promocion | None] = relationship(back_populates="ventas")
    detalles: Mapped[list[DetalleVenta]] = relationship(
        back_populates="venta",
        cascade="all, delete-orphan",
    )
