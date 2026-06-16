import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


def load_csv_files(base_path: str) -> dict:
    return {
        "sellers": pd.read_csv(os.path.join(base_path, "olist_sellers_dataset.csv")),
        "orders": pd.read_csv(os.path.join(base_path, "olist_orders_dataset.csv")),
        "customers": pd.read_csv(os.path.join(base_path, "olist_customers_dataset.csv")),
        "products": pd.read_csv(os.path.join(base_path, "olist_products_dataset.csv")),
        "geolocation": pd.read_csv(os.path.join(base_path, "olist_geolocation_dataset.csv")),
        "product_category_name": pd.read_csv(os.path.join(base_path, "product_category_name_translation.csv")),
        "order_reviews": pd.read_csv(os.path.join(base_path, "olist_order_reviews_dataset.csv")),
        "order_payments": pd.read_csv(os.path.join(base_path, "olist_order_payments_dataset.csv")),
        "order_items": pd.read_csv(os.path.join(base_path, "olist_order_items_dataset.csv")),
    }


def prepare_postgresql_data(raw: dict) -> dict:
    df_sellers = raw["sellers"]
    df_orders = raw["orders"]
    df_customers = raw["customers"]
    df_products = raw["products"]
    df_geolocation = raw["geolocation"]
    df_product_category_name = raw["product_category_name"]
    df_order_payments = raw["order_payments"]
    df_order_items = raw["order_items"]

    print("[INFO] Excluyendo olist_order_reviews_dataset.csv de PostgreSQL por decisión de diseño NoSQL.")

    df_product_category_name = df_product_category_name.drop_duplicates(
        subset=["product_category_name"]
    )

    df_products["sku"] = "SKU-" + df_products["product_id"].str[:8].str.upper()
    df_products["dimensions_cm"] = df_products.apply(
        lambda r: [
            int(r["product_length_cm"]) if pd.notnull(r["product_length_cm"]) else 0,
            int(r["product_width_cm"]) if pd.notnull(r["product_width_cm"]) else 0,
            int(r["product_height_cm"]) if pd.notnull(r["product_height_cm"]) else 0,
        ],
        axis=1,
    )
    df_products["is_active"] = True
    df_products["weight_g"] = df_products["product_weight_g"].fillna(0).astype(int)

    df_products_ready = df_products[
        ["product_id", "sku", "is_active", "weight_g", "dimensions_cm"]
    ]

    df_geolocation_ready = df_geolocation.drop_duplicates(
        subset=["geolocation_zip_code_prefix"]
    )
    df_geolocation_ready = df_geolocation_ready[
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ]
    ]

    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for col in date_cols:
        df_orders[col] = pd.to_datetime(df_orders[col])

    df_orders_ready = df_orders.rename(
        columns={
            "order_purchase_timestamp": "purchase_timestamp",
            "order_approved_at": "approved_at",
            "order_delivered_carrier_date": "delivered_carrier_date",
            "order_delivered_customer_date": "delivered_customer_date",
            "order_estimated_delivery_date": "estimated_delivery_date",
        }
    )

    df_time_bridge = df_orders_ready[["order_id", "purchase_timestamp"]]

    df_order_items = df_order_items.merge(df_time_bridge, on="order_id", how="inner")
    df_order_items["shipping_limit_date"] = pd.to_datetime(
        df_order_items["shipping_limit_date"]
    )

    df_order_items_ready = df_order_items[
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
            "purchase_timestamp",
        ]
    ]

    df_order_payments = df_order_payments.merge(df_time_bridge, on="order_id", how="inner")
    df_order_payments["gateway_response"] = df_order_payments.apply(
        lambda r: json.dumps(
            {
                "status": "approved",
                "processor": "stripe_ecommify_gateway",
                "meta": {
                    "installments_selected": int(r["payment_installments"]),
                    "fallback_payment": r["payment_type"],
                },
            }
        ),
        axis=1,
    )

    df_order_payments_ready = df_order_payments[
        [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
            "gateway_response",
            "purchase_timestamp",
        ]
    ]

    return {
        "product_category_name": df_product_category_name,
        "products": df_products_ready,
        "customers": df_customers,
        "sellers": df_sellers,
        "geolocation": df_geolocation_ready,
        "orders": df_orders_ready,
        "order_items": df_order_items_ready,
        "payments": df_order_payments_ready,
    }


def upload_to_postgresql(datasets: dict, database_url: str) -> None:
    engine = create_engine(database_url, pool_pre_ping=True)

    with engine.begin() as connection:
        print("[START] Conexión establecida. Iniciando migración transaccional estructurada...")

        for table_name, dataframe in datasets.items():
            print(f"-> Insertando {len(dataframe)} filas en '{table_name}'...")
            dataframe.to_sql(table_name, con=connection, if_exists="append", index=False)
            print(f"   [OK] Carga de tabla '{table_name}' finalizada.")

        print("[POST-PROCESS] Inicializando objetos PostGIS...")
        connection.execute(
            text(
                """
                UPDATE geolocation
                SET geom = ST_SetSRID(ST_MakePoint(geolocation_lng, geolocation_lat), 4326)
                WHERE geom IS NULL;
                """
            )
        )

        print("[OK] Objetos nativos PostGIS instanciados con éxito.")


def main() -> None:
    load_dotenv()

    database_url = os.getenv("POSTGRES_URL")
    data_path = os.getenv("DATA_PATH", "./data/raw")

    if not database_url:
        raise ValueError("Falta configurar POSTGRES_URL en el archivo .env")

    raw_data = load_csv_files(data_path)
    prepared_data = prepare_postgresql_data(raw_data)
    upload_to_postgresql(prepared_data, database_url)

    print("Base de datos PostgreSQL poblada correctamente.")


if __name__ == "__main__":
    main()