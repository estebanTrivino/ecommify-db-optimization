# Ecommify - Optimización de Rendimiento en PostgreSQL y MongoDB

## Descripción del Proyecto

Este repositorio contiene la implementación técnica de optimización de rendimiento para la plataforma **Ecommify**, desarrollada en el contexto de la asignatura **Diseño y Optimización de Bases de Datos**.

El proyecto implementa una arquitectura de persistencia híbrida, utilizando **PostgreSQL/Supabase** como sistema transaccional principal y **MongoDB Atlas** como motor documental para análisis de productos y reseñas.

La solución incluye estrategias de optimización mediante indexación especializada, particionamiento, validación documental, aggregation pipelines, diseño teórico de sharding y análisis cuantitativo de rendimiento antes y después de la optimización.

## Objetivos

* Implementar un modelo relacional optimizado en PostgreSQL.
* Implementar un modelo documental optimizado en MongoDB Atlas.
* Aplicar técnicas de indexación avanzada en ambos motores.
* Medir mejoras mediante `EXPLAIN ANALYZE` en PostgreSQL y `explain("executionStats")` en MongoDB.
* Diseñar una estrategia teórica de sharding y replica sets.
* Documentar evidencias cuantitativas de mejora de rendimiento.

## Arquitectura General

La solución adopta un enfoque de persistencia políglota:

* **PostgreSQL**: sistema transaccional para clientes, pedidos, pagos, vendedores y productos.
* **MongoDB Atlas**: sistema analítico para productos enriquecidos, reseñas y consultas agregadas.
* **Python/Colab**: procesos de carga, transformación de datos y pruebas de rendimiento.

## Estructura del Repositorio

```text
ecommify-db-optimization/
│
├── docs/
│   └── Documento técnico final
│
├── postgresql/
│   ├── ddl/
│   ├── indexes/
│   ├── queries/
│   ├── results/
│   └── notebooks/
│
├── mongodb/
│   ├── schema/
│   ├── indexes/
│   ├── pipelines/
│   ├── sharding/
│   └── notebooks/
│
├── evidence/
│   ├── postgresql/
│   └── mongodb/
│
└── data/
```

## Implementación PostgreSQL

La implementación en PostgreSQL incluye:

* Creación de tablas relacionales.
* Constraints y llaves foráneas.
* Uso de tipos avanzados como `JSONB`, `ARRAY` y `TSTZRANGE`.
* Extensiones:

  * `pgcrypto`
  * `postgis`
  * `pg_trgm`
* Particionamiento declarativo por rango temporal en la tabla `orders`.
* Índices especializados:

  * B-Tree para claves relacionales.
  * GIN con `pg_trgm` para búsquedas textuales.
  * GiST para consultas espaciales.
  * GIN sobre `JSONB` para datos semiestructurados.

## Implementación MongoDB

La implementación en MongoDB Atlas incluye:

* Colección `products`.
* Colección `reviews`.
* Validación mediante JSON Schema.
* Índices compuestos sobre `product_id_pg` y `score`.
* Índices parciales para reseñas críticas.
* Aggregation pipelines con:

  * `$match`
  * `$group`
  * `$sort`
  * `$limit`
  * `$lookup`
  * `$unwind`
  * `$project`

## Resultados de Optimización

### PostgreSQL

| Consulta        | Tiempo antes | Tiempo después | Mejora aproximada |
| --------------- | -----------: | -------------: | ----------------: |
| Q1 - Catálogo   |   1599.09 ms |       45.11 ms |            97.18% |
| Q2 - Rastreo    |    477.89 ms |       12.48 ms |            97.39% |
| Q3 - Geográfico |    739.23 ms |       86.70 ms |            88.27% |
| Q4 - Dashboard  |   1890.70 ms |      936.74 ms |            50.45% |
| Q5 - Pagos      |   1109.45 ms |       23.96 ms |            97.84% |

### MongoDB

| Consulta     | Tiempo antes | Tiempo después | Optimización aplicada  |
| ------------ | -----------: | -------------: | ---------------------- |
| Q-Calidad    |      1200 ms |          45 ms | Índice parcial         |
| Q-Lookup     |      1500 ms |         110 ms | Índice en foreignField |
| Q-Agregación |       950 ms |          60 ms | Índice compuesto       |

## Sincronización entre Sistemas

PostgreSQL actúa como sistema de registro principal. MongoDB recibe datos transformados para fines analíticos mediante procesos ETL desarrollados en Python.

La estrategia de consistencia adoptada es **consistencia eventual**, dado que MongoDB soporta consultas analíticas y no operaciones transaccionales críticas.

## Diseño Teórico de Escalabilidad

Para MongoDB se propone:

* Replica Set de tres nodos.
* Lecturas analíticas con `secondaryPreferred`.
* Escrituras críticas con `writeConcern: majority`.
* Sharding sobre:

```javascript
{ product_id_pg: "hashed" }
```

Esta shard key busca distribuir homogéneamente los documentos y reducir hotspots.

## Requisitos

* Python 3.10 o superior.
* PostgreSQL/Supabase.
* MongoDB Atlas.
* Google Colab o entorno local compatible.
* Librerías principales:

  * `pandas`
  * `sqlalchemy`
  * `psycopg2-binary`
  * `pymongo`
  * `tabulate`
  * `tqdm`

## Ejecución General

### PostgreSQL

1. Ejecutar los scripts DDL ubicados en `postgresql/ddl/`.
2. Cargar los datos mediante el notebook de PostgreSQL.
3. Ejecutar las consultas sin optimización.
4. Crear los índices definidos en `postgresql/indexes/`.
5. Ejecutar nuevamente las consultas optimizadas.
6. Comparar resultados en `postgresql/results/`.

### MongoDB

1. Crear el cluster en MongoDB Atlas.
2. Ejecutar el notebook `actividad5_nosql.py`.
3. Crear colecciones con validación JSON Schema.
4. Cargar productos y reseñas.
5. Ejecutar pruebas antes y después de índices.
6. Revisar planes de ejecución y métricas.

## Evidencias

Las evidencias se encuentran en la carpeta `evidence/` e incluyen:

* Resultados de `EXPLAIN ANALYZE`.
* Resultados de `executionStats`.
* Capturas de Supabase.
* Capturas de MongoDB Atlas.
* Gráficas comparativas de rendimiento.
* Tablas de mejora antes/después.

## Integrantes

* Juan Daniel Valderrama Pérez
* Jorge Esteban Triviño Correa
* Javier Andres Baron Fontanilla

## Asignatura

Diseño y Optimización de Bases de Datos
Universidad de La Sabana
Facultad de Ingeniería
2026
