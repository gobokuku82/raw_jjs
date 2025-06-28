"""
Configuration management for Legal AI Assistant
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str = Field("demo_key", env="OPENAI_API_KEY")
    
    # HyperClova-X Configuration
    clova_api_key: Optional[str] = Field(None, env="CLOVA_API_KEY")
    clova_apigw_api_key: Optional[str] = Field(None, env="CLOVA_APIGW_API_KEY")
    
    # Database Configuration (SQLite for MVP)
    database_url: str = Field("sqlite:///./data/legal_ai.db", env="DATABASE_URL")
    
    # Vector Database
    chroma_persist_directory: str = Field("./data/chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    
    # Model Configuration
    embedding_model: str = Field("nlpai-lab/KURE-v1", env="EMBEDDING_MODEL")
    reranker_model: str = Field("BAAI/bge-reranker-v2-m3", env="RERANKER_MODEL")
    
    # Application Settings
    app_title: str = Field("Legal AI Assistant", env="APP_TITLE")
    debug: bool = Field(True, env="DEBUG")
    

    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 