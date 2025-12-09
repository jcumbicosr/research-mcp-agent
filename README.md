# Research MCP Agent
This project implements a decoupled Multi-Agent architecture utilizing the Model Context Protocol (MCP). The system consumes a Vector Store knowledge base to classify scientific articles, perform structured data extraction (JSON), and generate automated critical reviews. The solution demonstrates efficient integration between AI Agents and external tools via MCP servers.

## 📂 Data Ingestion
The system employs a hierarchical directory structure to organize the knowledge base. The ingestion script (`loader.py`) recursively scans subdirectories within `data/raw_articles/`. The name of the subdirectory is automatically extracted and assigned as the "Area" metadata field for all contained documents.
```
data/
└── raw_articles/
    ├── Physics/
    │   ├── article1.pdf
    │   └── ...
    ├── Biology/
    │   └── ...
    └── Computer_Science/
        └── ...
```

### Pre-processing & Cleaning
Before indexing, raw PDF text undergoes a rigorous cleaning process to optimize retrieval quality:

* **Metadata Extraction:** automatically extracts Title, Authors, and Keywords from PDF properties.

* **Text Normalization:**

    * De-hyphenation: Rejoins words split across lines (e.g., "algo- rithm" → "algorithm").

    * Whitespace Fixes: Normalizes newlines while preserving paragraph structure.

* **Noise Reduction:**

    * Citation Removal: Strips numerical markers (e.g., `[1, 2]`) and inline citations (e.g., `(Author, 2023)`) to prevent context pollution.

    * Reference Truncation: Automatically detects and removes the "References" or "Bibliography" sections to reduce token usage and irrelevant matches.


## 🧩 Chunking Strategy
To maintain high retrieval accuracy, this project utilizes a Sentence-Aware Chunking strategy implemented via NLTK (`indexer.py`).

Unlike fixed-size character splitting, sentence-based chunking respects the natural linguistic structure of scientific writing. It ensures that sentences are never split in the middle, prioritizing semantic coherence.

Configuration:

* **Method:** NLTK Sentence Tokenization

* **Window Size:** 8 sentences per chunk (optimized to capture complete thoughts/arguments).

* **Overlap:** 1 sentence (preserves semantic continuity between adjacent chunks).

## 🗄️ Vector Store (ChromaDB)
The system uses **ChromaDB** as the persistent vector store.

* **Collection:** `scientific_articles`

* **Storage Path:** `data/vector_store/`

* **Metadata Filtering:** Each vector is indexed with its source filename, research area, and document metadata to allow for filtered queries (e.g., "Retrieve only from Computer_Science").