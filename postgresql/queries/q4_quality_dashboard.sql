EXPLAIN ANALYZE
SELECT p.product_id, p.sku,
       COUNT(oi.order_id) as items_vendidos,
       SUM(CASE WHEN o.delivered_customer_date > o.estimated_delivery_date THEN 1 ELSE 0 END) as entregas_con_retraso,
       AVG(oi.freight_value / (oi.price + 0.01)) as ratio_costo_envio
FROM products p JOIN order_items oi ON p.product_id = oi.product_id JOIN orders o ON oi.order_id = o.order_id AND oi.purchase_timestamp = o.purchase_timestamp
GROUP BY p.product_id, p.sku
HAVING COUNT(oi.order_id) > 5
ORDER BY entregas_con_retraso DESC
    LIMIT 20;
