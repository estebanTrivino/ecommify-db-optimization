# Diseño teórico de Replica Set y Sharding

## Replica Set

Topología propuesta:

- 1 nodo Primary para escrituras transaccionales.
- 2 nodos Secondary para lecturas analíticas.
- Despliegue distribuido en zonas de disponibilidad diferentes.

## Read Preference

```javascript
secondaryPreferred
```

Las consultas analíticas se descargan hacia réplicas secundarias para reducir la contención sobre el nodo primario.

## Write Concern

```javascript
{ w: "majority", j: true }
```

Las escrituras críticas deben confirmarse por mayoría y registrarse en journal.

## Read Concern

```javascript
{ readConcern: "local" }
```

Para analítica se acepta consistencia eventual a cambio de menor latencia.

## Sharding

Shard key propuesta:

```javascript
{ product_id_pg: "hashed" }
```

Justificación:

- Distribución homogénea de reseñas por producto.
- Mitigación de hotspots.
- Escalabilidad horizontal.
- Mejor distribución para pipelines de agregación de alto volumen.
- Posible co-localización lógica entre `products` y `reviews` usando la misma clave de integración.
