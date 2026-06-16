db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["product_id_pg", "name", "display_price", "seller"],
      properties: {
        product_id_pg: { bsonType: "string" },
        name: { bsonType: "string" },
        display_price: { bsonType: "number" },
        seller: {
          bsonType: "object",
          required: ["seller_id_pg", "name", "reputation_score"],
          properties: {
            seller_id_pg: { bsonType: "string" },
            name: { bsonType: "string" },
            reputation_score: { bsonType: "number" }
          }
        }
      }
    }
  }
});
