import os
import argbind
import json
import logging
import arxiv
from pathlib import Path
from pypdf import PdfReader
from tempfile import TemporaryDirectory

# Import the graph runner
from src.agent.graph import run_agent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _read_pdf(pdf_path: Path) -> str:
    """Read and extract text from a PDF file."""
    logger.info(f"Reading PDF file: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        full_text = "\n".join(text_parts)
        
        if not full_text.strip():
            logger.warning(f"No text extracted from PDF: {pdf_path}")
        
        return full_text

    except Exception as e:  
        logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
        raise

def _read_arxiv_url_file(path: Path) -> str:
    """
    Read a .url file containing an arXiv link, download the paper, and extract text.
    
    Args:
        path: Path to the .url file
        
    Returns:
        Extracted text from the arXiv paper
    """
    try:
        # Read URL from file
        with open(path, "r", encoding="utf-8") as f:
            url = f.read().strip()
        
        # Validate URL
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("Invalid URL format in .url file.")
        
        logger.info(f"Extracted URL: {url}")


        # Extract the arXiv ID from the URL
        arxiv_id = url.split('/')[-1]
        if ".pdf" in arxiv_id:
            arxiv_id = arxiv_id.replace(".pdf", "")
        
        logger.info(f"Extracted arXiv ID: {arxiv_id}")
        
        # Search for the paper
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(client.results(search))

        if not results:
            raise ValueError(f"No paper found for arXiv ID: {arxiv_id}")
        
        paper = results[0]
        logger.info(f"Found paper: {paper.title}")
        
        # Download and read PDF in temporary directory
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            pdf_filename = f"{arxiv_id.replace('/', '_')}.pdf"
            
            logger.info(f"Downloading paper to temporary location...")
            paper.download_pdf(dirpath=str(tmp_path), filename=pdf_filename)
            
            pdf_path = tmp_path / pdf_filename
            full_text = _read_pdf(pdf_path)
        
        return full_text
        
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to process arXiv URL file: {e}")
        raise

def _read_text_file(path: Path) -> str:
    """
    Read a plain text file.
    
    Args:
        path: Path to the text file
        
    Returns:
        File content
        
    Raises:
        Exception: If file cannot be read
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read text file {path}: {e}")
        raise

def read_file_content(file_path: str) -> str:
    """
    Robust file reader that handles multiple file types.
    
    Supports:
    - PDF files (.pdf): Extracts text from all pages
    - arXiv links (.url): Downloads paper from arXiv and extracts text
    - Plain text/markdown files: Reads content directly
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        Extracted text content from the file
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    logger.info(f"Reading file: {file_path}")
    
    # Route to appropriate handler based on file extension
    suffix = path.suffix.lower()
    
    if suffix == ".pdf":
        return _read_pdf(path)
    elif suffix == ".url":
        return _read_arxiv_url_file(path)
    else:
        return _read_text_file(path)


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