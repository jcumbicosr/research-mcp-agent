import re
import datetime
from pypdf import PdfReader
from pathlib import Path
from typing import Dict

def load_and_clean_pdf(pdf_path: str) -> Dict[str, str]:
    """
    Load and extract text content from a PDF file.
    Args:
        pdf_path (str): The file path to the PDF document to be loaded.
    Returns:
        Dict[str, str]: A dictionary containing metadata and the complete text content extracted from all pages of the PDF.
    Raises:
        FileNotFoundError: If the PDF file does not exist at the specified path.
    Notes:
        - Uses layout extraction mode to maintain reading order in multi-column documents.
        - Each page's text is separated by a newline character in the output.
        - Returns an empty dictionary if an error occurs during loading.
    """
    path = Path(pdf_path)

    try:
        # Verify that the file exists
        if not path.exists():
            raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    
        # Initiate PDF reader
        reader = PdfReader(path)

        # Extract metadata
        meta = reader.metadata
        title = meta.title if meta and meta.title else "Unknown Title"
        author = meta.author if meta and meta.author else "Unknown Author"
        keywords = meta.keywords if meta and meta.keywords else "No Keywords"
        date = meta.creation_date if meta and meta.creation_date else "Unknown Date"
        if isinstance(date, datetime.datetime):
            date = date.strftime("%Y-%m-%d")

        # Extract text from each page
        text = ""
        for page in reader.pages:
            # extraction_mode="layout" helps maintain reading order in some multi-column papers
            page_text = page.extract_text(extraction_mode="layout")
            text += page_text + "\n"
        
        # Clean the extracted text
        text = clean_text(text)

        return {
            "title": title,
            "author": author,
            "keywords": keywords,
            "date": date,
            "text": text
        }
    
    except Exception as e:
        print(f"An error occurred while loading the PDF: {e}")
        return {}

def clean_text(raw_text: str) -> str:
    """
    Clean and normalize text extracted from documents.

    Performs the following operations in sequence:
    1. De-hyphenation: Removes hyphens and newlines that split words across lines
    2. Newline normalization: Converts single newlines to spaces while preserving paragraph breaks (double newlines)
    3. Citation removal: Strips both numerical citations [1], [1, 2], [1-3] and author-year citations (Author, Year)
    4. Reference section removal: Removes the References/Bibliography section from the end of the document

    Args:
        raw_text (str): The raw text to clean, typically extracted from a PDF or document.

    Returns:
        str: The cleaned and normalized text with citations and reference sections removed.
    """

    # 1. De-hyphenation
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', raw_text)

    # 2. Fix other newlines
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # 3. Remove Citations 
    # Pattern for [1], [1, 2], [1-3]
    text = re.sub(r'\[\d+(?:,\s*\d+|-\d+)*\]', '', text) 
    # Pattern for (Author, Year) or (Author et al., Year) - Simplified
    text = re.sub(r'\([A-Za-z\s.,&]+ \d{4}\)', '', text)

    # 4. Remove Reference Section
    split_pattern = r'\s*(?:References|Bibliography|BIBLIOGRAPHY|REFERENCES)\s*'
    parts = re.split(split_pattern, text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) > 1:
        # If found, take the first part (content before references)
        text = parts[0]

    return text.strip()


if __name__ == "__main__":
    pdf_path = "data/raw_articles/economy/economy_01.pdf"
    pdf_data = load_and_clean_pdf(pdf_path)
    print(pdf_data.get("text", ""))