EXPLAIN ANALYZE
SELECT c.customer_city, COUNT(o.order_id) as total_ordenes
FROM orders o
         JOIN customers c ON o.customer_id = c.customer_id
         JOIN geolocation g ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix
WHERE o.order_status = 'delivered'
  -- ST_MakeEnvelope crea un área rectangular [xmin, ymin, xmax, ymax] (Coordenadas de control)
  AND ST_Contains(ST_MakeEnvelope(-47.5, -24.0, -46.0, -23.0, 4326), g.geom)
GROUP BY c.customer_city
ORDER BY total_ordenes DESC
    LIMIT 20;

