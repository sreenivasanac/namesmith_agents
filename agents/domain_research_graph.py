from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from pydantic import BaseModel
from agents.market_research_bot import market_research_chain
from agents.domain_generator import generate_domain_suggestions
from agents.domain_name_scoring_bot import evaluate_domain_set
from agents.trend_research_bot import generate_research_queries
from agents.check_domain_name_availability import domain_availability_tool
import requests
from domain_schema import DomainWithDetails, DomainName, DNAvailabilityStatus, DNEvaluation, DNSEOAnalysis

BASE_URL = "http://localhost:3000/api"

# Define our state
class State(TypedDict):
    initialized: bool
    trend_queries: list
    market_trends: dict
    generated_domains: list
    scored_domains: list
    domains: list
    available_domains: list
    iteration: int

# Define the nodes of our graph
def initialize(state: State = None) -> State:
    return State(
        initialized=True,
        trend_queries=[],
        market_trends={},
        generated_domains=[],
        scored_domains=[],
        domains=[],
        available_domains=[],
        iteration=0
    )

def trend_research_bot(state: State):
    print('Generating trend research queries...')
    state['trend_queries'] = generate_research_queries().queries
    print(f"Generated {len(state['trend_queries'])} trend research queries")
    return state

def market_trends_bot(state: State):
    print('Generating market trends...')
    state['market_trends'] = market_research_chain.invoke({})
    print(f"Generated market trends for {len(state['market_trends'].companies)} companies")
    return state

def domain_name_generator_bot(state: State):
    print("Cooking up some delicious domains...")
    state['generated_domains'] = generate_domain_suggestions(state['market_trends'])

    print(f"Generated {len(state['generated_domains'].suggestions)} domain suggestions")
    state['iteration'] += 1
    return state

def name_scoring_bot(state: State):
    print("Scoring the domains...")
    state['scored_domains'] = evaluate_domain_set(state['generated_domains'])
    state['domains'] = [eval.domain for eval in state['scored_domains'].evaluations]
    print(f"Scored {len(state['domains'])} domains")
    return state

def check_domain_name_availability(state: State):
    print("Checking domain availability...")
    domains_to_check = state['domains']
    available_domains = domain_availability_tool.run(domains_to_check)
    state['available_domains'] = available_domains
    print(f"Found {len(available_domains)} available domains")
    return state

def route(state: State) -> str:
    if state['available_domains']:
        return "process_available_domains"
    elif state['iteration'] < 3:  # Limit to 3 attempts
        return "domain_name_generator_bot"
    else:
        return "end_process"

def save_domain_to_db(domain_info):
    # Create DomainName object
    domain_name = DomainName(
        domainName=domain_info.domain,
        tld=domain_info.domain.split('.')[-1],
        length=len(domain_info.domain.split('.')[0]),
        processedByAgent="DomainResearchGraph",
        agentModel="GPT-4"
    )
    
    # Create domain in the database
    created_domain = create_domain(domain_name.dict())
    
    if created_domain:
        # Create DNAvailabilityStatus object
        availability_status = DNAvailabilityStatus(
            domainName=domain_info.domain,
            status="Available",
            processedByAgent="ProcessAvailableDomains",
            agentModel="GPT-4"
        )
        create_availability_status(availability_status.dict())
        
        # Create DNEvaluation object
        evaluation = DNEvaluation(
            domainName=domain_info.domain,
            possibleCategories=domain_info.scores.categories,
            possibleKeywords=domain_info.scores.keywords,
            memorabilityScore=domain_info.scores.memorability,
            pronounceabilityScore=domain_info.scores.pronounceability,
            brandabilityScore=domain_info.scores.brandability,
            description=domain_info.scores.explanation,
            processedByAgent="DomainResearchGraph",
            agentModel="GPT-4"
        )
        create_evaluation(evaluation.dict())
        
        print(f"Processed and saved domain: {domain_info.domain}")
        return True
    else:
        print(f"Failed to save domain: {domain_info.domain}")
        return False

def process_available_domains(state: State) -> dict:
    print("Processing available domains...")
    for available_domain in state['available_domains']:
        domain_info = next((d for d in state['scored_domains'].evaluations if d.domain == available_domain), None)
        if domain_info:
            save_domain_to_db(domain_info)
    return state

def end_process(state: State) -> dict:
    print("Ending process...")
    return {"final_message": "No available domains found after multiple attempts."}

def create_domain(domain_data):
    response = requests.post(f"{BASE_URL}/domains", json=domain_data)
    print(f"API Response for create_domain: Status {response.status_code}, Content: {response.text}")
    return response.json() if response.ok else None

def create_availability_status(status_data):
    response = requests.post(f"{BASE_URL}/availability-status", json=status_data)
    print(f"API Response for create_availability_status: Status {response.status_code}, Content: {response.text}")
    return response.json() if response.ok else None

def create_evaluation(evaluation_data):
    response = requests.post(f"{BASE_URL}/evaluation", json=evaluation_data)
    print(f"API Response for create_evaluation: Status {response.status_code}, Content: {response.text}")
    return response.json() if response.ok else None

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("initialize", initialize)
workflow.add_node("trend_research_bot", trend_research_bot)
workflow.add_node("market_trends_bot", market_trends_bot)
workflow.add_node("domain_name_generator_bot", domain_name_generator_bot)
workflow.add_node("name_scoring_bot", name_scoring_bot)
workflow.add_node("check_domain_name_availability", check_domain_name_availability)
workflow.add_node("process_available_domains", process_available_domains)
workflow.add_node("end_process", end_process)

# Add edges
workflow.add_edge("initialize", "trend_research_bot")
workflow.add_edge("trend_research_bot", "market_trends_bot")
workflow.add_edge("market_trends_bot", "domain_name_generator_bot")
workflow.add_edge("domain_name_generator_bot", "name_scoring_bot")
workflow.add_edge("name_scoring_bot", "check_domain_name_availability")
workflow.add_conditional_edges(
    'check_domain_name_availability',
    route,
    {
        "process_available_domains": 'process_available_domains',
        "domain_name_generator_bot": 'domain_name_generator_bot',
        "end_process": 'end_process'
    }
)
workflow.add_edge("process_available_domains", END)
workflow.add_edge("end_process", END)

# Set the entrypoint
workflow.set_entry_point("initialize")

config = {"configurable": {"thread_id": "1"}}

# Compile the graph
graph = workflow.compile()

def run_domain_research():
    initial_state = initialize()
    for output in graph.stream(initial_state):
        if "intermediate_steps" in output:
            print(f"Step: {output['intermediate_steps'][-1][0]}")
            print(f"Output: {output['intermediate_steps'][-1][1]}")
        else:
            print("Final output:", output)
    
    return output

# Add this new code block at the end of the file
try:
    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
except Exception:
    pass
