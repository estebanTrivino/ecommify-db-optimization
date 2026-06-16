db.products.createIndex({ product_id_pg: 1 }, { unique: true });

db.reviews.createIndex({ product_id_pg: 1, score: -1 });

db.reviews.createIndex(
  { score: 1 },
  { partialFilterExpression: { score: { $lt: 3 } } }
);
