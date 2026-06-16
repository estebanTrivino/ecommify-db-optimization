def create_validators(db):
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
                    "score": {"bsonType": "int"}
                },
            }
        },
    )