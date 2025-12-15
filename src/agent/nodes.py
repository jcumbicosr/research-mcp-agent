from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.structured_output import ToolStrategy
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from src.agent.prompts import RANDOM_PAPER
from src.agent.prompts import CLASSIFIER_PROMPT, EXTRACTION_PROMPT, REVIEWER_PROMPT
from src.agent.schemas import ClassifierResponse, ExtractionResponse
from src.agent.schemas import AgentState

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_retries=2
)

client = MultiServerMCPClient(
    {
        "research_article": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "src.mcp_server.server"],
        }
    }
)


async def classify_paper(state: AgentState) -> AgentState:
    """
    Agent 1: The Classifier.
    Classifies the input article into one of the existing areas.
    """
    input_message = {"messages": [{"role": "user", "content": state["input_text"]}]}

    async with client.session("research_article") as session:
        tools = await load_mcp_tools(session)

        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=CLASSIFIER_PROMPT,
            response_format=ToolStrategy(ClassifierResponse),
        )

        response = await agent.ainvoke(input_message)

        try:    
            # Convert the Pydantic object to a standard Python dictionary.
            final_json_dict = response["structured_response"].model_dump()
        except Exception as e:
            # Fallback state in case model fails to generate valid structure
            final_json_dict = {
                "area": "unclassified"
            }
    
    return {"area": final_json_dict["area"]}

def extractor_node(state: AgentState) -> AgentState:
    """
    Agent 2: The Extractor.
    Analyzes the text and forces output into the strict Pydantic schema.
    """

    input_message = {"messages": [{"role": "user", "content": state["input_text"]}]}

    agent = create_agent(
        model=llm,
        system_prompt=EXTRACTION_PROMPT,
        response_format=ToolStrategy(ExtractionResponse),
    )

    response = agent.invoke(input_message)
    
    try:    
        # Convert the Pydantic object to a standard Python dictionary.
        # IMPORTANT: by_alias=True ensures the keys have the typo required by the prompt.
        final_json_dict = response["structured_response"].model_dump(by_alias=True)
        
    except Exception as e:
        # Fallback state in case model fails to generate valid structure
        final_json_dict = {
            "what problem does the artcle propose to solve?": "Error during extraction",
            "step by step on how to solve it": ["Error"],
            "conclusion": f"Could not extract due to error: {e}"
        }

    return {"extraction": final_json_dict}

def reviewer_node(state: AgentState) -> AgentState:
    """
    Agent 3: The Reviewer.
    Analyzes the text and produces a critical review in Portuguese.
    """
    input_message = {"messages": [{"role": "user", "content": RANDOM_PAPER}]}

    agent = create_agent(
        model=llm,
        system_prompt=REVIEWER_PROMPT,
    )

    response = agent.invoke(input_message)

    try:
        # Extract the content of the last message in the response
        review_content = response['messages'][-1].content
        
    except Exception as e:
        review_content = f"Erro ao gerar resenha: {str(e)}"

    return {"review_markdown": review_content}


if __name__ == "__main__":
    # import asyncio
    # asyncio.run(classify_paper())

    # extractor_node()

    reviewer_node()


