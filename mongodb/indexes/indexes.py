def create_indexes(db):
    db["products"].create_index(
        [("product_id_pg", 1)],
        unique=True
    )

    db["reviews"].create_index(
        [("product_id_pg", 1), ("score", -1)]
    )

    db["reviews"].create_index(
        [("score", 1)],
        partialFilterExpression={"score": {"$lt": 3}}
    )