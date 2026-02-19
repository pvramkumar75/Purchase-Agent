from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import json
import logging
import asyncio

from app.core.config import settings
from app.core.memory import memory_manager
from app.core.llm import llm_engine
from app.agents.procurement_agent import procurement_agent
from app.tools.email_service import email_service
from app.tools.computer_search import computer_tools
from app.watcher.folder_watcher import start_watcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Ensure all workspace directories exist ──────────────────────────
WORKSPACE_DIRS = [
    settings.RFQ_DIR, settings.INBOX_DIR, settings.ORDERS_DIR,
    settings.ARCHIVE_DIR, settings.OUTPUT_DIR, settings.MEMORY_DIR,
]
for d in WORKSPACE_DIRS:
    os.makedirs(d, exist_ok=True)

# ─── App ─────────────────────────────────────────────────────────────
app = FastAPI(title="OmniMind — Universal AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ─────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("Starting folder watcher...")
    asyncio.create_task(start_watcher())

# ─── Health ──────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "online", "agent": "OmniMind", "version": "3.0"}

# ─── Upload ──────────────────────────────────────────────────────────
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and immediately analyze a document."""
    upload_dir = settings.INBOX_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    logger.info(f"File uploaded: {file_path}")
    
    try:
        result = await procurement_agent.process_new_document(file_path)
        return {"status": "success", "file": file.filename, "analysis": result}
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return {"status": "uploaded", "file": file.filename, "analysis": {"summary": f"File saved. Analysis error: {str(e)}"}}

# ─── CHAT — The Versatile Brain ──────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []

SYSTEM_PROMPT = """You are **OmniMind**, a powerful, highly-versatile autonomous AI assistant with full, deep access to the user's computer.

## YOUR IDENTITY
- You are a **proactive operations assistant** designed to make the user's life effortless.
- You perform complex tasks like searching, reading, analyzing, and organizing files across the entire computer.
- You are exceptionally good at procurement, but your intelligence extends to general business, personal organization, and data analysis.
- You think step-by-step, use your tools with precision, and always provide clear, structured results.

## COMPUTER ACCESS
You have direct line-of-sight to the following:
- `/host_d/` → Full D: drive access (main storage)
- `/host_users/` → C:/Users (Desktop, Downloads, Documents)
- `/host_capex/` → \\tplserver\Materials (Production & Network data)
- `/workspace/` → Internal project workspace for processing & memory

## CAPABILITIES
1. **🔍 Full-Disk Search** — Find any file or folder by name, extension, or context.
2. **🧠 Document Intelligence** — Extract, summarize, and analyze data from PDF, Excel, Word, CSV, and even images (OCR).
3. **📁 Autonomous Organization** — Proactively suggest and execute file moves, copies, and folder cleanups (sort by type, project, or date).
4. **📊 Specialized Procurement** — Multi-vendor comparisons, price tracking, and negotiation drafting.
5. **✉️ Communication Hub** — Draft professional emails, follow-ups, and reports.
6. **🔒 Local Memory** — You remember every interaction and every piece of data processed to build a long-term knowledge base.

## RESPONSE FORMAT RULES
- Use **bold** for important values, names, and dates.
- Use **Tables** for comparisons or listing search results.
- End every complex response with a "**✨ Proactive Recommendation**" section (how can you make the user's next step easier?).
- Translate container paths to human-readable ones (e.g., show "D:/Work/Quote.pdf" instead of "/host_d/Work/Quote.pdf").

## GROUNDING & SAFETY
- **Fact-Only**: If a search yields nothing, state: "I couldn't find that file or info on your computer."
- **Confirmation**: Always ask before moving/renaming important files or sending emails.
- **Privacy**: No deletions ever. Only safe file operations.
"""

@app.post("/chat")
async def chat_with_assistant(body: ChatRequest):
    """The main conversational endpoint — versatile like Claude."""
    import time
    start_time = time.time()
    
    user_query = body.query
    history = body.history or []
    
    if not user_query:
        return {"reply": "Please provide a query.", "duration": 0}
    
    lower_q = user_query.lower()
    context_parts = []
    
    # ─── TOOL EXECUTION LAYER ────────────────────────────────────────
    
    # 1. FILE SEARCH
    if any(k in lower_q for k in ["find", "search", "look for", "locate", "where is", "check"]):
        search_terms = _extract_search_terms(lower_q)
        search_root = "/host_d" if any(k in lower_q for k in ["d:", "d drive"]) else "/host_users"
        if "desktop" in lower_q: search_root = "/host_d/OneDrive - Thermopads Pvt Ltd/Desktop"
        
        if search_terms:
            results = computer_tools.search_files(f"*{search_terms}*", search_root)
            if results and (isinstance(results[0], dict) and "path" in results[0]):
                context_parts.append(f"[TOOL: file_search] Found {len(results)} files matching '{search_terms}':\n{json.dumps(results[:10], indent=1)}")
            else:
                context_parts.append(f"[TOOL: file_search] Status: No files found matching '{search_terms}' on the computer.")
    
    # 2. FOLDER LISTING
    if any(k in lower_q for k in ["list", "show folder", "what's in", "contents of", "show me"]):
        path = _extract_path(user_query, history)
        if path:
            listing = computer_tools.list_directory(path)
            context_parts.append(f"[TOOL: list_directory] Contents of {path}:\n{json.dumps(listing, indent=2)}")

    # 3. FOLDER ORGANIZATION (Preview vs Execution)
    if any(k in lower_q for k in ["organize", "sort", "arrange", "clean up", "tidy", "yes", "proceed", "do it"]):
        path = _extract_path(user_query, history)
        if path:
            # Check if this is a confirmation to proceed
            if any(k in lower_q for k in ["yes", "proceed", "do it", "confirm", "ok", "go ahead"]):
                result = computer_tools.organize_folder(path)
                if result.get("status") == "success":
                    context_parts.append(f"[TOOL: organize_execute] Successfully organized {path}.\nMoved: {json.dumps(result.get('organized', {}), indent=2)}")
                else:
                    context_parts.append(f"[TOOL: organize_execute] Failed to organize {path}: {result.get('message')}")
            else:
                # Provide a preview first
                listing = computer_tools.list_directory(path)
                context_parts.append(f"[TOOL: organize_preview] Folder contents to organize in {path}:\n{json.dumps(listing, indent=2)}")
                context_parts.append("[INSTRUCTION: Show the user what you WOULD organize and ask for confirmation ('Yes/No') before executing.]")

    # 4. FILE READING
    if any(k in lower_q for k in ["read", "open", "analyze", "extract", "summarize"]):
        search_terms = _extract_search_terms(lower_q)
        if search_terms:
            found = computer_tools.find_by_name(search_terms)
            if found:
                content = computer_tools.read_file_content(found[0])
                context_parts.append(f"[TOOL: read_file] Read '{found[0]}':\n{content}")
            else:
                context_parts.append(f"[TOOL: read_file] Status: File '{search_terms}' NOT FOUND on computer.")

    # 5. MEMORY SEARCH
    if any(k in lower_q for k in ["history", "previous", "last time", "remember", "past"]):
        try:
            memory_results = memory_manager.search_history(user_query)
            if memory_results and memory_results[0]:
                context_parts.append(f"[TOOL: memory_search] Historical data found:\n{json.dumps(memory_results, indent=2)}")
            else:
                context_parts.append("[TOOL: memory_search] Status: No matching historical records found in memory.")
        except:
            context_parts.append("[TOOL: memory_search] Status: Error searching memory database.")

    # 6. MOVE / COPY FILES
    if any(k in lower_q for k in ["move", "copy", "transfer"]):
        context_parts.append("[INSTRUCTION: The user wants to move/copy files. Ask them to confirm source and destination paths before executing.]")

    # ─── BUILD FINAL PROMPT ──────────────────────────────────────────
    tool_context = "\n\n".join(context_parts) if context_parts else ""
    
    # Keep only the last 6 turns of history for context window safety
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    
    messages.append({"role": "user", "content": f"{user_query}\n\n{tool_context}" if tool_context else user_query})
    
    try:
        response = llm_engine.chat(messages)
        duration = round(time.time() - start_time, 2)
        return {"reply": response, "duration": duration}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"reply": f"I encountered an error: {str(e)}. Please try again.", "duration": 0}

# ─── TOOL: Organize Folder (Confirmed Action) ───────────────────────
@app.post("/organize")
async def organize_folder(path: str):
    """Organize a folder by file type. Requires explicit user action."""
    result = computer_tools.organize_folder(path)
    return result

# ─── TOOL: Move File (Confirmed Action) ─────────────────────────────
@app.post("/move-file")
async def move_file(src: str, dest: str):
    """Move a file. Requires explicit user action."""
    result = computer_tools.move_file(src, dest)
    return result

# ─── Data Endpoints ──────────────────────────────────────────────────
@app.get("/quotes")
async def get_quotes():
    try:
        cursor = memory_manager.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM quotes ORDER BY id DESC")
        desc = cursor.description
        if desc is None:
            return []
        columns = [col[0] for col in desc]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Quotes error: {e}")
        return []

@app.get("/vendors")
async def get_vendors():
    try:
        cursor = memory_manager.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM vendor_performance")
        desc = cursor.description
        if desc is None:
            return []
        columns = [col[0] for col in desc]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except:
        return []

@app.post("/send-email")
async def send_email(to: str, subject: str, body: str):
    return email_service.send_email(to, subject, body)

@app.get("/search")
async def search_memory(q: str):
    try:
        return memory_manager.search_history(q)
    except:
        return []

# ─── Helper Functions ────────────────────────────────────────────────
def _extract_search_terms(query: str) -> str:
    """Extract the most likely search term from a natural language query."""
    # Remove common action words
    stop_words = ["find", "search", "look", "for", "check", "the", "my", "a", "an", "in",
                  "on", "desktop", "downloads", "documents", "folder", "file", "files",
                  "please", "can", "you", "show", "me", "read", "open", "analyze", "extract",
                  "summarize", "where", "is", "are", "locate", "get", "with", "from", "about",
                  "quotes", "quotations", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
                  "2023", "2024", "2025", "2026"]
    words = query.split()
    meaningful = [w for w in words if w.lower() not in stop_words and len(w) > 2]
    return " ".join(meaningful[:3]) if meaningful else ""

def _extract_path(query: str, history: List[Dict[str, str]] = None) -> str:
    """Try to extract a file path from a natural language query or history context."""
    lower = query.lower()
    
    # 1. Direct check in current query
    if "capex25" in lower: return "/host_capex/2025"
    if "desktop" in lower: return "/host_d/OneDrive - Thermopads Pvt Ltd/Desktop"
    if "downloads" in lower or "download" in lower: return "/host_users/Ramkumar/Downloads"
    if "documents" in lower or "document" in lower: return "/host_d/OneDrive - Thermopads Pvt Ltd/Documents"
    if "rfq" in lower: return settings.RFQ_DIR
    if "inbox" in lower: return settings.INBOX_DIR
    if "orders" in lower: return settings.ORDERS_DIR
    if "workspace" in lower: return "/workspace"
    if "d:" in lower or "d drive" in lower: return "/host_d"
    
    # 2. Check history if current query is a short confirmation (Yes/No/Proceed)
    if history and any(k in lower for k in ["yes", "proceed", "do it", "confirm", "ok", "go ahead"]):
        # Search backwards through history for the last mentioned path
        for msg in reversed(history):
            h_lower = msg["content"].lower()
            if "desktop" in h_lower: return "/host_d/OneDrive - Thermopads Pvt Ltd/Desktop"
            if "downloads" in h_lower: return "/host_users/Ramkumar/Downloads"
            if "documents" in h_lower: return "/host_d/OneDrive - Thermopads Pvt Ltd/Documents"
            if "d drive" in h_lower or "d:" in h_lower: return "/host_d"
            
    return "/host_d" # Default to D drive as it's likely the main storage
