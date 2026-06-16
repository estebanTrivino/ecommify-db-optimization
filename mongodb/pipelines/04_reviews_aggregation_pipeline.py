db.reviews.aggregate([
  { $match: { score: { $lt: 3 } } },
  {
    $group: {
      _id: "$product_id_pg",
      promedio_score: { $avg: "$score" },
      total_reviews: { $sum: 1 }
    }
  },
  { $sort: { total_reviews: -1 } },
  { $limit: 5 },
  {
    $lookup: {
      from: "products",
      localField: "_id",
      foreignField: "product_id_pg",
      as: "info"
    }
  },
  { $unwind: { path: "$info", preserveNullAndEmptyArrays: true } },
  {
    $project: {
      _id: 1,
      product_name: { $ifNull: ["$info.name", "Nombre no disponible"] },
      promedio_score: 1,
      total_reviews: 1
    }
  }
], { allowDiskUse: true });
