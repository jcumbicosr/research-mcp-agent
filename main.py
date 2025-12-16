import os
import argbind
import json
import logging
from pathlib import Path
from pypdf import PdfReader

# Import the graph runner
from src.agent.graph import run_agent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_file_content(file_path: str) -> str:
    """
    Robust file reader. Handles PDFs and plain text files.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    logger.info(f"Reading file: {file_path}")

    full_text = ""
    # Read PDF
    if path.suffix.lower() == ".pdf":
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                page_text = page.extract_text()
                full_text += page_text + "\n"
            
            return full_text

        except Exception as e:
            logger.error(f"Failed to read PDF: {e}")
            raise
    
    # Assume text file or markdown
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                full_text = f.read()
            
            return full_text
        
        except Exception as e:
            logger.error(f"Failed to read text file: {e}")
            raise



@argbind.bind(without_prefix=True)
def main(file_path: str = "samples/input_article_1.txt"):
    
    try:
        # 1. Read Content
        input_text = read_file_content(file_path)
        
        # 2. Run the Multi-Agent System
        logger.info("Starting Multi-Agent Workflow...")
        result = run_agent(input_text)
        
        
    except Exception as e:
        logger.critical(f"Execution Failed: {e}")
        exit(1)

if __name__ == "__main__":
    args = argbind.parse_args()
    with argbind.scope(args):
        main()