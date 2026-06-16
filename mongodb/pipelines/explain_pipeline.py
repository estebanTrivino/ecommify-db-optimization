from bson import json_util
from tabulate import tabulate

from mongodb.indexes.indexes import create_indexes
from mongodb.pipelines.reviews_pipeline import pipeline_base


def run_pipeline_explain(db):
    """
    Ejecuta medición antes/después de la optimización.

    Métricas:

    - executionTimeMillis
    - totalDocsExamined
    - WinningPlan
    """

    explain_cmd = {
        "explain": {
            "aggregate": "reviews",
            "pipeline": pipeline_base,
            "cursor": {}
        },
        "verbosity": "executionStats"
    }

    print("\n[INFO] Midiendo rendimiento ANTES de la optimización")

    db["reviews"].drop_indexes()

    before = db.command(explain_cmd)

    before_stats = before.get(
        "stages",
        [{}]
    )[0].get(
        "$cursor",
        {}
    ).get(
        "executionStats",
        before.get("executionStats", {})
    )

    before_time = before_stats.get(
        "executionTimeMillis",
        0
    )

    before_docs = before_stats.get(
        "totalDocsExamined",
        0
    )

    print("\n[INFO] Creando índices optimizados")

    create_indexes(db)

    print("\n[INFO] Midiendo rendimiento DESPUÉS de la optimización")

    after = db.command(explain_cmd)

    after_stats = after.get(
        "stages",
        [{}]
    )[0].get(
        "$cursor",
        {}
    ).get(
        "executionStats",
        after.get("executionStats", {})
    )

    after_plan = after.get(
        "stages",
        [{}]
    )[0].get(
        "$cursor",
        {}
    ).get(
        "queryPlanner",
        {}
    ).get(
        "winningPlan",
        {}
    )

    after_time = after_stats.get(
        "executionTimeMillis",
        0
    )

    after_docs = after_stats.get(
        "totalDocsExamined",
        0
    )

    saving = (
        (before_docs - after_docs)
        / max(1, before_docs)
    ) * 100

    table = [
        [
            "Estrategia de búsqueda",
            "COLLSCAN",
            "IXSCAN"
        ],
        [
            "Documentos escaneados",
            before_docs,
            f"{after_docs} (ahorro {saving:.2f}%)"
        ],
        [
            "Tiempo de ejecución",
            f"{before_time} ms",
            f"{after_time} ms"
        ]
    ]

    print(
        tabulate(
            table,
            headers=[
                "Métrica",
                "Antes",
                "Después"
            ],
            tablefmt="fancy_grid"
        )
    )

    print("\n[PLAN DE EJECUCIÓN GANADOR]")
    print(
        json_util.dumps(
            after_plan,
            indent=2
        )
    )

    return {
        "before_time": before_time,
        "after_time": after_time,
        "before_docs": before_docs,
        "after_docs": after_docs,
        "winning_plan": after_plan
    }