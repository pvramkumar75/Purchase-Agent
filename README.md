# ProcureAI — Autonomous Procurement Assistant

A **Claude-like** AI assistant for procurement operations. Powered by DeepSeek, running fully local with full disk access to your computer.

## 🚀 Quick Start

```bash
# 1. Clone and configure
cp .env.example .env   # Add your DEEPSEEK_API_KEY

# 2. Build and run
docker-compose up --build

# 3. Open the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## 🧠 Capabilities

| Feature | Description |
|---------|-------------|
| **Chat** | Natural language queries with Markdown-formatted responses |
| **File Search** | Find files anywhere on D: drive or user folders |
| **Document Analysis** | Extract data from PDF, Excel, Word, CSV, images (OCR) |
| **Folder Organization** | Sort files by type, move/copy/rename with AI commands |
| **Quote Comparison** | Multi-vendor tables with price/delivery analysis |
| **Email Drafting** | Negotiation and follow-up emails (requires approval) |
| **Persistent Memory** | SQLite + ChromaDB for vendor history and price trends |

## 📁 Project Structure

```
Purchase Agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI endpoints (chat, upload, organize)
│   │   ├── core/
│   │   │   ├── config.py        # Settings & environment variables
│   │   │   ├── llm.py           # DeepSeek API wrapper (chat + reasoner)
│   │   │   └── memory.py        # SQLite + ChromaDB memory engine
│   │   ├── agents/
│   │   │   └── procurement_agent.py  # Document processing pipeline
│   │   ├── tools/
│   │   │   ├── computer_search.py    # Full disk search & organization
│   │   │   ├── file_processor.py     # PDF/Excel/Word/Image reader
│   │   │   ├── comparison_engine.py  # Vendor quote comparison
│   │   │   ├── email_service.py      # Gmail SMTP integration
│   │   │   └── ocr.py               # Tesseract OCR
│   │   └── watcher/
│   │       └── folder_watcher.py     # Auto-process new files
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Chat UI with Markdown rendering
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Tailwind + Inter font
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env
└── workspace/                   # Auto-created workspace folders
    ├── inbox/
    ├── rfq/
    ├── orders/
    ├── archive/
    ├── output/
    └── memory/
```

## 🔒 Security

- **Local-first**: All processing runs on your machine. Only DeepSeek API calls go external.
- **No deletions**: The AI can only move/copy files, never delete.
- **Human-in-the-loop**: Emails require explicit approval before sending.
- **Drive access**: D: and C:/Users are mounted read-write inside the container.

## 🛠 Tech Stack

- **Backend**: FastAPI, Python 3.11, DeepSeek API
- **Frontend**: React 18, Vite, Tailwind CSS, Framer Motion
- **Memory**: SQLite (structured) + ChromaDB (vector/semantic)
- **OCR**: Tesseract via pytesseract
- **Containerization**: Docker Compose
