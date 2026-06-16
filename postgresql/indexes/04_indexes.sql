-- Índice GIN de Trigramas Parcial para búsquedas de texto difuso en productos activos
CREATE INDEX IF NOT EXISTS idx_products_sku_trgm
ON products USING gin (sku gin_trgm_ops)
WHERE (is_active = TRUE);

-- Índice B-tree Simple local sobre la llave foránea de pedidos
CREATE INDEX IF NOT EXISTS idx_orders_customer_id_local
ON orders (customer_id);

-- Índice GiST Espacial jerárquico para optimizar consultas de coordenadas vectoriales
CREATE INDEX IF NOT EXISTS idx_geolocation_geom_gist
ON geolocation USING gist (geom);

-- Índice GIN para JSONB especializado con mapeo de rutas óptimas de atributos binarios
CREATE INDEX IF NOT EXISTS idx_payments_gateway_extract
ON payments USING gin (gateway_response jsonb_path_ops);
