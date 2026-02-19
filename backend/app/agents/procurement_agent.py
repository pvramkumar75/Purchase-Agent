from app.tools.file_processor import file_processor
from app.core.llm import llm_engine
from app.core.memory import memory_manager
from app.tools.comparison_engine import comparison_engine
import os
import json
import logging

logger = logging.getLogger(__name__)

class ProcurementAgent:
    """Autonomous procurement agent that processes documents, extracts data, and provides actionable insights."""

    QUOTE_SCHEMA = json.dumps({
        "vendor_name": "string",
        "material": "string or null",
        "qty": "number or null",
        "unit_price": "number or null",
        "total": "number or null",
        "currency": "string (e.g. USD, EUR, INR)",
        "delivery_weeks": "number or null",
        "payment_terms": "string or null",
        "date": "string (YYYY-MM-DD) or null",
        "deviations": "string or null",
        "validity": "string or null"
    }, indent=2)

    async def process_new_document(self, file_path: str) -> dict:
        logger.info(f"Processing document: {file_path}")
        
        # 1. Read raw content
        try:
            raw_content = file_processor.read_file(file_path)
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return {"type": "Error", "summary": f"Could not read file: {str(e)}"}
        
        if not raw_content or len(raw_content.strip()) < 10:
            return {"type": "Error", "summary": "File appears to be empty or unreadable."}
        
        # 2. Detect document type
        doc_type = file_processor.detect_document_type(raw_content)
        logger.info(f"Detected type: {doc_type} for {os.path.basename(file_path)}")
        
        # 3. Process based on type
        if doc_type == "Quotation":
            return await self._process_quotation(file_path, raw_content)
        elif doc_type == "Purchase Order":
            return await self._process_po(file_path, raw_content)
        elif doc_type == "Invoice":
            return await self._process_invoice(file_path, raw_content)
        else:
            return await self._process_general(file_path, raw_content, doc_type)

    async def _process_quotation(self, file_path: str, raw_content: str) -> dict:
        """Full pipeline for quotation processing."""
        # Extract structured data
        structured = llm_engine.extract_structured_data(raw_content, self.QUOTE_SCHEMA)
        
        if "error" in structured:
            return {"type": "Quotation", "summary": f"Extraction issue: {structured.get('error')}", "data": {}}
        
        structured['file_path'] = file_path
        
        # Check memory for vendor history
        vendor = structured.get('vendor_name', 'Unknown')
        material = structured.get('material', 'Unknown')
        
        history = []
        try:
            history = memory_manager.search_history(f"quotes from {vendor} for {material}")
        except:
            pass
        
        # Store in memory
        try:
            memory_manager.store_quote(structured)
        except Exception as e:
            logger.error(f"Memory store error: {e}")
        
        # Generate intelligent summary
        summary_prompt = f"""Summarize this procurement quotation in 3-4 bullet points:

**Vendor:** {vendor}
**Material:** {material}
**Total:** {structured.get('currency', '')} {structured.get('total', 'N/A')}
**Delivery:** {structured.get('delivery_weeks', 'N/A')} weeks
**Payment Terms:** {structured.get('payment_terms', 'N/A')}
**Validity:** {structured.get('validity', 'N/A')}

Historical context: {json.dumps(history[:2]) if history else 'No prior quotes on record.'}

End with a recommendation (accept / negotiate / compare with alternatives).
"""
        summary = llm_engine.chat([{"role": "user", "content": summary_prompt}])
        
        return {
            "type": "Quotation",
            "data": structured,
            "summary": summary,
            "needs_approval": False
        }

    async def _process_po(self, file_path: str, raw_content: str) -> dict:
        summary = llm_engine.chat([
            {"role": "user", "content": f"Summarize this Purchase Order in clean bullet points. Highlight: PO number, vendor, items ordered, total value, delivery date.\n\n{raw_content[:3000]}"}
        ])
        return {"type": "Purchase Order", "summary": summary, "data": {}}

    async def _process_invoice(self, file_path: str, raw_content: str) -> dict:
        summary = llm_engine.chat([
            {"role": "user", "content": f"Summarize this Invoice. Highlight: invoice number, vendor, amount, due date, payment status.\n\n{raw_content[:3000]}"}
        ])
        return {"type": "Invoice", "summary": summary, "data": {}}

    async def _process_general(self, file_path: str, raw_content: str, doc_type: str) -> dict:
        summary = llm_engine.chat([
            {"role": "user", "content": f"This is a '{doc_type}' document. Provide a concise summary of its contents:\n\n{raw_content[:3000]}"}
        ])
        return {"type": doc_type, "summary": summary, "data": {}}

procurement_agent = ProcurementAgent()
