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
