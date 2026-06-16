db.createCollection("reviews", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["order_id_pg", "product_id_pg", "customer", "score", "creation_date"],
      properties: {
        order_id_pg: { bsonType: "string" },
        product_id_pg: { bsonType: "string" },
        customer: { bsonType: "object" },
        score: { bsonType: "int" },
        creation_date: { bsonType: "string" }
      }
    }
  }
});
