from fastmcp import FastMCP
from typing import List, Dict, Any
from src.ingestion.indexer import ChromaIndexer

# Initialize the FastMCP Server
mcp = FastMCP("Scientific Article Server")

# Database connection 
db_client = ChromaIndexer(persist_directory="data/vector_store/")

# --- TOOLS ---

@mcp.tool()
def search_articles(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    CRITICAL FOR CLASSIFICATION. 
    Use this tool to find the most semantically similar articles in the database.

    HOW TO USE FOR CLASSIFICATION:
    1. Pass relevant information or summary of the input article as the 'query'.
    2. Analyze the 'area' field of the returned results.
    3. If the top results are mostly 'Physics', classify the input as 'Physics'.

    Args:
        query: The text content or summary of the article you are analyzing. (e.g., "optimization in solar energy...").
        n_results: The number of top matches to return (default: 3).

    Returns:
        A list with n_results of elements, where each element is a dictionary contains:
        - id: The unique article ID (needed for get_article_content).
        - title: The title of the paper.
        - area: The scientific field/area.
        - score: A similarity score (lower is better).
    """
    results = db_client.collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["metadatas", "distances"] 
    )

    # Flatten the ChromaDB result structure for the Agent
    output = []
    if results['ids']:
        for i in range(len(results['ids'][0])):
            output.append({
                "id": results['ids'][0][i],
                "title": results['metadatas'][0][i].get("title", "Unknown"),
                "area": results['metadatas'][0][i].get("area", "Unknown"),
                "score": results['distances'][0][i] 
            })
    
    return output


@mcp.tool()
def get_article_content(article_id: str) -> Dict[str, Any]:
    """
    Retrieve the full text content of a specific article using its ID.

    This function should be used **only after** performing an `article_search`
    and determining that it is not possible to classify the input article based
    solely on the search results.

    Steps to follow:
        1. Identify one relevant `article_id` that you want to examine in depth.
        2. Analyze the `content` field returned by this function.
        3. Compare that content with the summary of the input article and decide
           whether the article should be classified in the given area.

    Args:
        article_id (str): The unique string ID of the article (obtained from
            `search_articles`).

    Returns:
        dict: A dictionary containing:
            - id (str): The unique article ID.
            - title (str): The article title.
            - content (str): The full text content of the article.
            - error (str, optional): Included if the ID was not found.
    """
    result = db_client.collection.get(
        ids=[article_id],
        include=["documents", "metadatas"]
    )

    if not result['ids']:
        return {"error": f"Article with ID {article_id} not found."}

    return {
        "id": result['ids'][0],
        "title": result['metadatas'][0].get("title", "Unknown"),
        "area": result['metadatas'][0].get("area", "Unknown"),
        "content": result['documents'][0] # The full chunk text
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")

