# HITAM_AI-RAG

**AI-Powered Conversational Retrieval System** — A state-of-the-art platform that transforms user queries into context-aware semantic responses via retrieval-augmented generation.

---

## AI OVERVIEW
A visionary AI-engineered platform orchestrating deep embeddings, dynamic memory, and real-time conversational intelligence. Every component resonates with intelligent design, amplifying user queries into semantically enriched responses.

---

## AI-Powered FEATURES
- **Streamlit Neural Interface**: Rapid AI UI deployment for intuitive human–AI interaction.
- **OpenAI Semantic Embeddings**: Transformer-driven embeddings capturing contextual nuance.
- **Pinecone Vector Intelligence**: Persistent AI-backed vector store for ultra-fast similarity search.
- **Retrieval-Augmented Chain**: LangChain-powered AI pipeline unifying retrieval and generation.
- **Cognitive Memory Module**: Persistent conversational AI memory for contextual continuity.
- **Prompt Engineering Suite**: AI-crafted prompts delivering precision-guided responses.

---

## AI INSTALLATION
1. Clone the AI repository:
   ```bash
   git clone https://github.com/Shindevrp/hitam_ai.git
   cd hitam_ai
   ```
2. Initialize AI environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install AI dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

##  AI CONFIGURATION
1. Create `creds.py` at project root with:
   ```python
   openai_key = "YOUR_OPENAI_API_KEY"
   PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
   index_name = "YOUR_PINECONE_INDEX_NAME"
   ```
2. Ensure AI keys have vector store and embedding access.

---

## AI USAGE
Launch the AI interface and ignite semantic dialogues:
```bash
streamlit run app.py
```
Enter queries to witness AI-driven retrieval and generative synthesis in real time.

---

##  SYSTEM ARCHITECTURE
A detailed overview of how components interact end-to-end:

```mermaid
flowchart LR
    subgraph UI
        A[Streamlit Front-End]
    end
    subgraph Core
        B[Query Processor] --> C[Embedding Generator]
        C --> D[Pinecone Vector Store]
        D --> E[Retrieval Engine]
        E --> F[LLM (OpenAI)]
        F --> G[Response Formatter]
    end
    subgraph Memory
        H[SQLite Chat History]
    end
    subgraph Config
        I[creds.py]
    end
    A --> B
    E --> H
    H --> E
    G --> A
    I --> B
```

###  Each module:
- **Streamlit Front-End**: Collects user queries and renders AI responses.
- **Query Processor**: Orchestrates embedding requests and retrieval routines.
- **Embedding Generator**: Uses OpenAI embeddings to encode text into semantic vectors.
- **Pinecone Vector Store**: Indexes and searches vectors for similarity.
- **Retrieval Engine**: Gathers relevant content chunks for context enrichment.
- **LLM (OpenAI)**: Generates thoughtful, context-aware responses.
- **Response Formatter**: Applies prompt engineering templates and formats output.
- **SQLite Chat History**: Persists conversation turns for long-term context continuity.
- **Configuration (creds.py)**: Centralizes API keys and index parameters.

---

##  AI FILE STRUCTURE
```
├── app.py                            # Streamlit AI interface
├── creds.py                          # AI credentials placeholder
├── chat_history.db                   # AI conversation memory store
├── Conversational_Retrieval_Chain_2.py  # AI RAG pipeline
├── doc2vectordb.py                   # AI embedding generator
├── memory.py                         # AI context manager
├── prompts.py                        # AI prompt definitions
├── requirements.txt                  # AI dependency manifest
└── README.md                         # AI project manifesto
```

---

## AI CONTRIBUTING
Neural contributions are welcome. Fork, commit your AI enhancements, and submit pull requests. For issues, raise an AI ticket in GitHub Issues.

---

> _Coded with intelligence, deployed with intent — the future of AI-driven conversation begins here._

