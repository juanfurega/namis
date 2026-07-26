-- Agregar columna a_la_venta a la tabla productos
ALTER TABLE productos ADD COLUMN a_la_venta BOOLEAN DEFAULT FALSE NOT NULL;
