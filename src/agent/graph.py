from langgraph.graph import StateGraph, END
from src.agent.schemas import AgentState
from src.agent.nodes import classifier_node, extractor_node, reviewer_node
from src.agent.prompts import RANDOM_PAPER

# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("classify", classifier_node)
workflow.add_node("extract", extractor_node)
workflow.add_node("review", reviewer_node)

# 3. Define Edges (The Logic Flow)
# Flow: Start -> Classify -> Extract -> Review -> End
workflow.set_entry_point("classify")
workflow.add_edge("classify", "extract")
workflow.add_edge("extract", "review")
workflow.add_edge("review", END)

# 4. Compile the Graph
app = workflow.compile()

# --- Helper Function to Run the Agent ---
async def run_agent(input_text: str):
    """
    Main entry point to call the agent.
    """
    initial_state = AgentState(
        input_text=input_text,
        area=None,
        extraction=None,
        review_markdown=None,
    )
    
    # Run the graph asynchronously
    result = await app.ainvoke(initial_state)
    
    # Format the final output
    final_output = {
        "area": result["area"],
        "extraction": result["extraction"],
        "review_markdown": result["review_markdown"]
    }
    
    return final_output

if __name__ == "__main__":
    import asyncio
    import json
    
    # Run the async function
    output = asyncio.run(run_agent(RANDOM_PAPER))
    
    # Print the structured output
    print(json.dumps(output, indent=4, ensure_ascii=False))