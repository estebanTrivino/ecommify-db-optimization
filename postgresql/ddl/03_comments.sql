COMMENT ON TABLE product_category_name IS 'Tabla maestra de traducción de categorías de productos.';
COMMENT ON TABLE products IS 'Tabla maestra transaccional de productos.';
COMMENT ON TABLE customers IS 'Clientes asociados a órdenes de compra.';
COMMENT ON TABLE sellers IS 'Vendedores asociados a productos de la plataforma.';
COMMENT ON TABLE geolocation IS 'Catálogo de coordenadas geográficas para análisis espacial.';
COMMENT ON TABLE promotions IS 'Gestión de descuentos temporales aplicables a productos.';
COMMENT ON TABLE orders IS 'Tabla transaccional central de pedidos, particionada por purchase_timestamp.';
COMMENT ON TABLE order_items IS 'Detalle de productos contenidos en cada pedido.';
COMMENT ON TABLE payments IS 'Transacciones financieras y metadatos de pasarela en JSONB.';
