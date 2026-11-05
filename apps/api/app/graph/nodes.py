from app.services.analysis import choose_method, chart_spec, run_analysis, run_anomaly, run_sql, run_statistics


def route(state):
    return {"method": choose_method(state["question"], state["df"])}


def execute(state):
    method = state["method"]
    if method == "profile":
        return {"result": {"message": "Automated dataset profile.", "profile": state["profile"], "tables": []}}
    if method == "sql":
        return {"result": run_sql(state["question"], state["df"])}
    if method == "statistics":
        return {"result": run_statistics(state["question"], state["df"])}
    if method == "anomaly":
        return {"result": run_anomaly(state["df"])}
    if method == "visualization":
        chart = chart_spec(state["question"], state["df"])
        return {"result": {"message": chart["title"], "chart": chart, "tables": []}}
    return {"result": run_analysis(state["question"], state["df"])}
