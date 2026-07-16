from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class LineaVentaHistorial:
    id_detalle: int
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario_cobrado: Decimal
    costo_unitario_historico: Decimal
    subtotal_cobrado: Decimal
    subtotal_costo: Decimal


@dataclass(frozen=True, slots=True)
class VentaHistorialDetalle:
    id_venta: int
    id_cliente: int
    fecha: datetime
    medio_pago: str | None
    red_social: str | None
    nombre_promocion: str | None
    descuento_porcentaje: Decimal | None
    monto_descontado: Decimal
    costo_envio: Decimal
    subtotal_bruto: Decimal
    total_cobrado: Decimal
    costo_productos: Decimal
    ganancia: Decimal
    lineas: list[LineaVentaHistorial]


@dataclass(frozen=True, slots=True)
class ClienteHistorialDia:
    """Ventas de un cliente en un día (nombre primero, detalles debajo)."""

    id_cliente: int
    nombre_cliente: str
    ventas: list[VentaHistorialDetalle]
    total_cobrado: Decimal
    total_ganancia: Decimal


@dataclass(frozen=True, slots=True)
class HistorialDiaPorCliente:
    fecha: date
    clientes: list[ClienteHistorialDia]


@dataclass(frozen=True, slots=True)
class VentaHistorialConCliente:
    """Detalle de una venta con datos del cliente asociado."""

    id_cliente: int
    nombre_cliente: str
    venta: VentaHistorialDetalle


@dataclass(frozen=True, slots=True)
class BalancePorMedioPago:
    """Balance desglosado por medio de pago."""
    medio_pago: str
    cantidad_ventas: int
    total_cobrado: Decimal
    total_ganancia: Decimal


@dataclass(frozen=True, slots=True)
class ResumenDia:
    fecha: date
    cantidad_ventas: int
    total_cobrado: Decimal
    total_ganancia: Decimal
    por_medio_pago: list[BalancePorMedioPago]


@dataclass(frozen=True, slots=True)
class DiaCalendario:
    fecha: date
    cantidad_ventas: int
    total_ganancia: Decimal
    tiene_ventas: bool


@dataclass(frozen=True, slots=True)
class ResumenMesCalendario:
    anio: int
    mes: int
    dias: list[DiaCalendario]
    total_cobrado: Decimal
    total_ganancia: Decimal
    cantidad_ventas: int
