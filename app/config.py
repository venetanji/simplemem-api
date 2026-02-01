"""
Configuration management for SimpleMem API
Uses environment variables with sensible defaults for local development
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application settings
    app_name: str = "SimpleMem API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # SimpleMem / Storage settings
    db_path: str = "./simplemem_data"
    db_type: str = "lancedb"  # Currently only lancedb, future: neo4j
    table_name: str = "memories"
    
    # LLM settings for SimpleMem
    model_name: Optional[str] = None  # e.g., "gpt-4" or "claude-3-opus-20240229"
    api_key: Optional[str] = None
    
    # Neo4j settings (placeholder for future)
    neo4j_uri: Optional[str] = None
    neo4j_user: Optional[str] = None
    neo4j_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
