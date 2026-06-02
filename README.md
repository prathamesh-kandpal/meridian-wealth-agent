# Meridian Wealth Partners - AI Agent Workspace

An agentic AI financial workspace built using **LangGraph** and **FastAPI** to manage client relationship data, analyze live portfolio holdings from an internal SQLite engine, and perform context-aware compliance checks using RAG (Retrieval-Augmented Generation) against firm policy documentation.

---

## 🏗️ Project Architecture & Layout

The project enforces strict separation of concerns across data storage, backend tools, and agent graph orchestration state machines:

```text
meridian-wealth-agent/
│
├── data/
│   ├── faiss_index/          # Local vector storage embeddings for RAG lookup
│   ├── policy documents/     # Extracted internal PDF compliance books
│   └── meridian_wealth       # Core SQLite database binary snapshot
│
├── source/
│   ├── agents.py             # LangGraph core orchestration & state graph loops
│   ├── database_queries.py   # Secure parameterized tools (Portfolio Lookup, Metrics)
│   └── rag_pipeline.py       # Document chunking, indexing, and vector similarity retrieval
│
├── app.py                    # Application Entrypoint (FastAPI + Uvicorn server runtime)
├── .gitignore                # Absolute exclusion tracking matrix (Venv, Secrets, Keys)
└── README.md                 # System documentation manual
