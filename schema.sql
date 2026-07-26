CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    fecha_registro DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE productos ( -- PRODUCTO QUE SE VENDE
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL, 
    tamano_g INT NOT NULL, -- 350, 500 o 750 (obligatorio)
    es_endulzado BOOLEAN, -- 1 para Sí, 0 para Natural
    precio_actual DECIMAL(10, 2) NOT NULL, -- precio de venta
    costo_actual DECIMAL(10, 2) NOT NULL -- Se debe actualizar cada vez que cambia el precio del insumo 
    -- otra opción es removerlo y que se calcule el costo actual de la receta
);

CREATE TABLE promociones (
    id_promocion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_promocion VARCHAR(50) NOT NULL,
    descuento_porcentaje DECIMAL(5, 2) NOT NULL, -- ej: 20.00 = 20%
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE promocion_requisitos (
    id_requisito INT AUTO_INCREMENT PRIMARY KEY,
    id_promocion INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad_requerida INT NOT NULL, -- mínimo de unidades de ese producto en la venta
    FOREIGN KEY (id_promocion) REFERENCES promociones(id_promocion) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT,
    UNIQUE KEY uq_promo_producto (id_promocion, id_producto)
);

CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    medio_pago VARCHAR(50), -- 'Transferencia', 'Efectivo', etc.
    red_social VARCHAR(50), -- Medio de comunicación informativo: 'wsp', 'ig', 'msn'
    requiere_envio BOOLEAN DEFAULT FALSE,
    costo_envio DECIMAL(10, 2) DEFAULT 0.00,
    id_promocion INT NULL, -- Promo aplicada automáticamente; NULL si ninguna califica
    monto_descontado DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_cobrado DECIMAL(10, 2) NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_promocion) REFERENCES promociones(id_promocion)
);

CREATE TABLE detalle_ventas (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario_cobrado DECIMAL(10, 2) NOT NULL,
    costo_unitario_historico DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE insumos ( -- MATERIA PRIMA
    id_insumo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_insumo VARCHAR(100) NOT NULL UNIQUE,
    unidad_medida VARCHAR(20) NOT NULL -- Ej: 'ml', 'gramos', 'unidades'
);

CREATE TABLE insumos_historial_precios ( -- HISTORIAL DE PRECIOS DE LA MATERIA PRIMA
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_insumo INT NOT NULL,
    cantidad_paquete DECIMAL(10, 2) NOT NULL, 
    precio_paquete DECIMAL(10, 2) NOT NULL,   
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) ON DELETE CASCADE
); -- El precio de los insumos es el último que se registró (el más reciente)

CREATE TABLE recetas (
    id_receta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL, -- Producto dueño de la receta (ej: postre)
    id_insumo INT NULL, -- Línea de materia prima (XOR con id_producto_componente)
    id_producto_componente INT NULL, -- Línea de sub-receta (ej: yogurt dentro de postre)
    cantidad_necesaria DECIMAL(10, 2) NOT NULL, -- En unidad del insumo, o gramos del producto componente
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) ON DELETE RESTRICT,
    FOREIGN KEY (id_producto_componente) REFERENCES productos(id_producto) ON DELETE RESTRICT,
    CHECK (
        (id_insumo IS NOT NULL AND id_producto_componente IS NULL)
        OR (id_insumo IS NULL AND id_producto_componente IS NOT NULL)
    )
);