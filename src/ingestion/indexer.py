import nltk
import chromadb
from pathlib import Path
from typing import List, Dict, Any
from .loader import process_pdfs


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
    def __init__(self, persist_directory: str = "data/vector_store/") -> None:
        """
        Initialize a ChromaDB client with persistent storage.

        Args:
            persist_directory (str): Directory path for persistent storage.
        """
        path_dir = Path(persist_directory)
        path_dir.mkdir(parents=True, exist_ok=True)

        # Use PersistentClient
        self.client = chromadb.PersistentClient(path=persist_directory)

        self.collection = self.client.get_or_create_collection(name="scientific_articles")
        if self.collection.count() == 0:
            print("The ChromaDB collection is void. Run create_collection() to initialize it.")
        else:
            print(f"Loaded existing collection with {self.collection.count()} documents.")
        
    def create_collection(self, documents: List[Dict[str, str]]) -> None:
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
        print(f"Added {len(documents)} documents. Total in collection: {self.collection.count()}")

    def query(self, query_texts: List[str], n_results: int = 1) -> Dict[str, Any]:
        """
        Query the collection for similar items based on input text.
        
        Args:
            query_texts (List[str]): A list of query strings to search for in the collection.
            n_results (int, optional): The number of results to return for each query. Defaults to 1.
        
        Returns:
            Dict[str, Any]: A dictionary containing the query results from the collection.
        """
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=["metadatas", "distances", "documents"]
        )

        # Flatten the ChromaDB result structure
        output = {
            'ids': results['ids'][0] if results.get('metadatas') else [],
            'documents': results['documents'][0] if results.get('documents') else [],
            'distances': results['distances'][0] if results.get('distances') else [],
        }

        # Flatten metadata keys into top-level dictionary
        if results.get('metadatas') and results['metadatas'][0]:
            # Collect all unique metadata keys
            all_metadata_keys = set()
            for metadata in results['metadatas'][0]:
                all_metadata_keys.update(metadata.keys())
            
            # Create a list for each metadata key
            for key in all_metadata_keys:
                output[key] = [
                    metadata.get(key, None) for metadata in results['metadatas'][0]
                ]
        
        return output
    
def main():
    # Load and clead pdf files, add metadata
    docs = process_pdfs(directory="data/raw_articles/")
    # Chunk text
    docs = chunk_pdfs(documents=docs, max_sentences=8, overlap=1)
    # Create vector store
    vector_db = ChromaIndexer(persist_directory="data/vector_store")
    vector_db.create_collection(documents=docs)
    # Test retrieve
    results = vector_db.query(["Sentence talking about machine learning."], n_results=2)
    print(f"Retrieve docs:\n{results['documents']}")


if __name__ == "__main__":
    main()

    # Example usage
    # sample_documents = [
    #     {'text': "This is the first sentence. Here is the second sentence. This makes the third sentence. Fourth sentence is here. Finally, this is the fifth sentence."},
    #     {'text': "Another document starts here. It has its own sentences. This is the third one. Fourth comes next. And finally, the fifth sentence."}
    # ]
    
    # chunked_docs = chunk_pdfs(sample_documents, max_sentences=3, overlap=1)
    
    # for doc in chunked_docs:
    #     print(f"Chunk Index: {doc['index']}, Text: {doc['text']}\n")

    # vector_db = ChromaIndexer()
    # vector_db.create_collection(chunked_docs)

    # results = vector_db.query(["First sentence"], n_results=2)
    # print(f"Retrieve docs:\n{results['documents']}")

