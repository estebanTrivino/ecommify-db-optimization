EXPLAIN ANALYZE
SELECT o.order_id, o.order_status, o.purchase_timestamp, oi.price, p.payment_type, p.payment_value
FROM customers c
         JOIN orders o ON c.customer_id = o.customer_id
         JOIN order_items oi ON o.order_id = oi.order_id AND o.purchase_timestamp = oi.purchase_timestamp
         JOIN payments p ON o.order_id = p.order_id AND o.purchase_timestamp = p.purchase_timestamp
WHERE c.customer_unique_id = '871766c5855e863f64db0585a72663bc' -- Cliente con múltiples compras históricas
ORDER BY o.purchase_timestamp DESC;

