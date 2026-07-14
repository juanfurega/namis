class NamisError(Exception):
    """Error de dominio del sistema Namis."""


class InsumoNoEncontradoError(NamisError):
    def __init__(self, id_insumo: int) -> None:
        super().__init__(f"No existe insumo con id {id_insumo}.")
        self.id_insumo = id_insumo


class ProductoNoEncontradoError(NamisError):
    def __init__(self, id_producto: int) -> None:
        super().__init__(f"No existe producto con id {id_producto}.")
        self.id_producto = id_producto


class InsumoSinPrecioVigenteError(NamisError):
    def __init__(self, id_insumo: int) -> None:
        super().__init__(f"El insumo {id_insumo} no tiene compras registradas.")
        self.id_insumo = id_insumo


class InsumoDuplicadoError(NamisError):
    def __init__(self, nombre: str) -> None:
        super().__init__(f"Ya existe un insumo con el nombre '{nombre}'.")
        self.nombre = nombre


class RecetaCiclicaError(NamisError):
    def __init__(self, id_producto: int, id_componente: int) -> None:
        super().__init__(
            f"Ciclo en recetas: el producto {id_producto} no puede incluir "
            f"el componente {id_componente} (dependencia circular)."
        )
        self.id_producto = id_producto
        self.id_componente = id_componente


class LineaRecetaInvalidaError(NamisError):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)


class LineaRecetaNoEncontradaError(NamisError):
    def __init__(self, id_receta: int) -> None:
        super().__init__(f"No existe la línea de receta con id {id_receta}.")
        self.id_receta = id_receta


class VentaInvalidaError(NamisError):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)


class VentaNoEncontradaError(NamisError):
    def __init__(self, id_venta: int) -> None:
        super().__init__(f"No existe venta con id {id_venta}.")
        self.id_venta = id_venta


class PromocionInvalidaError(NamisError):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)


class PromocionNoEncontradaError(NamisError):
    def __init__(self, id_promocion: int) -> None:
        super().__init__(f"No existe promoción con id {id_promocion}.")
        self.id_promocion = id_promocion
