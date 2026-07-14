from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class RequisitoPromocionInput:
    id_producto: int
    cantidad_requerida: int


@dataclass(frozen=True, slots=True)
class RequisitoPromocionDetalle:
    id_requisito: int
    id_producto: int
    nombre_producto: str
    cantidad_requerida: int


@dataclass(frozen=True, slots=True)
class PromocionDetalle:
    id_promocion: int
    nombre_promocion: str
    descuento_porcentaje: Decimal
    activa: bool
    requisitos: list[RequisitoPromocionDetalle]


@dataclass(frozen=True, slots=True)
class PromocionAplicada:
    id_promocion: int
    nombre_promocion: str
    descuento_porcentaje: Decimal
    monto_descontado: Decimal
    subtotal_afectado: Decimal
