import os
from dotenv import load_dotenv

# Use the modern LangGraph wrapper layout explicitly called out in your lab materials
from langgraph.prebuilt import create_react_agent 
from langchain_openai import ChatOpenAI

# Updated modern Tavily tool import path
from langchain_community.tools.tavily_search import TavilySearchResults

# Custom module imports matching your project tree layout
from source.database_queries import portfolio_lookup, calculate_metrics
from source.rag_pipeline import policy_retriever

# Load environment variables (.env)
load_dotenv()

# 1. Core LLM Orchestrator
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Consolidate Tools Array
tools = [portfolio_lookup, calculate_metrics, policy_retriever]

# Add live web search if your Tavily API key is registered 
if os.getenv("TAVILY_API_KEY"):
    # Updated tool class call to match your environment package
    web_search = TavilySearchResults(max_results=3)
    tools.append(web_search)

# 3. System Instruction Prompt Guide
system_modifier = (
    "You are a helpful financial analyst agent for Meridian Wealth Partners. "
    "You have access to internal client portfolios, metrics calculators, compliance guidelines, and live web search. "
    "Always utilize the proper database tools or policy retrievers when addressing financial information. "
    "Be structured, factual, and explicit in your responses."
)

# 4. Instantiate the Agent Executor
# Changed to 'prompt' to ensure seamless backwards-compatibility with your package version
financial_agent_executor = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_modifier
)