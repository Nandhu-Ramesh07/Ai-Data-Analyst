from langgraph.graph import END, START, StateGraph

from app.graph.nodes import execute, route
from app.graph.state import AgentState


def build_workflow():
    graph = StateGraph(AgentState)
    graph.add_node("router", route)
    graph.add_node("executor", execute)
    graph.add_edge(START, "router")
    graph.add_edge("router", "executor")
    graph.add_edge("executor", END)
    return graph.compile()
