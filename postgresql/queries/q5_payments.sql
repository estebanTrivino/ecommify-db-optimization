EXPLAIN ANALYZE
SELECT p.order_id, p.payment_value,
       p.gateway_response->>'processor' as pasarela_utilizada,
    p.gateway_response->'meta'->>'installments_selected' as cuotas_solicitadas
FROM payments p
WHERE p.payment_value > 300
  AND p.gateway_response->>'status' = 'approved' -- Extracción en caliente de texto JSONB
  AND p.gateway_response->'meta'->>'fallback_payment' = 'credit_card'
ORDER BY p.payment_value DESC
    LIMIT 30;

