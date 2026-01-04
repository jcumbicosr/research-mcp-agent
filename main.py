import argbind
import json
import logging

from research_mcp_agent.agent.graph import run_graph
from research_mcp_agent.io import read_file_content, save_outputs


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@argbind.bind(without_prefix=True)
def main(file_path: str = "samples/input_article_1.txt") -> None:
    """
    Main entry point for the Multi-Agent System workflow.
    Orchestrates the complete pipeline: reading input content, executing the multi-agent
    system, displaying results, and saving outputs to files.
    Args:
        file_path (str): Path to the input text file to be processed. 
                        Defaults to "samples/input_article_1.txt".
    Raises:
        Exception: Logs critical errors and exits with status code 1 if any step fails.
    Returns:
        None
    """
    try:
        # Read Content
        input_text = read_file_content(file_path)
        
        # Run the Multi-Agent System
        logger.info("Starting Multi-Agent Workflow...")
        result = run_graph(input_text)

        # Output the result
        print(json.dumps(result, indent=4))

        # Save Files
        save_outputs(file_path, result)

    except Exception as e:
        logger.critical(f"Execution Failed: {e}")
        exit(1)


if __name__ == "__main__":
    args = argbind.parse_args()
    with argbind.scope(args):
        main()

