import os
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from tqdm import tqdm

# Permite importar módulos desde la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from mongodb.schema.validators import create_validators
from mongodb.pipelines.reviews_pipeline import pipeline_completo
from mongodb.pipelines.explain_pipeline import run_pipeline_explain


def print_banner(title: str) -> None:
    print("\n" + "=" * 80)
    print(title.upper())
    print("=" * 80)


def get_database():
    """
    Obtiene conexión a MongoDB Atlas.
    """
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "ecommify_db")

    if not mongo_uri:
        raise ValueError(
            "No se encontró MONGO_URI en el archivo .env"
        )

    client = MongoClient(mongo_uri)
    client.admin.command("ping")
    print(f"[OK] Conexión exitosa a MongoDB Atlas - Base de datos: {mongo_db}")

    return client[mongo_db]

def recreate_collections(db):
    """
    Elimina colecciones existentes y crea nuevamente
    los validadores JSON Schema.
    """
    print_banner("Etapa 1 - Preparación de infraestructura")
    collections = ["products", "reviews"]
    existing = db.list_collection_names()

    for collection_name in collections:
        if collection_name in existing:
            db.drop_collection(collection_name)
            print(f"[INFO] Colección '{collection_name}' eliminada")

    create_validators(db)
    print("[OK] Validadores JSON Schema aplicados correctamente")

def load_source_data(data_path: str):
    """
    Carga datasets CSV originales.
    """
    print_banner("Etapa 2 - Lectura de datasets")

    datasets = {
        "products":
            pd.read_csv(
                os.path.join(
                    data_path,
                    "olist_products_dataset.csv"
                )
            ),
        "orders":
            pd.read_csv(
                os.path.join(
                    data_path,
                    "olist_orders_dataset.csv"
                )
            ),
        "order_items":
            pd.read_csv(
                os.path.join(
                    data_path,
                    "olist_order_items_dataset.csv"
                )
            ),
        "order_reviews":
            pd.read_csv(
                os.path.join(
                    data_path,
                    "olist_order_reviews_dataset.csv"
                )
            )
    }

    print("[OK] Datasets cargados")

    return datasets

def transform_products(df_products):
    """
    Convierte productos relacionales a documentos.
    """
    print("[INFO] Transformando catálogo de productos...")
    products = []
    limit = min(len(df_products), 1000)

    for _, row in tqdm(df_products.head(limit).iterrows(), total=limit, desc="Productos"):
        products.append(
            {
                "product_id_pg":
                    str(row["product_id"]),
                "name":
                    (
                        str(
                            row["product_category_name"]
                        )
                        if pd.notna(
                            row["product_category_name"]
                        )
                        else "Sin Categoria"
                    ),
                "display_price":
                    50.0,
                "seller": {
                    "seller_id_pg":
                        "S_001",
                    "name":
                        "Vendedor Default",
                    "reputation_score":
                        5.0
                }
            }
        )

    return products


def transform_reviews(df_reviews, df_orders, df_items):
    """
    Construye documentos de reviews.
    """
    print("[INFO] Transformando reseñas...")

    df_full = (
        df_reviews
        .merge(
            df_orders,
            on="order_id"
        )
        .merge(
            df_items,
            on="order_id"
        )
    )

    reviews = []
    limit = min(len(df_full), 1000)

    for _, row in tqdm(df_full.head(limit).iterrows(), total=limit, desc="Reviews"):
        reviews.append(
            {
                "order_id_pg":
                    str(row["order_id"]),
                "product_id_pg":
                    str(row["product_id"]),
                "customer": {
                    "customer_id_pg":
                        str(row["customer_id"]),
                    "first_name":
                        "N/A"
                },
                "score":
                    int(row["review_score"]),
                "creation_date":
                    str(
                        row[
                            "review_creation_date"
                        ]
                    )
            }
        )

    return reviews


def insert_documents(db, products, reviews):
    """
    Inserta documentos en MongoDB.
    """
    print_banner("Etapa 3 - Inserción de documentos")

    if products:
        db["products"].insert_many(products)
        print(f"[OK] {len(products)} productos insertados")

    if reviews:
        db["reviews"].insert_many(reviews)
        print(f"[OK] {len(reviews)} reseñas insertadas")


def execute_analytics(db):
    """
    Ejecuta explain() y pipeline final.
    """
    print_banner("Etapa 4 - Optimización y análisis")
    metrics = run_pipeline_explain(db)
    print_banner("Top productos con reseñas críticas")

    results = list(
        db["reviews"].aggregate(
            pipeline_completo
        )
    )

    for row in results:
        print(
            f"Producto: {row['_id']} | "
            f"Nombre: {row.get('product_name', 'N/D')} | "
            f"Promedio: {round(row['promedio_score'], 2)} | "
            f"Reviews: {row['total_reviews']}"
        )

    return metrics

def main():
    start_time = time.time()
    load_dotenv()
    data_path = os.getenv("DATA_PATH", "./data/raw")
    db = get_database()
    recreate_collections(db)
    datasets = load_source_data(data_path)
    products = transform_products(datasets["products"])

    reviews = transform_reviews(
        datasets["order_reviews"],
        datasets["orders"],
        datasets["order_items"]
    )

    insert_documents(db, products, reviews)
    execute_analytics(db)
    print_banner("Proceso finalizado")
    print(
        f"Tiempo total: "
        f"{round(time.time() - start_time, 2)} segundos"
    )

if __name__ == "__main__":
    main()