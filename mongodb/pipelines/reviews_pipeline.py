"""
Aggregation Pipelines para el módulo analítico de Ecommify.

Contiene:

- pipeline_base
- pipeline_completo

Utilizados para análisis de reseñas críticas de productos.
"""

pipeline_base = [
    {
        "$match": {
            "score": {"$lt": 3}
        }
    },
    {
        "$group": {
            "_id": "$product_id_pg",
            "promedio_score": {
                "$avg": "$score"
            },
            "total_reviews": {
                "$sum": 1
            }
        }
    },
    {
        "$sort": {
            "total_reviews": -1
        }
    },
    {
        "$limit": 5
    }
]

pipeline_completo = pipeline_base + [
    {
        "$lookup": {
            "from": "products",
            "localField": "_id",
            "foreignField": "product_id_pg",
            "as": "info"
        }
    },
    {
        "$unwind": {
            "path": "$info",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        "$project": {
            "_id": 1,
            "product_name": {
                "$ifNull": [
                    "$info.name",
                    "Nombre no disponible"
                ]
            },
            "promedio_score": 1,
            "total_reviews": 1
        }
    }
]