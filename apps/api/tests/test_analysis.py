import pandas as pd
from app.services.analysis import choose_method, run_anomaly, run_sql, run_statistics


def test_router_selects_anomaly():
    assert choose_method("find anomalies", pd.DataFrame({"x": [1, 2]})) == "anomaly"


def test_sql_only_allows_select():
    result = run_sql("SELECT sum(sales) AS total FROM dataset", pd.DataFrame({"sales": [1, 2]}))
    assert result["tables"][0]["rows"] == [[3.0]]


def test_anomaly_result_has_metadata():
    assert run_anomaly(pd.DataFrame({"x": [1, 1, 1, 200]}))["anomalies"]["method"] == "robust_z_score"


def test_statistics_normality():
    assert run_statistics("test normality", pd.DataFrame({"x": range(20)}))["statistics"]["test"] == "shapiro_wilk"
