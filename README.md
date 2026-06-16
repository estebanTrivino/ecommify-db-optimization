<h1 align="center">Ecommify Database Optimization</h1>

<div align="center">
  <img src="https://img.shields.io/badge/SQL-Orange?style=for-the-badge&logo=sql&logoColor=white" alt="SQL Badge"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB Badge"/>
  <img src="https://img.shields.io/badge/Universidad-La_Sabana-0033A0?style=for-the-badge" alt="UNISABANA Badge"/>
  <img src="https://img.shields.io/badge/Maestr%C3%ADa-Arquitectura_de_Software-2b9348?style=for-the-badge" alt="Maestria Badge"/>
  <img src="https://img.shields.io/badge/Asignatura-Dise%C3%B1o%20y%20Optimizaci%C3%B3n%20de%20Bases%20de%20Datos-8A2BE2?style=for-the-badge" alt="Asignatura Badge"/>
  <img src="https://img.shields.io/badge/Status-Completado-success?style=for-the-badge" alt="Status Badge"/>
</div>

<p align="center">
  <i>Archivo correspondiente a las Actividades Evaluativas de Diseño y Optimización de Bases de Datos.</i>
</p>

---

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura de la Solución](#arquitectura-de-la-solución)  
3. [Estructura del Repositorio](#estructura-del-repositorio)
4. [Configuración del Entorno](#configuración-del-entorno)
5. [Variables de Entorno](#variables-de-entorno)
6. [Ejecución PostgreSQL](#ejecución-postgresql)
7. [Ejecución MongoDB](#ejecución-mongodb)
8. [Flujo ETL](#flujo-etl)
9. [Principales Optimizaciones Implementadas](#principales-optimizaciones-implementadas)
10. [Documentación](#documentación)
11. [Notebooks Académicos](#notebooks-académicos)
12. [Integrantes](#integrantes)

---

## Descripción General

Este repositorio contiene la implementación desarrollada para la actividad de optimización de bases de datos de la plataforma **Ecommify**, utilizando una arquitectura de persistencia híbrida basada en:

* PostgreSQL (OLTP)
* MongoDB Atlas (OLAP)
* Python para procesos ETL
* Supabase como proveedor PostgreSQL

El proyecto implementa estrategias de optimización de rendimiento mediante indexación especializada, particionamiento, validación documental, aggregation pipelines y análisis cuantitativo de consultas.

### Video de presentación de la Solución

[![Ecommify Database Optimization](https://img.youtube.com/vi/YJ5iH-2D840/hqdefault.jpg)](https://drive.google.com/file/d/11Sz5RFka1riZqh1UkiWITrQ7q_mB0cen/view?usp=sharing)

---

## Arquitectura de la Solución

La solución adopta un enfoque de **Persistencia Políglota (Polyglot Persistence)**.

### PostgreSQL

Responsable de:

* Clientes
* Productos
* Vendedores
* Pedidos
* Pagos
* Geolocalización
* Promociones

Características implementadas:

* Particionamiento por rango temporal
* Índices B-Tree
* Índices GIN
* Índices GiST
* JSONB
* PostGIS
* pg_trgm

### MongoDB Atlas

Responsable de:

* Catálogo analítico de productos
* Reseñas de clientes
* Consultas agregadas
* Análisis de reputación de productos

Características implementadas:

* JSON Schema Validation
* Índices compuestos
* Índices parciales
* Aggregation Pipelines
* Diseño teórico de Replica Sets
* Diseño teórico de Sharding

---

## Estructura del Repositorio

```text
ecommify-db-optimization/
│
├── data/
│   └── raw/
│       ├── olist_customers_dataset.csv
│       ├── olist_geolocation_dataset.csv
│       ├── olist_order_items_dataset.csv
│       ├── olist_order_payments_dataset.csv
│       ├── olist_order_reviews_dataset.csv
│       ├── olist_orders_dataset.csv
│       ├── olist_products_dataset.csv
│       ├── olist_sellers_dataset.csv
│       └── product_category_name_translation.csv
│
├── docs/
│   └── Optimización_de_Rendimiento_en_PostgreSQL&MongoDB.pdf
│
├── etl/
│   ├── postgresql/
│   │   └── etl_postgresql.py
│   │
│   └── mongodb/
│       └── etl_mongodb.py
│
├── mongodb/
│   ├── schema/
│   │   └── validators.py
│   ├── indexes/
│   │   └── indexes.py
│   ├── pipelines/
│   │   ├── explain_pipeline.py
│   │   └── reviews_pipeline.py
│   └── sharding/
│       └── sharding_replica_set_design.py
│
├── notebooks/
│   ├── postgresql/
│   │   └── Modelado_de_Tablas_PostgreSQL.ipynb
│   └── mongodb/
│       ├── Actividad5_NOSQL.ipynb
│       └── Modelado_de_Documentos_NoSQL.ipynb
│
├── postgresql/
│   ├── ddl/
│   │   ├── 00_extensions.sql
│   │   ├── 01_schema.sql
│   │   ├── 02_partitions.sql
│   │   └── 03_comments.sql
│   ├── indexes/
│   │   └── 04_indexes.sql
│   └── queries/
│       ├── q1_catalog.sql
│       ├── q2_order_tracking.sql
│       ├── q3_geographic.sql
│       ├── q4_quality_dashboard.sql
│       ├── q5_payments.sql
│       └── run_all_queries.sql
│
├── results/
│   ├── Resultado_Queries_Con_Optimizacion.txt
│   └── Resultado_Queries_Sin_Optimizacion.txt
│
├── .env.example
├── README.md
└── requirements.txt
```

---

## Configuración del Entorno

### 1. Clonar el repositorio

```bash
git clone https://github.com/estebanTrivino/ecommify-db-optimization.git
cd ecommify-db-optimization
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Variables de Entorno

Crear un archivo `.env` a partir de `.env.example`.

Ejemplo:

```env
POSTGRES_URL=postgresql://usuario:password@host:5432/postgres

MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/

MONGO_DB=ecommify_db

DATA_PATH=./data/raw
```

---

## Ejecución PostgreSQL

### Crear estructura

Ejecutar en orden:

```sql
postgresql/ddl/00_extensions.sql

postgresql/ddl/01_schema.sql

postgresql/ddl/02_partitions.sql

postgresql/indexes/04_indexes.sql
```

### Poblar PostgreSQL

```bash
python etl/postgresql/etl_postgresql.py
```

El proceso realiza:

* Lectura de CSV
* Transformación de datos
* Generación de atributos derivados
* Construcción de objetos PostGIS
* Inserción en PostgreSQL

---

## Ejecución MongoDB

### Crear colecciones y validadores

Los validadores JSON Schema se encuentran en:

```text
mongodb/schema/
```

### Poblar MongoDB

```bash
python etl/mongodb/etl_mongodb.py
```

El proceso realiza:

* Lectura de datasets
* Conversión relacional → documental
* Creación de documentos products
* Creación de documentos reviews
* Inserción en MongoDB Atlas
* Creación de índices
* Ejecución de aggregation pipelines
* Análisis de rendimiento mediante explain()

---

## Flujo ETL

### PostgreSQL

```text
CSV
 ↓
Transformación
 ↓
PostgreSQL
```

### MongoDB

```text
CSV
 ↓
Transformación Documental
 ↓
MongoDB Atlas
 ↓
Aggregation Pipelines
```

---

## Principales Optimizaciones Implementadas

### PostgreSQL

* Particionamiento por rango temporal
* Índices GIN para búsquedas textuales
* Índices GiST para consultas geográficas
* Índices JSONB
* Optimización de consultas críticas

### MongoDB

* Índices compuestos ESR
* Índices parciales
* Aggregation Pipelines optimizados
* Diseño de Sharding
* Replica Sets

---

## Documentación

La documentación técnica completa del proyecto se encuentra en:

```text
docs/
```

---

## Notebooks Académicos

Los notebooks originales utilizados durante el desarrollo se encuentran en:

```text
notebooks/
```

Estos archivos documentan el proceso experimental realizado durante la actividad académica y sirven como respaldo de las decisiones de diseño y optimización implementadas.

---

## Integrantes

* Jorge Esteban Triviño Correa
* Juan Daniel Valderrama Pérez
* Javier Andrés Barón Fontanilla

---

## Asignatura

Diseño y Optimización de Bases de Datos

Maestría en Arquitectura de Software
