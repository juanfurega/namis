-- Importes cobrados por cada medio de pago.
ALTER TABLE ventas ADD COLUMN monto_efectivo DECIMAL(10, 2) NULL;
ALTER TABLE ventas ADD COLUMN monto_transferencia DECIMAL(10, 2) NULL;

-- Conserva el desglose correcto para las ventas creadas antes de esta mejora.
UPDATE ventas
SET monto_efectivo = CASE WHEN medio_pago = 'efectivo' THEN total_cobrado ELSE 0.00 END,
    monto_transferencia = CASE WHEN medio_pago = 'transferencia' THEN total_cobrado ELSE 0.00 END
WHERE monto_efectivo IS NULL OR monto_transferencia IS NULL;
