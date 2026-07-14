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
    fecha: datetime
    nombre_cliente: str
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
class ResumenDia:
    fecha: date
    cantidad_ventas: int
    total_cobrado: Decimal
    total_ganancia: Decimal


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
