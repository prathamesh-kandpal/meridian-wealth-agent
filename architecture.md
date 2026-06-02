# Financial Analyst Agent - System Architecture

## Overview

The Financial Analyst Agent is a FastAPI-based AI application that combines:

- Agentic AI Workflow (LangGraph)
- Retrieval Augmented Generation (RAG)
- SQLite Database Querying
- FAISS Vector Search
- Policy Document Analysis
- Interactive Chat UI

The system is designed using a clean separation of concerns where:

- FastAPI handles application serving
- LangGraph handles reasoning and orchestration
- SQLite stores financial data
- FAISS stores policy document embeddings
- HTML/CSS/JavaScript provides the user interface

---

# High-Level Architecture

```text
┌─────────────────────────────────────┐
│             End User                │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│          Chat Interface             │
│                                     │
│  chat.html + CSS + JavaScript       │
└─────────────────┬───────────────────┘
                  │
        HTTP Request (/chat)
                  │
                  ▼
┌─────────────────────────────────────┐
│              FastAPI                │
│                                     │
│             app.py                  │
│                                     │
│  GET  /                            │
│  GET  /health                      │
│  GET  /agentinfo                   │
│  POST /chat                        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      FinancialAnalystAgent          │
│                                     │
│            agents.py                │
└─────────────────┬───────────────────┘
                  │
                  ▼
         LangGraph Workflow
                  │
                  ▼
┌─────────────────────────────────────┐
│            Router Node              │
└───────┬─────────────────┬───────────┘
        │                 │
        ▼                 ▼

 Database Path      Policy/RAG Path

        │                 │
        ▼                 ▼

┌──────────────┐   ┌─────────────────┐
│ SQLite DB    │   │  FAISS Vector   │
│ Queries      │   │  Search         │
└──────────────┘   └─────────────────┘

        │                 │
        └───────┬─────────┘
                │
                ▼

      Financial Analysis Node

                │
                ▼

         Final Response

                │
                ▼

        Chat UI Rendering
```

---

# Application Flow

## Step 1 - User Query

User submits a question through the web interface.

Example:

```text
What is the AUM of Meridian Equity Fund?
```

The frontend JavaScript sends:

```json
{
  "question": "What is the AUM of Meridian Equity Fund?"
}
```

to:

```http
POST /chat
```

---

## Step 2 - FastAPI Receives Request

FastAPI validates the request using:

```python
ChatRequest
```

defined in:

```text
source/schemas.py
```

and forwards it to:

```python
FinancialAnalystAgent.invoke()
```

---

## Step 3 - LangGraph Agent Execution

The LangGraph workflow begins.

### Router Node

The router determines which information source is required.

Possible routes:

| Query Type | Route |
|------------|--------|
| Financial metrics | Database |
| Policy questions | RAG |
| Hybrid question | Database + RAG |
| Analytical question | Database + Analysis |

---

## Step 4A - Database Route

When structured financial data is required:

```text
source/database_queries.py
```

is used.

### Responsibilities

- SQLite connection
- Query execution
- Data aggregation
- Financial calculations

Database:

```text
data/
└── meredian_wealth.db
```

Example:

```sql
SELECT *
FROM funds
WHERE fund_name = 'Meridian Equity Fund'
```

---

## Step 4B - Policy Retrieval Route

When policy knowledge is required:

```text
source/rag_pipeline.py
```

is used.

### Responsibilities

- Load vector store
- Similarity search
- Retrieve document chunks
- Return context

Knowledge Base:

```text
data/
└── policy_documents/
```

Vector Store:

```text
vector_store/
└── faiss_index/
```

---

## Step 5 - FAISS Retrieval

The RAG pipeline:

1. Converts user question into embeddings
2. Searches FAISS index
3. Retrieves relevant chunks
4. Returns context

```text
Question
    │
    ▼
Embedding
    │
    ▼
FAISS Search
    │
    ▼
Top K Chunks
    │
    ▼
Context Returned
```

---

## Step 6 - Financial Analysis Layer

The analysis node combines:

- User question
- Database results
- Policy context

