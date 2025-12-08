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

        # Extract text from each page
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            text += page_text + "\n"
        
        # Clean the extracted text
        text = clean_text(text)

        return {
            "title": title,
            "authors": author,
            "keywords": keywords,
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

def process_pdfs(directory: str="data/raw_articles/"):
    """
    Process all PDF files in a directory and its subdirectories.
    Recursively iterates through subdirectories, loads and cleans PDF files,
    and enriches them with metadata including the area (subdirectory name) and filename.
    Args:
        directory (str): Path to the directory containing subdirectories with PDF files.
    Returns:
        list: A list of dictionaries containing processed PDF data with the following keys:
            - Existing keys from load_and_clean_pdf output
            - 'area' (str): Name of the subdirectory where the PDF was found
            - 'filename' (str): Name of the PDF file
    Raises:
        NotADirectoryError: If the specified directory does not exist or is not a directory.
    """

    dir = Path(directory)

    if not dir.exists() or not dir.is_dir():
        raise NotADirectoryError(f"The directory {directory} does not exist or is not a directory.")
    
    # Iterate over all subdirectories
    documents = []
    for subdir in dir.iterdir():
        if subdir.is_dir():
            # Process PDFs in the subdirectory
            print(f"Processing area: {subdir.name}...")

            for pdf_file in subdir.glob("*.pdf"):
                pdf_data = load_and_clean_pdf(pdf_file)
                
                # Add metadata
                if pdf_data:
                    pdf_data['area'] = subdir.name
                    pdf_data['filename'] = pdf_file.name
                    
                    documents.append(pdf_data)

    return documents

if __name__ == "__main__":
    docs = process_pdfs()
    print(f"Processed {len(docs)} documents.")