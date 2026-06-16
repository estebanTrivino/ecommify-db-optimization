db.runCommand({
  explain: {
    aggregate: "reviews",
    pipeline: [
      { $match: { score: { $lt: 3 } } },
      {
        $group: {
          _id: "$product_id_pg",
          promedio_score: { $avg: "$score" },
          total_reviews: { $sum: 1 }
        }
      },
      { $sort: { total_reviews: -1 } },
      { $limit: 5 }
    ],
    cursor: {}
  },
  verbosity: "executionStats"
});
