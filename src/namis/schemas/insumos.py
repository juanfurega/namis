from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PrecioVigenteInsumo:
    id_insumo: int
    id_historial: int
    cantidad_paquete: Decimal
    precio_paquete: Decimal
    precio_unitario: Decimal
    fecha_registro: datetime


@dataclass(frozen=True, slots=True)
class InsumoConPrecioVigente:
    id_insumo: int
    nombre_insumo: str
    unidad_medida: str
    precio_vigente: PrecioVigenteInsumo | None


@dataclass(frozen=True, slots=True)
class RegistroCompraInsumoResultado:
    id_historial: int
    id_insumo: int
    productos_costo_actualizado: list[int]
