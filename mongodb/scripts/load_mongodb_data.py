import os
import time
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from tqdm import tqdm
from tabulate import tabulate
from bson import json_util

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('MONGO_DB', 'ecommify_db')
DATA_PATH = os.getenv('DATA_PATH', './data/raw')

if not MONGO_URI:
    raise RuntimeError('Configure MONGO_URI en el archivo .env')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def path(filename):
    full_path = os.path.join(DATA_PATH, filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f'No se encontró {full_path}')
    return full_path

def print_banner(title):
    print('\n' + '=' * 80)
    print(title.upper())
    print('=' * 80)

def setup_collections():
    print_banner('Preparación de colecciones y validadores')
    for name in ['products', 'reviews']:
        if name in db.list_collection_names():
            db.drop_collection(name)

    db.create_collection('products', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['product_id_pg', 'name', 'display_price', 'seller'],
            'properties': {
                'product_id_pg': {'bsonType': 'string'},
                'name': {'bsonType': 'string'},
                'display_price': {'bsonType': 'number'},
                'seller': {
                    'bsonType': 'object',
                    'required': ['seller_id_pg', 'name', 'reputation_score'],
                    'properties': {
                        'seller_id_pg': {'bsonType': 'string'},
                        'name': {'bsonType': 'string'},
                        'reputation_score': {'bsonType': 'number'},
                    },
                },
            },
        }
    })

    db.create_collection('reviews', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['order_id_pg', 'product_id_pg', 'customer', 'score', 'creation_date'],
            'properties': {'score': {'bsonType': 'int'}},
        }
    })


def get_prepared_data(limit=1000):
    print_banner('Extracción y transformación de datos')
    df_order_items = pd.read_csv(path('olist_order_items_dataset.csv'))
    df_order_reviews = pd.read_csv(path('olist_order_reviews_dataset.csv'))
    df_orders = pd.read_csv(path('olist_orders_dataset.csv'))
    df_products = pd.read_csv(path('olist_products_dataset.csv'))

    products = []
    for _, row in tqdm(df_products.head(limit).iterrows(), total=min(limit, len(df_products)), desc='Productos'):
        products.append({
            'product_id_pg': str(row['product_id']),
            'name': str(row['product_category_name']) if pd.notna(row['product_category_name']) else 'Sin Categoria',
            'display_price': 50.0,
            'seller': {
                'seller_id_pg': 'S_001',
                'name': 'Vendedor Default',
                'reputation_score': 5.0,
            },
        })

    df_full = df_order_reviews.merge(df_orders, on='order_id').merge(df_order_items, on='order_id')
    reviews = []
    for _, row in tqdm(df_full.head(limit).iterrows(), total=min(limit, len(df_full)), desc='Reseñas'):
        reviews.append({
            'order_id_pg': str(row['order_id']),
            'product_id_pg': str(row['product_id']),
            'customer': {'customer_id_pg': str(row['customer_id']), 'first_name': 'N/A'},
            'score': int(row['review_score']),
            'creation_date': str(row['review_creation_date']),
        })

    return products, reviews


def load_data(products, reviews):
    print_banner('Carga de documentos')
    if products:
        db.products.insert_many(products)
    if reviews:
        db.reviews.insert_many(reviews)
    print(f'Productos: {db.products.count_documents({})}')
    print(f'Reseñas: {db.reviews.count_documents({})}')


def optimize_and_measure():
    print_banner('Medición antes/después')
    pipeline_base = [
        {'$match': {'score': {'$lt': 3}}},
        {'$group': {'_id': '$product_id_pg', 'promedio_score': {'$avg': '$score'}, 'total_reviews': {'$sum': 1}}},
        {'$sort': {'total_reviews': -1}},
        {'$limit': 5},
    ]
    explain_cmd = {'explain': {'aggregate': 'reviews', 'pipeline': pipeline_base, 'cursor': {}}, 'verbosity': 'executionStats'}

    db.reviews.drop_indexes()
    before = db.command(explain_cmd)
    before_stats = before.get('stages', [{}])[0].get('$cursor', {}).get('executionStats', before.get('executionStats', {}))

    db.products.create_index([('product_id_pg', 1)], unique=True)
    db.reviews.create_index([('product_id_pg', 1), ('score', -1)])
    db.reviews.create_index([('score', 1)], partialFilterExpression={'score': {'$lt': 3}})

    after = db.command(explain_cmd)
    after_stats = after.get('stages', [{}])[0].get('$cursor', {}).get('executionStats', after.get('executionStats', {}))
    after_plan = after.get('stages', [{}])[0].get('$cursor', {}).get('queryPlanner', {}).get('winningPlan', {})

    docs_before = before_stats.get('totalDocsExamined', 0)
    docs_after = after_stats.get('totalDocsExamined', 0)
    improvement = ((docs_before - docs_after) / max(1, docs_before)) * 100

    table = [
        ['Documentos examinados', docs_before, f'{docs_after} (ahorro {improvement:.2f}%)'],
        ['Tiempo de ejecución', f"{before_stats.get('executionTimeMillis', 0)} ms", f"{after_stats.get('executionTimeMillis', 0)} ms"],
    ]
    print(tabulate(table, headers=['Métrica', 'Antes', 'Después'], tablefmt='github'))
    print('\nPlan ganador después de optimizar:')
    print(json_util.dumps(after_plan, indent=2))

    pipeline_complete = pipeline_base + [
        {'$lookup': {'from': 'products', 'localField': '_id', 'foreignField': 'product_id_pg', 'as': 'info'}},
        {'$unwind': {'path': '$info', 'preserveNullAndEmptyArrays': True}},
        {'$project': {'_id': 1, 'product_name': {'$ifNull': ['$info.name', 'Nombre no disponible']}, 'promedio_score': 1, 'total_reviews': 1}},
    ]
    print('\nTop 5 reseñas críticas:')
    for row in db.reviews.aggregate(pipeline_complete, allowDiskUse=True):
        print(row)

if __name__ == '__main__':
    start = time.time()
    setup_collections()
    products, reviews = get_prepared_data()
    load_data(products, reviews)
    optimize_and_measure()
    print(f'Finalizado en {time.time() - start:.2f} segundos')
