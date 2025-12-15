from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ToolStrategy
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from src.agent.prompts import CLASSIFIER_PROMPT


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

class ClassifierResponse(BaseModel):
    category: str = Field(description="The name of the area.")

async def classify_paper():
    paper = """
    Field of study in artificial intelligence concerned with the development and study 
    of statistical algorithms that can learn from data and generalise to unseen data, 
    and thus perform tasks without explicit instructions. Advances in the field of deep 
    learning have allowed neural networks, a class of statistical algorithms, to surpass 
    many previous machine learning approaches in performance.
    """  
    input_message = {"messages": [{"role": "user", "content": paper}]}

    async with client.session("research_article") as session:
        tools = await load_mcp_tools(session)

        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=CLASSIFIER_PROMPT,
            response_format=ToolStrategy(ClassifierResponse),
        )

        response = await agent.ainvoke(input_message)
        print(response["structured_response"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(classify_paper())

