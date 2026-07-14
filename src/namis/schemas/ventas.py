from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from namis.schemas.promociones import PromocionAplicada


@dataclass(frozen=True, slots=True)
class ItemVentaInput:
    """Producto y cantidad a incluir en una venta."""

    id_producto: int
    cantidad: int


@dataclass(frozen=True, slots=True)
class LineaVentaCalculada:
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal
    costo_unitario: Decimal
    subtotal: Decimal


@dataclass(frozen=True, slots=True)
class PresupuestoVenta:
    """Total a cobrar antes de persistir (para mostrar en pantalla)."""

    lineas: list[LineaVentaCalculada]
    subtotal_productos: Decimal
    costo_envio: Decimal
    monto_descontado: Decimal
    total_cobrado: Decimal
    promocion: PromocionAplicada | None


@dataclass(frozen=True, slots=True)
class VentaRegistrada:
    id_venta: int
    id_cliente: int
    nombre_cliente: str
    fecha: datetime
    medio_pago: str | None
    red_social: str | None
    costo_envio: Decimal
    monto_descontado: Decimal
    total_cobrado: Decimal
    promocion: PromocionAplicada | None
    lineas: list[LineaVentaCalculada]


# Valores informativos permitidos (la UI puede mostrar estos)
MEDIOS_COMUNICACION = frozenset({"wsp", "ig", "msn"})
MEDIOS_PAGO = frozenset({"efectivo", "transferencia"})
