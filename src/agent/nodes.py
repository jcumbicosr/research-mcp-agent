from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ToolStrategy
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_retries=2
)

class ClassifierResponse(BaseModel):
    category: str = Field(description="The name of the category.")

def classify_paper():
    text = "A sport is an activity involving physical exertion and skill in which an individual or team competes against another or others for entertainment."  
    input_message = {"messages": [{"role": "user", "content": text}]}

    agent = create_agent(
        model=llm,
        system_prompt="You are a text classification assistant. Classify the following text into one of these categories: 'sports', 'politics', 'technology', 'entertainment'.",
        response_format=ToolStrategy(ClassifierResponse),
    )

    response = agent.invoke(input_message)
    print(response["structured_response"])

if __name__ == "__main__":
    classify_paper()

