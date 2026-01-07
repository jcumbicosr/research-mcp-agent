# 🧠 Research MCP Agent

This project implements a decoupled **Multi-Agent architecture** designed to automate the analysis of scientific literature. It leverages **LangGraph** for orchestration and the **Model Context Protocol (MCP)** to ground agentic reasoning in a local vector database.

The system performs three key tasks autonomously:
1.  **Classification:** Identifies the scientific domain of an input text (PDF, URL, or Text) by comparing it against a curated knowledge base of **9 articles** across **3 scientific areas**.
2.  **Extraction:** Performs structured data extraction (JSON) of problem statements and methodologies, strictly adhering to the requested schema.
3.  **Critical Review:** Generates a comprehensive critical review in Portuguese.

---

## 🏗️ Architectural Decisions & Framework Justification

To ensure **flexibility, comprehensiveness, and scalability**, the following stack was chosen:

| Component | Choice | Justification |
| :--- | :--- | :--- |
| **Orchestration** | **LangGraph** | Chosen over **CrewAI** or **AutoGen**. While CrewAI is good for generic role-playing, **LangGraph** provides fine-grained control over state and execution flow (`Classify -> Extract -> Review`). It allows for a deterministic pipeline essential for this specific challenge, avoiding the infinite loops common in "chatty" multi-agent frameworks. |
| **Connectivity** | **MCP (FastMCP)** | Decouples the "Brain" (Agent) from the "Knowledge" (Vector Store). This allows the Vector Store to be swapped or hosted remotely without changing the Agent's code. |
| **Vector Store** | **ChromaDB** | Selected for its simplicity and local persistence (no Docker required for evaluation), making the repository easier to clone and run. |
| **LLM** | **Gemini 2.5** | High context window and superior reasoning speed for document analysis. |

---

## 🚀 Getting Started

This guide provides step-by-step instructions to set up and run the **Research MCP Agent** on any host machine.

## 📋 Prerequisites

* **Python 3.12**
* **uv** (An extremely fast Python package installer and resolver).
    * *Install uv:* `curl -LsSf https://astral.sh/uv/install.sh | sh`

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/jcumbicosr/research-mcp-agent.git
    cd research-mcp-agent
    ```

2.  **Set up Virtual Environment & Install Dependencies**
    We use `uv` to manage dependencies and install the app as an editable package. This exposes the `research-mcp-agent` command in your terminal.
    ```bash
    # Create a virtual environment and install dependencies
    uv sync

    # Activate the environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    .venv\Scripts\activate
    ```

3.  **Configuration**
    Create a `.env` file in the root directory to store your API keys.
    ```bash
    touch .env
    ```
    Open `.env` and add your Google Gemini API key:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```  
4.  **Create the vector store** To create the vector store based on the ingestion structure folder (see Data Ingestion section), run the following command using the exposed CLI:
    ```bash
    research-mcp-agent create --input_dir data/raw_articles
    ```
---
## 🏃 Running the Agent

You can now run the agent directly using the `research-mcp-agent` command. The tool supports three types of input files via the `--file_path` argument.

### Option A: Analyze Raw Text
Processes a plain text or markdown file.
```bash
research-mcp-agent run --file_path samples/input_article_1.txt
```

### Option B: Analyze a PDF File
Directly processes a local PDF.
```bash
research-mcp-agent run --file_path samples/input_article_2.pdf
```

### Option C: Analyze an arXiv Paper (.url)
Create a `.url` file containing a single arXiv link (e.g., `https://arxiv.org/abs/2310.xxxxx`).
```bash
research-mcp-agent run --file_path samples/input_article_3.url
```
The system will automatically download the paper, extract text, and process it.

## 📦 Outputs & Artifacts
For every execution, the system generates three files in the same directory as the input file, appended with the base filename:

| File | Description |
|------|-------------|
| _full.json | The complete structured output (Area, Extraction, Review).|
| _extraction.json | JSON containing only the problem statement and methodology.|
| _review.md | The critical review in Markdown format (Portuguese).```
------------------

1. Extraction JSON  
    Matches the requested schema (including the artcle typo handling). File: `*_extraction.json`
    ```JSON
    {
    "what problem does the artcle propose to solve?": "Extracted text...",
    "step by step on how to solve it": ["Step 1", "Step 2"],
    "conclusion": "Conclusion text..."
    }
    ```
2. Critical Review (Portuguese)  
    A detailed markdown review including:
    * Pontos Positivos (Strengths)
    * Possíveis Falhas (Weaknesses/Methodology Checks)
    * Comentários Finais

## 📂 Data Ingestion
The system employs a hierarchical directory structure to organize the knowledge base. The ingestion script (`loader.py`) recursively scans subdirectories within `raw_articles/`. The name of the subdirectory is automatically extracted and assigned as the "Area" metadata field for all contained documents.
```
raw_articles/
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

* **Storage Path:** `vector_store/`

* **Metadata Filtering:** Each vector is indexed with its source filename, research area, and document metadata to allow for filtered queries (e.g., "Retrieve only from Computer_Science").

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

## Research MCP Agent

This project implements a decoupled **Multi-Agent architecture** designed to automate the analysis of scientific literature. It leverages **LangGraph** for orchestration and the **Model Context Protocol (MCP)** to ground agentic reasoning in a local vector database.

The system performs three key tasks autonomously:
1.  **Classification:** Identifies the scientific domain of an input text by comparing it against a known knowledge base.
2.  **Extraction:** Performs structured data extraction (JSON) of problem statements and methodologies.
3.  **Critical Review:** Generates a comprehensive critical review in Portuguese.

---

## 🏗️ Architecture

The system is built as a state machine using **LangGraph**. The workflow consists of three specialized nodes that pass a shared state (`AgentState`) sequentially.

```mermaid
graph LR
    Start --> Classify[Classifier Node]
    Classify --> Extract[Extractor Node]
    Extract --> Review[Reviewer Node]
    Review --> End

