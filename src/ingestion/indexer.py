import nltk
from typing import List, Dict

# Download required NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import sent_tokenize

def chunk_text_by_sentences(raw_text: str, max_sentences: int = 5, overlap: int = 1) -> list:
    """
    Chunk text into smaller segments based on a maximum number of sentences with overlap.

    Args:
        raw_text (str): The input text to be chunked.
        max_sentences (int): The maximum number of sentences per chunk.
        overlap (int): The number of sentences to overlap between chunks (default: 1).

    Returns:
        list: A list of text chunks, each containing up to max_sentences sentences,
              with overlap sentences from the previous chunk.
    """
    sentences = sent_tokenize(raw_text)
    chunks = []
    
    i = 0
    while i < len(sentences):
        # Take max_sentences starting from current position
        chunk = ' '.join(sentences[i:i + max_sentences])
        chunks.append(chunk)
        
        # Move forward by (max_sentences - overlap) to create overlap
        i += max_sentences - overlap
    
    return chunks

def chunk_pdfs(documents: List[Dict[str, str]], max_sentences: int = 5, overlap: int = 1) -> List[Dict[str, str]]:
    """
    Chunk the 'text' of each PDF document in the list into smaller segments
    based on a maximum number of sentences with overlap.

    Args:
        documents (list): A list of dictionaries, each containing a 'text' key with text.
        max_sentences (int): The maximum number of sentences per chunk.
        overlap (int): The number of sentences to overlap between chunks (default: 1).

    Returns:
        list: A new list of dictionaries where each original document is replaced
              by its chunks, each represented as a separate dictionary.
    """
    chunked_documents = []
    
    for doc in documents:
        content = doc.get('text', '')
        chunks = chunk_text_by_sentences(content, max_sentences, overlap)
        
        for idx, chunk in enumerate(chunks):
            new_doc = doc.copy()
            new_doc['text'] = chunk
            new_doc['chunk_index'] = idx
            chunked_documents.append(new_doc)
    
    return chunked_documents

if __name__ == "__main__":
    # Example usage
    sample_documents = [
        {'text': "This is the first sentence. Here is the second sentence. This makes the third sentence. Fourth sentence is here. Finally, this is the fifth sentence."},
        {'text': "Another document starts here. It has its own sentences. This is the third one. Fourth comes next. And finally, the fifth sentence."}
    ]
    
    chunked_docs = chunk_pdfs(sample_documents, max_sentences=3, overlap=1)
    
    for doc in chunked_docs:
        print(f"Chunk Index: {doc['chunk_index']}, Text: {doc['text']}\n")

