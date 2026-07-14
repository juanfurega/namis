from sqlalchemy import select
from sqlalchemy.orm import Session

from namis.models.cliente import Cliente


def obtener_o_crear_cliente(session: Session, nombre: str) -> Cliente:
    """Busca cliente por nombre; si no existe, lo crea."""
    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        raise ValueError("El nombre del cliente no puede estar vacío.")

    existente = session.scalar(
        select(Cliente).where(Cliente.nombre == nombre_limpio)
    )
    if existente is not None:
        return existente

    cliente = Cliente(nombre=nombre_limpio)
    session.add(cliente)
    session.flush()
    return cliente
