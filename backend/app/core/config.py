from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str
    WORKSPACE_ROOT: str = "/workspace"
    DB_PATH: str = "/workspace/memory/procurement.db"
    CHROMA_PATH: str = "/workspace/memory/chroma"
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    
    @property
    def INBOX_DIR(self): return os.path.join(self.WORKSPACE_ROOT, "inbox")
    @property
    def RFQ_DIR(self): return os.path.join(self.WORKSPACE_ROOT, "rfq")
    @property
    def ORDERS_DIR(self): return os.path.join(self.WORKSPACE_ROOT, "orders")
    @property
    def ARCHIVE_DIR(self): return os.path.join(self.WORKSPACE_ROOT, "archive")
    @property
    def OUTPUT_DIR(self): return os.path.join(self.WORKSPACE_ROOT, "output")
    @property
    def MEMORY_DIR(self): return os.path.join(self.WORKSPACE_ROOT, "memory")

    class Config:
        env_file = ".env"

settings = Settings()
