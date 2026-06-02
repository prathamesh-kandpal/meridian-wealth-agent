from pathlib import Path

PROJECT_STRUCTURE = {
    "app.py": """
# FastAPI Application Entry Point

# Responsibilities:
# - Initialize FastAPI
# - Mount static files
# - Configure templates
# - Register API routes
# - Connect agent workflow

""",

    ".env": """
# Environment Variables

# OPENAI_API_KEY=
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
""",

    ".gitignore": """
__pycache__/
*.pyc
.env
.vscode/
.idea/
logs/*.log
""",

    "requirements.txt": """
# Add project dependencies here
""",

    "README.md": """
# Financial Analyst Agent

Project documentation.
""",

    "source/__init__.py": "",

    "source/agents.py": """
# Agent Definitions

# Responsibilities:
# - LangGraph workflow
# - Agent routing
# - Tool definitions
# - State management
# - Financial analyst logic
""",

    "source/schemas.py": """
# Pydantic Schemas

# Responsibilities:
# - Request schemas
# - Response schemas
# - Agent state schemas
""",

    "source/rag_pipeline.py": """
# RAG Pipeline

# Responsibilities:
# - PDF ingestion
# - Chunking
# - Embedding generation
# - Retrieval logic
# - FAISS integration
""",

    "source/database_queries.py": """
# Database Layer

# Responsibilities:
# - SQLite connections
# - SQL queries
# - CRUD operations
# - Analytics queries
""",

    "vector_store/build_index.py": """
# One-Time FAISS Index Builder

# Responsibilities:
# - Read policy PDFs
# - Create embeddings
# - Build FAISS index
# - Persist index to disk

# Should only run when:
# - New PDFs are added
# - Re-indexing is required
""",

    "vector_store/faiss_index/.gitkeep": "",

    "data/meridian_wealth.db": "",

    "data/policy_documents/.gitkeep": "",

    "frontend/templates/index.html": """
<!-- Landing Page -->
""",

    "frontend/templates/chat.html": """
<!-- Chat Interface -->

<!--
Display:
- User messages
- Agent responses
- Node execution steps
-->
""",

    "frontend/templates/login.html": """
<!-- Login Page -->
""",

    "frontend/templates/dashboard.html": """
<!-- Dashboard Page -->
""",

    "frontend/templates/error.html": """
<!-- Error Page -->
""",

    "frontend/static/css/style.css": """
/* Global Styles */
""",

    "frontend/static/css/chat.css": """
/* Chat Page Styles */
""",

    "frontend/static/css/dashboard.css": """
/* Dashboard Styles */
""",

    "frontend/static/js/chat.js": """
// Chat Logic

// Responsibilities:
// - Send messages to backend
// - Display responses
// - Render execution steps
""",

    "frontend/static/js/api.js": """
// API Helper Functions
""",

    "frontend/static/js/dashboard.js": """
// Dashboard Logic
""",

    "logs/app.log": "",

    "logs/agent.log": "",

    "config/settings.py": """
# Application Settings

# Store:
# - Paths
# - Model Names
# - Environment Configurations
# - Database Locations
# - FAISS Locations
""",

    "config/prompts.py": """
# Central Prompt Repository

# Store:
# - System prompts
# - Agent prompts
# - RAG prompts
""",

    "tests/test_agent.py": """
# Agent Tests
""",

    "tests/test_rag.py": """
# RAG Tests
""",

    "tests/test_api.py": """
# API Tests
""",

    "notebooks/.gitkeep": "",
}


def create_structure():
    root = Path.cwd()

    for relative_path, content in PROJECT_STRUCTURE.items():

        full_path = root / relative_path

        full_path.parent.mkdir(parents=True, exist_ok=True)

        if not full_path.exists():
            full_path.write_text(content.strip() + "\n", encoding="utf-8")
            print(f"Created: {relative_path}")
        else:
            print(f"Skipped (already exists): {relative_path}")

    print("\nProject scaffold created successfully.")


if __name__ == "__main__":
    create_structure()