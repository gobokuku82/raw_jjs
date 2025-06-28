"""
Simple configuration management for Streamlit MVP
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class SimpleSettings:
    """Simple settings class without Pydantic"""
    
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "demo_key")
        
        # HyperClova-X Configuration (Optional)
        self.clova_api_key = os.getenv("CLOVA_API_KEY")
        self.clova_apigw_api_key = os.getenv("CLOVA_APIGW_API_KEY")
        
        # Database Configuration (SQLite for MVP)
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./data/legal_ai.db")
        
        # Vector Database
        self.chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
        
        # Model Configuration
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nlpai-lab/KURE-v1")
        self.reranker_model = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
        
        # Application Settings
        self.app_title = os.getenv("APP_TITLE", "Legal AI Assistant")
        self.debug = os.getenv("DEBUG", "True").lower() == "true"


# Global settings instance
settings = SimpleSettings() 