and generates a final response using the LLM.

Example:

```text
Input:
- AUM data
- Fund performance data
- Policy constraints

Output:
- Financial insight
- Recommendation
- Explanation
```

---

## Step 7 - Execution Trace Capture

Every node execution is tracked.

Example:

```json
[
  {
    "node": "router",
    "output": "database"
  },
  {
    "node": "database_tool",
    "output": "Retrieved fund metrics"
  },
  {
    "node": "analyst",
    "output": "Generated final analysis"
  }
]
```

This trace is returned to the frontend.

---

## Step 8 - Response Returned

FastAPI returns:

```json
{
  "answer": "...",
  "execution_steps": [...],
  "sources": [...],
  "success": true
}
```

---

## Step 9 - Frontend Rendering

The frontend displays:

```text
User Question
      │
      ▼
Execution Flow
      │
      ▼
Final Answer
```

Example:

```text
-----------------------------------
Question
-----------------------------------

What is the AUM of Meridian Equity Fund?

-----------------------------------
Execution Steps
-----------------------------------

✓ Router

✓ Database Tool

✓ Financial Analyst

-----------------------------------
Answer
-----------------------------------

Meridian Equity Fund currently
manages assets worth...
```

---

# Persistent Vector Database Flow

The vector database is intentionally separated from application startup.

## Initial Index Build

```text
vector_store/
└── build_index.py
```

reads:

```text
data/policy_documents/
```

and creates:

```text
vector_store/faiss_index/
├── index.faiss
├── index.pkl
└── metadata.json
```

---

## Application Startup

FastAPI startup:

```text
Load Existing FAISS Index
        │
        ▼
No Re-Embedding
        │
        ▼
No Re-Chunking
        │
        ▼
Instant Startup
```

This prevents expensive indexing every time the application restarts.

---

# API Endpoints

## GET /

Serves:

```text
chat.html
```

Main application interface.

---

## GET /health

Health monitoring endpoint.

Response:

```json
{
  "status": "healthy",
  "agent": "ready",
  "database": "connected",
  "vector_store": "loaded"
}
```

---

## GET /agentinfo

Returns metadata about the agent.

Response:

```json
{
  "agent_name": "Financial Analyst Agent",
  "version": "1.0.0",
  "database": "SQLite",
  "vector_store": "FAISS"
}
```

---

## POST /chat

Main conversational endpoint.

Input:

```json
{
  "question": "..."
}
```

Output:

```json
{
  "answer": "...",
  "execution_steps": [...],
  "sources": [...],
  "success": true
}
```

---

# Project Directory Structure

```text
financial-analyst-agent/
│
├── app.py
│
├── source/
│   ├── agents.py
│   ├── schemas.py
│   ├── rag_pipeline.py
│   └── database_queries.py
│
├── vector_store/
│   ├── build_index.py
│   └── faiss_index/
│
├── data/
│   ├── meredian_wealth.db
│   └── policy_documents/
│
├── frontend/
│   ├── templates/
│   │   └── chat.html
│   │
│   └── static/
│       ├── css/
│       │   └── chat.css
│       │
│       └── js/
│           ├── chat.js
│           └── api.js
│
├── config/
│   ├── settings.py
│   └── prompts.py
│
├── logs/
│
├── notebooks/
│
├── tests/
│
├── requirements.txt
├── .env
├── README.md
└── scaffold.py
```

---

# Design Principles

### Thin FastAPI Layer

`app.py` should never contain business logic.

Its responsibility is only:

- Receive request
- Validate request
- Call agent
- Return response

---

### Agent-Centric Architecture

All reasoning stays inside:

```text
source/agents.py
```

---

### Persistent Knowledge Layer

FAISS index survives application restarts.

---

### Separation of Structured and Unstructured Data

Structured Data:

```text
SQLite Database
```

Unstructured Data:

```text
Policy PDFs + FAISS
```

---

### Frontend Independence

The frontend only knows:

```http
POST /chat
```

meaning it can later be replaced by:

- React
- Vue
- Streamlit
- Mobile App

without changing the backend architecture.