import argparse
import json
import logging

from research_mcp_agent.agent.graph import run_graph
from research_mcp_agent.ingestion.indexer import run_create
from research_mcp_agent.io import read_file_content, save_outputs


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_app(file_path: str = "samples/input_article_1.txt") -> None:
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
    # try:
    #     # Read Content
    #     input_text = read_file_content(file_path)
        
    #     # Run the Multi-Agent System
    #     logger.info("Starting Multi-Agent Workflow...")
    #     result = run_graph(input_text)

    #     # Output the result
    #     print(json.dumps(result, indent=4))

    #     # Save Files
    #     save_outputs(file_path, result)

    # except Exception as e:
    #     logger.critical(f"Execution Failed: {e}")
    #     exit(1)
    print("Runing the app...")



def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(description="Research MCP agent CLI tool.")
    
    # Create the subparser object
    # dest="command" helps you check which command was run if needed
    subparsers = parser.add_subparsers(title="Sub-commands",
                                       description='Available commands',
                                       help='Use "command --help" for more info',
                                       dest="command", 
                                       required=True)

    # --------------------------------------
    # Sub-command: run
    # --------------------------------------
    parser_run = subparsers.add_parser("run", help="Run Research mcp agent app")
    
    # Arguments specific to 'run'
    parser_run.add_argument("--file_path", 
                            type=str, 
                            default="samples/input_article_1.txt", 
                            help="Path to the input text file to be processed")
   
    parser_run.set_defaults(func=run_app)
    
    # --------------------------------------
    # Sub-command: create
    # --------------------------------------
    parser_create = subparsers.add_parser("create", help="Create the vector store from estructured folder")
    
    # Arguments specific to 'create'
    parser_create.add_argument("--input_dir",
                               type=str, 
                               default="data/raw_articles/", 
                               help="Directory containing structured folders with PDF files.")
    parser_create.add_argument("--reset_db", 
                               action='store_true', # False by default, True when present
                               help="Whether to reset the vector store database if it exists") 
    
    parser_create.set_defaults(func=run_create)

    # --- Parse and Dispatch ---
    args = parser.parse_args()

    # Dictionary unpacking
    args_dict = vars(args)
    func_to_call = args_dict.pop('func')
    command_name = args_dict.pop('command') # clean up extra keys

    # Unpack the remaining arguments directly into the function
    func_to_call(**args_dict)

if __name__ == "__main__":
    main()
