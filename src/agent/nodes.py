from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ToolStrategy
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools


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
    category: str = Field(description="The name of the category.")

async def classify_paper():
    text = "A sport is an activity involving physical exertion and skill in which an individual or team competes against another or others for entertainment."  
    input_message = {"messages": [{"role": "user", "content": text}]}

    async with client.session("research_article") as session:
        tools = await load_mcp_tools(session)

        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt="You are a text classification assistant. Classify the following text into one of these categories: 'sports', 'politics', 'technology', 'entertainment'.",
            response_format=ToolStrategy(ClassifierResponse),
        )

        response = agent.invoke(input_message)
        print(response["structured_response"])

if __name__ == "__main__":
    classify_paper()

