-- Agregar columna es_deudor a la tabla ventas
ALTER TABLE ventas ADD COLUMN es_deudor BOOLEAN DEFAULT FALSE;
