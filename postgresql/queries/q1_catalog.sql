EXPLAIN ANALYZE
SELECT p.product_id, p.product_weight_g, t.product_category_name_english
FROM products p
         JOIN product_category_name t ON p.product_category_name = t.product_category_name
WHERE p.product_category_name = 'esporte_lazer'
    LIMIT 20;

