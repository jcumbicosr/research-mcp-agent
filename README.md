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


## 🤖 MCP Server Architecture
This project exposes the knowledge base to AI agents using the **Model Context Protocol (MCP)** via a `FastMCP` server. This architecture decouples the database logic from the agentic reasoning, allowing the agent to "consult" the literature dynamically.

## 🤖 MCP Server Architecture

This project exposes the knowledge base to AI agents using the **Model Context Protocol (MCP)** via a `FastMCP` server. This architecture decouples the database logic from the agentic reasoning, allowing the agent to "consult" the literature dynamically.

### Server Tools
The server exposes two primary tools designed to support an **Agentic Classification Workflow**:

#### 1. `search_articles`
**Purpose:** Semantic Search & Classification Helper. This is the primary entry point for the agent. It performs a semantic search on the Vector Store to find the most relevant articles based on a query or summary.
* **Inputs:** `query` (str), `n_results` (int, default=3).
* **Output:** List of article metadata (ID, Title, Area, Similarity Score).
* **Agent Strategy:** The agent uses this tool to infer the classification of a new input text by analyzing the `area` field of the nearest neighbors returned by this search.


#### 2. `get_article_content`
**Purpose:** Deep Inspection & Verification. Retrieves the full text content of a specific chunk/article using its ID.
* **Inputs:** `article_id` (str).
* **Output:** List of article metadata (ID, Title, Area, Content).
* **Agent Strategy:** Used when search results are ambiguous (e.g., mixed areas). The agent calls this tool to read the full content of a similar article to make a more informed decision.
