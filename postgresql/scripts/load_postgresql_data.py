import os
import json
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('POSTGRES_URL')
DATA_PATH = os.getenv('DATA_PATH', './data/raw')

if not DATABASE_URL:
    raise RuntimeError('Configure POSTGRES_URL en el archivo .env')

required_files = {
    'sellers': 'olist_sellers_dataset.csv',
    'orders': 'olist_orders_dataset.csv',
    'customers': 'olist_customers_dataset.csv',
    'products': 'olist_products_dataset.csv',
    'geolocation': 'olist_geolocation_dataset.csv',
    'product_category_name': 'product_category_name_translation.csv',
    'order_payments': 'olist_order_payments_dataset.csv',
    'order_items': 'olist_order_items_dataset.csv',
}

def read_csv(name):
    path = os.path.join(DATA_PATH, required_files[name])
    if not os.path.exists(path):
        raise FileNotFoundError(f'No se encontró {path}')
    return pd.read_csv(path)

print('[INFO] Cargando datasets locales...')
df_sellers = read_csv('sellers')
df_orders = read_csv('orders')
df_customers = read_csv('customers')
df_products = read_csv('products')
df_geolocation = read_csv('geolocation')
df_product_category_name = read_csv('product_category_name')
df_order_payments = read_csv('order_payments')
df_order_items = read_csv('order_items')

print('[INFO] Transformando datos para el modelo PostgreSQL...')
df_product_category_name = df_product_category_name.drop_duplicates(subset=['product_category_name'])

df_products['sku'] = 'SKU-' + df_products['product_id'].str[:8].str.upper()
df_products['dimensions_cm'] = df_products.apply(
    lambda r: [
        int(r['product_length_cm']) if pd.notnull(r['product_length_cm']) else 0,
        int(r['product_width_cm']) if pd.notnull(r['product_width_cm']) else 0,
        int(r['product_height_cm']) if pd.notnull(r['product_height_cm']) else 0,
    ],
    axis=1,
)
df_products['is_active'] = True
df_products['weight_g'] = df_products['product_weight_g'].fillna(0).astype(int)
df_products_ready = df_products[['product_id', 'sku', 'is_active', 'weight_g', 'dimensions_cm']]

df_geolocation_ready = df_geolocation.drop_duplicates(subset=['geolocation_zip_code_prefix'])
df_geolocation_ready = df_geolocation_ready[
    ['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng', 'geolocation_city', 'geolocation_state']
]

date_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
]
for col in date_cols:
    df_orders[col] = pd.to_datetime(df_orders[col])

df_orders_ready = df_orders.rename(
    columns={
        'order_purchase_timestamp': 'purchase_timestamp',
        'order_approved_at': 'approved_at',
        'order_delivered_carrier_date': 'delivered_carrier_date',
        'order_delivered_customer_date': 'delivered_customer_date',
        'order_estimated_delivery_date': 'estimated_delivery_date',
    }
)

df_time_bridge = df_orders_ready[['order_id', 'purchase_timestamp']]

df_order_items = df_order_items.merge(df_time_bridge, on='order_id', how='inner')
df_order_items['shipping_limit_date'] = pd.to_datetime(df_order_items['shipping_limit_date'])
df_order_items_ready = df_order_items[
    ['order_id', 'order_item_id', 'product_id', 'seller_id', 'shipping_limit_date', 'price', 'freight_value', 'purchase_timestamp']
]

df_order_payments = df_order_payments.merge(df_time_bridge, on='order_id', how='inner')
df_order_payments['gateway_response'] = df_order_payments.apply(
    lambda r: json.dumps(
        {
            'status': 'approved',
            'processor': 'stripe_ecommify_gateway',
            'meta': {
                'installments_selected': int(r['payment_installments']),
                'fallback_payment': r['payment_type'],
            },
        }
    ),
    axis=1,
)
df_order_payments_ready = df_order_payments[
    ['order_id', 'payment_sequential', 'payment_type', 'payment_installments', 'payment_value', 'gateway_response', 'purchase_timestamp']
]

datasets_to_upload = {
    'product_category_name': df_product_category_name,
    'products': df_products_ready,
    'customers': df_customers,
    'sellers': df_sellers,
    'geolocation': df_geolocation_ready,
    'orders': df_orders_ready[
        [
            'order_id', 'customer_id', 'order_status', 'purchase_timestamp', 'approved_at',
            'delivered_carrier_date', 'delivered_customer_date', 'estimated_delivery_date'
        ]
    ],
    'order_items': df_order_items_ready,
    'payments': df_order_payments_ready,
}

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
with engine.begin() as connection:
    print('[START] Carga transaccional en PostgreSQL/Supabase...')
    for table_name, dataframe in datasets_to_upload.items():
        print(f'-> Insertando {len(dataframe)} filas en {table_name}...')
        dataframe.to_sql(table_name, con=connection, if_exists='append', index=False, method='multi', chunksize=1000)

    print('[POST-PROCESS] Inicializando geometría PostGIS...')
    connection.execute(
        text(
            """
            UPDATE geolocation
            SET geom = ST_SetSRID(ST_MakePoint(geolocation_lng, geolocation_lat), 4326)
            WHERE geom IS NULL;
            """
        )
    )

print('[OK] Carga PostgreSQL finalizada.')
