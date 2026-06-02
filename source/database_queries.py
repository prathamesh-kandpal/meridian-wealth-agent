import sqlite3
import json
import os
from typing import Dict, Any, List
from langchain_core.tools import tool

# UNIVERSAL PATH MANAGEMENT: Targets your exact database file safely
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "meridian_wealth.db"))

def execute_read_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Helper function to execute secure read-only SQL operations against SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        # This will return the error string safely to the agent instead of throwing an API 500
        return [{"error": f"Database execution failed: {str(e)}"}]
    finally:
        conn.close()

@tool
def portfolio_lookup(query: Any) -> str:
    """
    Queries the Meridian Wealth internal database to fetch client records, holdings, and risk profiles.
    Input can be a numerical index index (e.g. 1, 2), a database ID (e.g. 'CLT-001'), 
    a client name string (e.g. 'Rajesh Mehta'), or words like 'top' / 'highest'.
    """
    clean_query = str(query).strip().lower()
    
    # --- WORKFLOW 1: Handle high-level "Top Clients" Queries ---
    if "top" in clean_query or "highest" in clean_query or "best" in clean_query or "investors" in clean_query:
        sql_query = """
            SELECT client_id, name, risk_profile, relationship_mgr, aum_inr
            FROM clients
            ORDER BY aum_inr DESC
            LIMIT 3
        """
        results = execute_read_query(sql_query)
        return json.dumps(results, indent=2, default=str)

    # --- WORKFLOW 2: Handle Specific Client Lookups ---
    # Map raw UI integers to database codes safely (e.g., 1 -> "CLT-001")
    if clean_query.isdigit():
        target_id = f"CLT-{int(clean_query):03d}"
    elif clean_query.startswith("clt-"):
        target_id = clean_query.upper()
    else:
        target_id = None

    if target_id:
        # Step A: Pull Client Demographics (Columns: client_id, name, risk_profile, aum_inr, etc.)
        client_sql = "SELECT client_id, name, risk_profile, relationship_mgr, aum_inr, investment_horizon FROM clients WHERE client_id = ?"
        client_data = execute_read_query(client_sql, (target_id,))
        
        # Step B: Pull Client Investment Positions using EXACT verified binary columns
        holdings_sql = "SELECT id, client_id, ticker, company_name, shares, avg_cost_basis, current_price, sector, purchase_date FROM holdings WHERE client_id = ?"
        holdings_data = execute_read_query(holdings_sql, (target_id,))
        
        if not client_data:
            return json.dumps({"message": f"No client matching ID '{target_id}' found."})
            
        output = {
            "client_profile": client_data[0],
            "holdings": holdings_data
        }
        return json.dumps(output, indent=2, default=str)
        
    # --- WORKFLOW 3: Fallback Name Search Text Matching ---
    else:
        client_sql = "SELECT client_id, name, risk_profile, relationship_mgr, aum_inr, investment_horizon FROM clients WHERE LOWER(name) LIKE ?"
        client_data = execute_read_query(client_sql, (f"%{clean_query}%",))
        
        if client_data:
            found_id = client_data[0]["client_id"]
            holdings_sql = "SELECT id, client_id, ticker, company_name, shares, avg_cost_basis, current_price, sector, purchase_date FROM holdings WHERE client_id = ?"
            holdings_data = execute_read_query(holdings_sql, (found_id,))
            
            output = {
                "client_profile": client_data[0],
                "holdings": holdings_data
            }
            return json.dumps(output, indent=2, default=str)

    return json.dumps({"message": f"No records matching query criteria '{query}' located."})

@tool
def calculate_metrics(portfolio_json: str) -> str:
    """
    Performs mathematical aggregation operations on portfolio holdings structure payloads.
    Input must be a valid JSON string configuration.
    """
    try:
        data = json.loads(portfolio_json)
        # Pull list if nested under portfolio payload
        holdings = data.get("holdings", []) if isinstance(data, dict) else data
        if not isinstance(holdings, list):
            holdings = []
            
        total_value = 0.0
        sector_allocations: Dict[str, float] = {}
        
        for item in holdings:
            # Match strict schema: compute market value = shares * current_price
            shares = float(item.get("shares", 0))
            price = float(item.get("current_price", 0))
            val = shares * price
            total_value += val
            
            sector = item.get("sector", "Other")
            sector_allocations[sector] = sector_allocations.get(sector, 0.0) + val

        metrics = {
            "calculated_holdings_market_value": round(total_value, 2),
            "sector_concentration_percentage": {
                k: round((v / total_value) * 100, 2) if total_value > 0 else 0 
                for k, v in sector_allocations.items()
            }
        }
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to calculate metrics: {str(e)}"})