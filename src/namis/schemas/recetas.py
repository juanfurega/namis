from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class LineaRecetaDetalle:
    id_receta: int
    tipo: str  # "insumo" | "producto"
    id_componente: int
    nombre_componente: str
    unidad: str
    cantidad_necesaria: Decimal
    costo_unitario_componente: Decimal
    costo_linea: Decimal


@dataclass(frozen=True, slots=True)
class RecetaDetalle:
    id_producto: int
    nombre_producto: str
    lineas: list[LineaRecetaDetalle]
    costo_total: Decimal
