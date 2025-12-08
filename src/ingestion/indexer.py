import nltk

# Download required NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import sent_tokenize

def chunk_text_by_sentences(text: str, max_sentences: int = 5, overlap: int = 1) -> list:
    """
    Chunk text into smaller segments based on a maximum number of sentences with overlap.

    Args:
        text (str): The input text to be chunked.
        max_sentences (int): The maximum number of sentences per chunk.
        overlap (int): The number of sentences to overlap between chunks (default: 1).

    Returns:
        list: A list of text chunks, each containing up to max_sentences sentences,
              with overlap sentences from the previous chunk.
    """
    sentences = sent_tokenize(text)
    chunks = []
    
    i = 0
    while i < len(sentences):
        # Take max_sentences starting from current position
        chunk = ' '.join(sentences[i:i + max_sentences])
        chunks.append(chunk)
        
        # Move forward by (max_sentences - overlap) to create overlap
        i += max_sentences - overlap
    
    return chunks

if __name__ == "__main__":
    sample_text = ("This is the first sentence. Here is the second sentence. "
                   "This makes the third sentence. Now we have the fourth. "
                   "Finally, this is the fifth sentence. And this is the sixth.")
    
    chunks = chunk_text_by_sentences(sample_text, max_sentences=3)
    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx + 1}:\n{chunk}\n")

