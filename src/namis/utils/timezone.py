"""Fechas y horas de negocio para Namis."""

from datetime import date, datetime
from zoneinfo import ZoneInfo


ZONA_HORARIA_ARGENTINA = ZoneInfo("America/Argentina/Buenos_Aires")


def ahora_argentina() -> datetime:
    """Hora actual de Argentina, sin zona para persistir en MySQL DATETIME."""
    return datetime.now(ZONA_HORARIA_ARGENTINA).replace(tzinfo=None)


def hoy_argentina() -> date:
    """Fecha actual de Argentina."""
    return ahora_argentina().date()
