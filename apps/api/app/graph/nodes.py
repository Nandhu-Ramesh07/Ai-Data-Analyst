from app.services.analysis import choose_method, chart_spec, run_analysis, run_anomaly, run_sql, run_statistics


def route(state):
    return {"method": choose_method(state["question"], state["df"])}


def analyst_agent(state):
    if state["method"] == "profile":
        return {"result": {"message": "Automated dataset profile.", "profile": state["profile"], "tables": []}}
    if state["method"] == "sql":
        return {"result": run_sql(state["question"], state["df"])}
    return {"result": run_analysis(state["question"], state["df"])}


def visualization_agent(state):
    chart = chart_spec(state["question"], state["df"])
    return {"result": {"message": chart["title"], "chart": chart, "tables": []}}


def statistics_agent(state):
    if state["method"] == "anomaly":
        return {"result": run_anomaly(state["df"])}
    return {"result": run_statistics(state["question"], state["df"])}


def report_agent(state):
    return {"result": {"message": "Your report is ready to download. Use the Download PDF report button to create it from this conversation.", "tables": []}}
