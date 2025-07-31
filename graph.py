from langgraph.graph import StateGraph, START, END
from methods import *


def Get_workflow():
    """
    This function returns the workflow of the graph.
    """

    graph= StateGraph(WorkingState)
    
    # adding the nodes
    graph.add_node('InputAgent', InputAgent)
    graph.add_node('Use-case Classifier Agent', UseCaseClassifierAgent)
    graph.add_node('Scope Generator Agent', ScopeGeneratorAgent)
    graph.add_node('Timeline Estimator Agent', TimelineEstimatorAgent)
    graph.add_node('Budget Estimator Agent', BudgetEstimatorAgent)
    graph.add_node('Proposal Writer Agent', ProposalWriterAgent)
    
    
    # add the edges
    graph.add_edge(START, 'InputAgent')
    graph.add_edge('InputAgent', 'Use-case Classifier Agent')
    graph.add_edge('Use-case Classifier Agent', 'Scope Generator Agent')
    graph.add_edge('Scope Generator Agent', 'Timeline Estimator Agent')
    graph.add_edge('Timeline Estimator Agent', 'Budget Estimator Agent')
    graph.add_edge('Budget Estimator Agent', 'Proposal Writer Agent')
    graph.add_edge('Proposal Writer Agent', END)
    

    return graph.compile()































