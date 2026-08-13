from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from namis.models.base import Base

if TYPE_CHECKING:
    from namis.models.insumo import Insumo


class InsumoHistorialPrecio(Base):
    __tablename__ = "insumos_historial_precios"
    # Streamlit puede recargar módulos durante el desarrollo o despliegue.
    # Evita que una segunda carga registre de nuevo esta tabla en el mismo metadata.
    __table_args__ = {"extend_existing": True}

    id_historial: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_insumo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("insumos.id_insumo", ondelete="CASCADE"),
        nullable=False,
    )
    cantidad_paquete: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    precio_paquete: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    insumo: Mapped[Insumo] = relationship(back_populates="historial_precios")
