from langgraph.graph import StateGraph, START, END
from methods import (
    WorkingState,
    UnifiedAnalysisAgent,
    TimelineBudgetAgent,
    ProposalWriterAgent
)

def Get_workflow():
    graph = StateGraph(WorkingState)

    graph.add_node("UnifiedAnalysisAgent", UnifiedAnalysisAgent)
    graph.add_node("TimelineBudgetAgent", TimelineBudgetAgent)
    graph.add_node("ProposalWriterAgent", ProposalWriterAgent)

    graph.add_edge(START, "UnifiedAnalysisAgent")
    graph.add_edge("UnifiedAnalysisAgent", "TimelineBudgetAgent")
    graph.add_edge("TimelineBudgetAgent", "ProposalWriterAgent")
    graph.add_edge("ProposalWriterAgent", END)

    return graph.compile()
