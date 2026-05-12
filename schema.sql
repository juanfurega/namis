CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    fecha_registro DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE productos ( -- PRODUCTO QUE SE VENDE
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL, 
    tamano_g INT, -- 350, 500 o 750
    es_endulzado BOOLEAN, -- 1 para Sí, 0 para Natural
    precio_actual DECIMAL(10, 2) NOT NULL, -- precio minorista (venta habitual)
    precio_mayorista DECIMAL(10, 2) NULL, -- NULL si el producto no se vende por mayor
    costo_actual DECIMAL(10, 2) NOT NULL -- Se debe actualizar cada vez que cambia el precio del insumo 
    -- otra opción es removerlo y que se calcule el costo actual de la receta
);

CREATE TABLE promociones (
    id_promocion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_promocion VARCHAR(50) NOT NULL, -- ej: 'Descuento 10%', 'Promo 2x1'
    id_producto_requerido INT NULL, -- ¿Qué producto activa la promo?
    cantidad_requerida INT NOT NULL, -- ¿Cuántos de ese producto hay que llevar?
    descuento_monto DECIMAL(10, 2) DEFAULT 0.00,
    descuento_porcentaje DECIMAL(5, 2) DEFAULT 0.00,
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    medio_pago VARCHAR(50), -- 'Transferencia', 'Efectivo', etc.
    red_social VARCHAR(50), -- 'Facebook', 'Instagram', etc.
    requiere_envio BOOLEAN DEFAULT FALSE,
    costo_envio DECIMAL(10, 2) DEFAULT 0.00,
    id_promocion INT NULL, -- Puede ser NULL si no hay promo aplicada
    es_precio_mayorista BOOLEAN NOT NULL DEFAULT FALSE, -- TRUE si la venta se armó con lista mayorista
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
    id_producto INT NOT NULL, -- PUEDE INCLUIR PRODUCTOS YA CREADOS (YOGURT POR EJEMPLO)
    id_insumo INT NOT NULL,
    cantidad_necesaria DECIMAL(10, 2) NOT NULL, -- Cuánto usas de la unidad_medida para un solo pote
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) ON DELETE RESTRICT
);