import nltk
import chromadb
from pathlib import Path
from typing import List, Dict


# Download required NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import sent_tokenize

def chunk_text_by_sentences(raw_text: str, max_sentences: int = 5, overlap: int = 1) -> List[str]:
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
    global_index = 0
    for doc in documents:
        content = doc.get('text', '')
        chunks = chunk_text_by_sentences(content, max_sentences, overlap)
        
        for chunk in chunks:
            new_doc = doc.copy()
            new_doc['text'] = chunk
            new_doc['index'] = f"id{global_index}"
            chunked_documents.append(new_doc)
            global_index += 1
    
    return chunked_documents

class ChromaIndexer:
    def __init__(self, persist_directory: str = "data/vector_store/"):
        """
        Initialize a ChromaDB client with persistent storage.

        Args:
            persist_directory (str): Directory path for persistent storage.
        """
        path_dir = Path(persist_directory)
        path_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.Client(chromadb.config.Settings(
            persist_directory=persist_directory
        ))

        self.collection = self.client.get_or_create_collection(name="scientific_articles")
        if self.collection.count() == 0:
            print("The ChromaDB collection is void. Run create_collection() to initialize it.")
        
    def create_collection(self, documents: List[Dict[str, str]]):
        """
        Add documents to the ChromaDB collection.
        
        Args:
            documents: List of dicts with 'text', 'index', and any other metadata fields
        """
        texts = []
        metadatas = []
        ids = []
        
        for doc in documents:
            # Extract text (required)
            texts.append(doc['text'])
            
            # Extract ID (required)
            ids.append(str(doc['index']))  # Ensure ID is a string
            
            # Extract all other keys as metadata
            metadata = {k: v for k, v in doc.items() if k not in ['text', 'index']}
            # If no metadata exists, add a placeholder
            if not metadata:
                metadata = {'source': 'default'}
            
            metadatas.append(metadata)
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

if __name__ == "__main__":
    # Example usage
    sample_documents = [
        {'text': "This is the first sentence. Here is the second sentence. This makes the third sentence. Fourth sentence is here. Finally, this is the fifth sentence."},
        {'text': "Another document starts here. It has its own sentences. This is the third one. Fourth comes next. And finally, the fifth sentence."}
    ]
    
    chunked_docs = chunk_pdfs(sample_documents, max_sentences=3, overlap=1)
    
    for doc in chunked_docs:
        print(f"Chunk Index: {doc['index']}, Text: {doc['text']}\n")

    vector_db = ChromaIndexer()
    vector_db.create_collection(chunked_docs)

