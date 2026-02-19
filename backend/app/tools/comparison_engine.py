from typing import List, Dict, Any
from app.core.llm import llm_engine
import pandas as pd

class ComparisonEngine:
    @staticmethod
    def compare_quotations(quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes a list of structured quote data and produces a comparison table and recommendation.
        """
        if not quotes:
            return {"error": "No quotes provided for comparison"}
        
        # Convert to DataFrame for tabular representation
        df = pd.DataFrame(quotes)
        
        # Use LLM for qualitative analysis and recommendation
        prompt = f"""
        Compare these vendor quotations for procurement. 
        Highlight:
        1. Best price (normalized)
        2. Delivery time differences
        3. Payment term risks
        4. Technical deviations / missing info
        
        Data:
        {df.to_json(orient='records')}
        
        Return a structured comparison summary with a 'recommendation'.
        """
        
        analysis = llm_engine.chat([{"role": "user", "content": prompt}])
        
        return {
            "table": df.to_dict(orient='records'),
            "analysis": analysis,
            "best_bid": df.loc[df['total'].idxmin()].get('vendor_name') if 'total' in df.columns else "Unknown"
        }

    @staticmethod
    def detect_revisions(old_quote: Dict[str, Any], new_quote: Dict[str, Any]) -> str:
        prompt = f"""
        Compare these two versions of a quotation from {old_quote.get('vendor_name')}.
        Identify ONLY what has changed (price, delivery, terms).
        
        Old: {old_quote}
        New: {new_quote}
        """
        return llm_engine.chat([{"role": "user", "content": prompt}])

comparison_engine = ComparisonEngine()
