from langgraph.graph import END, START, StateGraph

from app.graph.nodes import analyst_agent, report_agent, route, statistics_agent, visualization_agent
from app.graph.state import AgentState


def build_workflow():
    graph = StateGraph(AgentState)
    graph.add_node("router", route)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("visualization", visualization_agent)
    graph.add_node("statistics", statistics_agent)
    graph.add_node("report", report_agent)
    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", lambda state: state["method"], {
        "analysis": "analyst", "profile": "analyst", "sql": "analyst",
        "visualization": "visualization", "statistics": "statistics", "anomaly": "statistics", "report": "report",
    })
    graph.add_edge("analyst", END)
    graph.add_edge("visualization", END)
    graph.add_edge("statistics", END)
    graph.add_edge("report", END)
    return graph.compile()
