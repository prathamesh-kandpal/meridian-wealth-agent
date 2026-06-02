import os
import dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import tool

# Ensure environment variables are loaded for embeddings
dotenv.load_dotenv()

# 1. Universal Project Root File Path Management
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 2. Dynamic Targets Matching Your Exact Spacing
PDF_DIR = os.path.join(BASE_DIR, "data", "policy documents")
FAISS_INDEX_DIR = os.path.join(BASE_DIR, "data", "faiss_index")

# 3. Defensive Safety Check
# This prints directly to the console so you can verify the location on boot
print(f"[RAG Init] Scanning directory for PDFs: {PDF_DIR}")

def build_or_load_vector_store() -> FAISS:
    """Builds a local FAISS database from investment policies if missing, or loads existing index."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 1. Load from cache if index already built
    if os.path.exists(FAISS_INDEX_DIR):
        return FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    
    # 2. Verify target directory configuration stability
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
        raise FileNotFoundError(f"'{PDF_DIR}/' folder created. Place policy PDFs inside it and re-run.")
        
    documents = []
    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(PDF_DIR, file))
            documents.extend(loader.load())
            
    if not documents:
        raise ValueError(f"No compliance PDF documents found inside the '{PDF_DIR}' directory.")
        
    # 3. Process, chunk, and embed documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    
    vector_store = FAISS.from_documents(docs, embeddings)
    
    # Save a snapshot copy locally for future application fast-boots
    vector_store.save_local(FAISS_INDEX_DIR)
    
    # Return directly from fast operational system memory cache layout 
    return vector_store

# Initialize Vector DB instance
vector_db = build_or_load_vector_store()
retriever = vector_db.as_retriever(search_kwargs={"k": 4})

@tool
def policy_retriever(query: str) -> str:
    """
    Searches across Meridian Wealth's internal PDF documents including Asset Allocation, 
    Client Suitability Standards, Rebalancing Protocols, and Risk Management Guidelines.
    Input should be specific compliance questions.
    """
    matching_docs = retriever.invoke(query)
    context_blocks = []
    for doc in matching_docs:
        source_name = os.path.basename(doc.metadata.get("source", "Policy Doc"))
        page = doc.metadata.get("page", 0)
        context_blocks.append(f"[{source_name} - Page {page}]:\n{doc.page_content}\n")
        
    return "\n---\n".join(context_blocks)