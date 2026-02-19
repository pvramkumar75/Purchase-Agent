import time
import logging
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.core.config import settings
from app.agents.procurement_agent import procurement_agent

class ProcurementFolderHandler(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            # Run the async agent process in the main loop
            asyncio.run_coroutine_threadsafe(
                procurement_agent.process_new_document(event.src_path), 
                self.loop
            )

async def start_watcher():
    loop = asyncio.get_running_loop()
    event_handler = ProcurementFolderHandler(loop)
    observer = Observer()
    
    # Watch RFQ and Inbox specifically
    import os
    os.makedirs(settings.RFQ_DIR, exist_ok=True)
    os.makedirs(settings.INBOX_DIR, exist_ok=True)
    
    observer.schedule(event_handler, settings.RFQ_DIR, recursive=False)
    observer.schedule(event_handler, settings.INBOX_DIR, recursive=False)
    
    observer.start()
    print(f"Watcher started on {settings.RFQ_DIR} and {settings.INBOX_DIR}")
    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        observer.stop()
    observer.join()
