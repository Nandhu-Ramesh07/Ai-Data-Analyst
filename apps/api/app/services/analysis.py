"""Trusted, typed analytical operations. No LLM generated code is executed here."""
from __future__ import annotations

import re
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.astype(str).tolist()


def _find_columns(question: str, df: pd.DataFrame) -> list[str]:
    lower = question.lower()
    return [str(column) for column in df.columns if str(column).lower() in lower]


def choose_method(question: str, df: pd.DataFrame) -> str:
    q = question.lower()
    if any(word in q for word in ("outlier", "anomal", "unusual", "fraud")):
        return "anomaly"
    if any(word in q for word in ("test", "significant", "hypothesis", "p-value", "correlat", "regression")):
        return "statistics"
    if any(word in q for word in ("chart", "plot", "graph", "visual", "trend")):
        return "visualization"
    if any(word in q for word in ("profile", "quality", "missing", "duplicate", "overview")):
        return "profile"
    if any(word in q for word in ("sql", "select", "group by", "aggregate", "query")):
        return "sql"
    return "analysis"


def table(df: pd.DataFrame, limit: int = 200) -> dict[str, Any]:
    display = df.head(limit).replace({np.nan: None})
    return {"columns": [str(c) for c in display.columns], "rows": display.astype(object).where(pd.notna(display), None).values.tolist()}


def run_sql(question: str, df: pd.DataFrame) -> dict[str, Any]:
    match = re.search(r"```sql\s*(.*?)```", question, re.IGNORECASE | re.DOTALL)
    sql = match.group(1).strip() if match else question.strip()
    if not re.match(r"^select\b", sql, re.IGNORECASE) or ";" in sql.rstrip(";"):
        raise ValueError("Only one read-only SELECT statement is allowed. Put SQL inside a ```sql block.")
    forbidden = r"\b(insert|update|delete|drop|alter|attach|copy|create|pragma|call)\b"
    if re.search(forbidden, sql, re.IGNORECASE):
        raise ValueError("Only read-only SELECT SQL is allowed.")
    connection = duckdb.connect(":memory:")
    try:
        connection.register("dataset", df)
        result = connection.execute(sql).df()
    finally:
        connection.close()
    return {"message": f"SQL returned {len(result):,} row(s).", "tables": [table(result)]}


def run_analysis(question: str, df: pd.DataFrame) -> dict[str, Any]:
    columns = _find_columns(question, df)
    numeric = [c for c in columns if c in _numeric_columns(df)] or _numeric_columns(df)
    if not numeric:
        return {"message": "This dataset has no numeric columns to summarize.", "tables": []}
    summary = df[numeric].describe().transpose().reset_index(names="column")
    return {"message": f"Summary statistics for {len(numeric)} numeric column(s).", "tables": [table(summary)]}


def run_statistics(question: str, df: pd.DataFrame) -> dict[str, Any]:
    numeric = _numeric_columns(df)
    selected = [c for c in _find_columns(question, df) if c in numeric]
    q = question.lower()
    if "correlat" in q and len(selected or numeric) >= 2:
        cols = selected or numeric[:10]
        correlation = df[cols].corr(numeric_only=True).reset_index(names="column")
        return {"message": "Pearson correlation matrix.", "statistics": {"test": "pearson_correlation", "assumptions": ["Numeric variables", "Linear association"], "result": table(correlation)}, "tables": [table(correlation)]}
    if len(selected) >= 2:
        a, b = (df[selected[0]].dropna(), df[selected[1]].dropna())
        statistic, p_value = stats.ttest_ind(a, b, equal_var=False)
        return {"message": "Welch two-sample t-test completed.", "statistics": {"test": "welch_t_test", "statistic": float(statistic), "p_value": float(p_value), "effect_size": float((a.mean() - b.mean()) / np.sqrt((a.var() + b.var()) / 2)), "assumptions": ["Independent observations", "Approximately normal samples"]}, "tables": []}
    if numeric:
        series = df[numeric[0]].dropna()
        statistic, p_value = stats.shapiro(series.sample(min(len(series), 5000), random_state=42))
        return {"message": f"Shapiro-Wilk normality test for {numeric[0]}.", "statistics": {"test": "shapiro_wilk", "statistic": float(statistic), "p_value": float(p_value), "assumptions": ["Continuous numeric data"]}, "tables": []}
    return {"message": "No compatible numeric data was found for a statistical test.", "tables": []}


def run_anomaly(df: pd.DataFrame) -> dict[str, Any]:
    numeric = _numeric_columns(df)
    if not numeric:
        return {"message": "No numeric columns are available for anomaly detection.", "anomalies": {"count": 0, "method": "none"}, "tables": []}
    values = df[numeric]
    z = ((values - values.median()) / values.apply(lambda col: np.median(np.abs(col.dropna() - col.dropna().median())) or 1))
    flagged = z.abs().gt(3.5).any(axis=1)
    method = "robust_z_score"
    if len(numeric) > 1 and len(values.dropna()) >= 20:
        clean = values.fillna(values.median())
        flagged = IsolationForest(contamination="auto", random_state=42).fit_predict(clean) == -1
        flagged = pd.Series(flagged, index=df.index)
        method = "isolation_forest"
    result = df.loc[flagged].copy()
    result.insert(0, "row_index", result.index)
    return {"message": f"Detected {len(result):,} potential anomaly row(s) using {method}.", "anomalies": {"count": int(len(result)), "method": method, "threshold": "3.5 robust z-score" if method == "robust_z_score" else "Isolation Forest auto contamination"}, "tables": [table(result)]}


def chart_spec(question: str, df: pd.DataFrame) -> dict[str, Any]:
    columns = _find_columns(question, df)
    numeric = [c for c in columns if c in _numeric_columns(df)] or _numeric_columns(df)
    categorical = [str(c) for c in df.select_dtypes(include=["object", "category"]).columns]
    if categorical and numeric:
        grouped = df.groupby(categorical[0], dropna=False)[numeric[0]].mean().sort_values(ascending=False).head(20).reset_index()
        return {"type": "bar", "title": f"Average {numeric[0]} by {categorical[0]}", "x": categorical[0], "y": numeric[0], "data": table(grouped)}
    if numeric:
        return {"type": "histogram", "title": f"Distribution of {numeric[0]}", "x": numeric[0], "data": table(df[[numeric[0]]])}
    return {"type": "table", "title": "Dataset preview", "data": table(df)}
