# Ecommify - Optimización de Rendimiento en PostgreSQL y MongoDB

Repositorio académico de la asignatura **Diseño y Optimización de Bases de Datos**. Contiene una implementación reproducible de optimización de rendimiento para la plataforma Ecommify, usando **PostgreSQL/Supabase** como motor transaccional y **MongoDB Atlas** como motor documental analítico.

## Objetivo

Implementar, ejecutar y documentar optimizaciones de rendimiento en PostgreSQL y MongoDB mediante:

- Esquema relacional con tipos avanzados y extensiones.
- Particionamiento declarativo en PostgreSQL.
- Índices especializados B-Tree, GIN, GiST y JSONB.
- Modelo documental en MongoDB con JSON Schema.
- Índices compuestos y parciales.
- Aggregation pipelines optimizados.
- Evidencias cuantitativas antes/después.
- Diseño teórico de Replica Set y Sharding.

## Estructura

```text
ecommify-db-optimization/
├── docs/
├── postgresql/
│   ├── ddl/
│   ├── indexes/
│   ├── queries/
│   ├── scripts/
│   └── notebooks/
├── mongodb/
│   ├── schema/
│   ├── indexes/
│   ├── pipelines/
│   ├── scripts/
│   ├── sharding/
│   └── notebooks/
├── data/
├── requirements.txt
├── .env.example
└── README.md
```

## Requisitos

- Python 3.10+
- PostgreSQL/Supabase con PostGIS habilitable
- MongoDB Atlas
- Mongo Shell o MongoDB Compass para ejecutar scripts `.js`
- Dataset Olist ubicado en `data/raw/`

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

Crear archivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Configurar:

```env
POSTGRES_URL=postgresql://usuario:password@host:puerto/database
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
MONGO_DB=ecommify_db
DATA_PATH=./data/raw
```

## Ejecución PostgreSQL

Ejecutar los scripts SQL en este orden:

```bash
psql "$POSTGRES_URL" -f postgresql/ddl/00_extensions.sql
psql "$POSTGRES_URL" -f postgresql/ddl/01_schema.sql
psql "$POSTGRES_URL" -f postgresql/ddl/02_partitions.sql
psql "$POSTGRES_URL" -f postgresql/ddl/03_comments.sql
```

Cargar datos:

```bash
python postgresql/scripts/load_postgresql_data.py
```

Ejecutar consultas antes de crear índices para obtener línea base:

```bash
psql "$POSTGRES_URL" -f postgresql/queries/q1_catalog.sql
psql "$POSTGRES_URL" -f postgresql/queries/q2_order_tracking.sql
psql "$POSTGRES_URL" -f postgresql/queries/q3_geographic.sql
psql "$POSTGRES_URL" -f postgresql/queries/q4_quality_dashboard.sql
psql "$POSTGRES_URL" -f postgresql/queries/q5_payments.sql
```

Crear índices:

```bash
psql "$POSTGRES_URL" -f postgresql/indexes/04_indexes.sql
```

Ejecutar de nuevo las consultas para comparar resultados.

## Ejecución MongoDB

Cargar y optimizar desde Python:

```bash
python mongodb/scripts/load_mongodb_data.py
```

Opcionalmente, ejecutar manualmente los scripts en Mongo Shell o Compass:

```javascript
load("mongodb/schema/01_products_validator.py")
load("mongodb/schema/02_reviews_validator.py")
load("mongodb/indexes/03_indexes.py")
load("mongodb/pipelines/04_reviews_aggregation_pipeline.py")
load("mongodb/pipelines/05_reviews_explain.py")
```

## Resultados PostgreSQL

| Consulta | Antes | Después | Mejora aproximada |
|---|---:|---:|---:|
| Q1 - Catálogo | 1599.091 ms | 45.109 ms | 97.18% |
| Q2 - Rastreo | 477.887 ms | 12.476 ms | 97.39% |
| Q3 - Geográfico | 739.227 ms | 86.699 ms | 88.27% |
| Q4 - Dashboard | 1890.701 ms | 936.741 ms | 50.45% |
| Q5 - Pagos | 1109.451 ms | 23.963 ms | 97.84% |

Los planes de ejecución completos están en `postgresql/results/`.

## Resultados MongoDB

La optimización transforma consultas con escaneo completo de colección en planes que usan índices compuestos y parciales. Se evalúa mediante `executionStats`, revisando principalmente:

- `executionTimeMillis`
- `totalDocsExamined`
- plan ganador (`winningPlan`)
- uso de `IXSCAN` frente a `COLLSCAN`

## Decisiones técnicas clave

1. **PostgreSQL como sistema transaccional**: mantiene integridad sobre pedidos, clientes y pagos.
2. **MongoDB como motor analítico**: soporta análisis de productos y reseñas mediante documentos y agregaciones.
3. **Particionamiento temporal en orders**: reduce el alcance de lectura sobre datos históricos.
4. **Índices especializados**: cada patrón de consulta usa el tipo de índice adecuado.
5. **Consistencia eventual**: MongoDB recibe datos transformados para análisis sin afectar la operación transaccional.

## Integrantes

- Juan Daniel Valderrama Pérez
- Jorge Esteban Triviño Correa
- Javier Andres Baron Fontanilla

## Universidad

Universidad de La Sabana  
Facultad de Ingeniería  
2026
