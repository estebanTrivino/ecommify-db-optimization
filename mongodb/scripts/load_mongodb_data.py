import os
import time
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm
from tabulate import tabulate
from bson import json_util


def print_banner(title: str) -> None:
    print("\n" + "=" * 80)
    print(title.upper())
    print("=" * 80)


def get_database():
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB", "ecommify_db")

    if not mongo_uri:
        raise ValueError("Falta configurar MONGO_URI en el archivo .env")

    client = MongoClient(mongo_uri)
    return client[db_name]


def setup_collections(db) -> None:
    print_banner("Etapa 1: Preparación de infraestructura y esquemas")
    start_time = time.time()

    collections = ["products", "reviews"]
    existing = db.list_collection_names()

    for collection_name in collections:
        if collection_name in existing:
            db.drop_collection(collection_name)
            print(f"Colección '{collection_name}' eliminada para aplicar nuevo esquema.")

    db.create_collection(
        "products",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["product_id_pg", "name", "display_price", "seller"],
                "properties": {
                    "product_id_pg": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "display_price": {"bsonType": "number"},
                    "seller": {
                        "bsonType": "object",
                        "required": ["seller_id_pg", "name", "reputation_score"],
                        "properties": {
                            "seller_id_pg": {"bsonType": "string"},
                            "name": {"bsonType": "string"},
                            "reputation_score": {"bsonType": "number"},
                        },
                    },
                },
            }
        },
    )

    db.create_collection(
        "reviews",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "order_id_pg",
                    "product_id_pg",
                    "customer",
                    "score",
                    "creation_date",
                ],
                "properties": {
                    "score": {"bsonType": "int"},
                },
            }
        },
    )

    print(f"Esquemas JSON aplicados correctamente en {round(time.time() - start_time, 2)}s.")


def prepare_mongodb_data(data_path: str):
    print_banner("Etapa 2: Extracción y transformación de datos")
    start_time = time.time()

    df_order_items = pd.read_csv(os.path.join(data_path, "olist_order_items_dataset.csv"))
    df_order_reviews = pd.read_csv(os.path.join(data_path, "olist_order_reviews_dataset.csv"))
    df_orders = pd.read_csv(os.path.join(data_path, "olist_orders_dataset.csv"))
    df_products = pd.read_csv(os.path.join(data_path, "olist_products_dataset.csv"))

    products = []

    for _, row in tqdm(df_products.head(1000).iterrows(), total=1000, desc="Productos"):
        products.append(
            {
                "product_id_pg": str(row["product_id"]),
                "name": str(row["product_category_name"])
                if pd.notna(row["product_category_name"])
                else "Sin Categoria",
                "display_price": 50.0,
                "seller": {
                    "seller_id_pg": "S_001",
                    "name": "Vendedor Default",
                    "reputation_score": 5.0,
                },
            }
        )

    df_full = df_order_reviews.merge(df_orders, on="order_id").merge(
        df_order_items, on="order_id"
    )

    reviews = []

    for _, row in tqdm(df_full.head(1000).iterrows(), total=1000, desc="Reseñas"):
        reviews.append(
            {
                "order_id_pg": str(row["order_id"]),
                "product_id_pg": str(row["product_id"]),
                "customer": {
                    "customer_id_pg": str(row["customer_id"]),
                    "first_name": "N/A",
                },
                "score": int(row["review_score"]),
                "creation_date": str(row["review_creation_date"]),
            }
        )

    print(f"Transformación finalizada en {round(time.time() - start_time, 2)}s.")
    return products, reviews


def load_data(db, products, reviews) -> None:
    print_banner("Etapa 3: Ingestión a MongoDB Atlas")

    if products:
        db["products"].insert_many(products)

    if reviews:
        db["reviews"].insert_many(reviews)

    print("Documentos insertados exitosamente.")


def run_optimization_evidence(db) -> None:
    print_banner("Etapa 4: Evidencia cuantitativa de rendimiento")

    pipeline_base = [
        {"$match": {"score": {"$lt": 3}}},
        {
            "$group": {
                "_id": "$product_id_pg",
                "promedio_score": {"$avg": "$score"},
                "total_reviews": {"$sum": 1},
            }
        },
        {"$sort": {"total_reviews": -1}},
        {"$limit": 5},
    ]

    explain_cmd = {
        "explain": {
            "aggregate": "reviews",
            "pipeline": pipeline_base,
            "cursor": {},
        },
        "verbosity": "executionStats",
    }

    print("1. Midiendo rendimiento antes de la optimización...")
    db["reviews"].drop_indexes()

    before = db.command(explain_cmd)
    before_stats = before.get("stages", [{}])[0].get("$cursor", {}).get(
        "executionStats", before.get("executionStats", {})
    )

    before_time = before_stats.get("executionTimeMillis", 0)
    before_docs = before_stats.get("totalDocsExamined", 0)

    print("2. Creando índices compuestos y parciales...")
    start_idx = time.time()

    db["products"].create_index([("product_id_pg", 1)], unique=True)
    db["reviews"].create_index([("product_id_pg", 1), ("score", -1)])
    db["reviews"].create_index(
        [("score", 1)],
        partialFilterExpression={"score": {"$lt": 3}},
    )

    print(f"Índices creados en {round(time.time() - start_idx, 2)}s.")

    print("3. Midiendo rendimiento después de la optimización...")
    after = db.command(explain_cmd)
    after_stats = after.get("stages", [{}])[0].get("$cursor", {}).get(
        "executionStats", after.get("executionStats", {})
    )
    after_plan = after.get("stages", [{}])[0].get("$cursor", {}).get(
        "queryPlanner", {}
    ).get("winningPlan", {})

    after_time = after_stats.get("executionTimeMillis", 0)
    after_docs = after_stats.get("totalDocsExamined", 0)

    saving = ((before_docs - after_docs) / max(1, before_docs)) * 100

    table = [
        ["Estrategia de búsqueda", "COLLSCAN", "IXSCAN"],
        ["Documentos escaneados", before_docs, f"{after_docs} (ahorro {saving:.2f}%)"],
        ["Tiempo de ejecución", f"{before_time} ms", f"{after_time} ms"],
    ]

    print(tabulate(table, headers=["Métrica", "Antes", "Después"], tablefmt="fancy_grid"))

    pipeline_complete = pipeline_base + [
        {
            "$lookup": {
                "from": "products",
                "localField": "_id",
                "foreignField": "product_id_pg",
                "as": "info",
            }
        },
        {"$unwind": {"path": "$info", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 1,
                "product_name": {
                    "$ifNull": ["$info.name", "Nombre no disponible"],
                },
                "promedio_score": 1,
                "total_reviews": 1,
            }
        },
    ]

    print_banner("Resultado final del módulo analítico")
    results = list(db["reviews"].aggregate(pipeline_complete))

    for result in results:
        print(
            f"Producto: {result['_id']} - "
            f"{result['product_name'][:25]} | "
            f"Promedio: {round(result['promedio_score'], 1)} | "
            f"Reseñas críticas: {result['total_reviews']}"
        )

    print_banner("Plan de ejecución ganador")
    print(json_util.dumps(after_plan, indent=2))


def main() -> None:
    load_dotenv()

    data_path = os.getenv("DATA_PATH", "./data/raw")
    db = get_database()

    setup_collections(db)
    products, reviews = prepare_mongodb_data(data_path)
    load_data(db, products, reviews)
    run_optimization_evidence(db)

    print_banner("Pipeline del módulo analítico finalizado exitosamente")


if __name__ == "__main__":
    main()