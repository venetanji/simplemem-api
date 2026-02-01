"""
Data models for SimpleMem API
Matches SimpleMem data schema for compatibility
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DialogueInput(BaseModel):
    """Input model for a single dialogue/memory"""
    speaker: str = Field(..., description="Speaker/author of the dialogue")
    content: str = Field(..., description="The dialogue/memory content to store")
    timestamp: Optional[str] = Field(None, description="Timestamp of the dialogue (ISO format)")


class DialogueBatchInput(BaseModel):
    """Input model for batch dialogue addition"""
    dialogues: List[DialogueInput] = Field(..., description="List of dialogues to add")


class MemoryRecord(BaseModel):
    """Complete memory record matching SimpleMem MemoryEntry schema"""
    entry_id: Optional[str] = Field(None, description="Unique entry identifier")
    lossless_restatement: str = Field(..., description="Lossless restatement of the memory")
    keywords: Optional[List[str]] = Field(None, description="Keywords extracted from memory")
    timestamp: Optional[str] = Field(None, description="When the memory was created")
    location: Optional[str] = Field(None, description="Location associated with memory")
    persons: Optional[List[str]] = Field(None, description="People mentioned in memory")
    entities: Optional[List[str]] = Field(None, description="Entities mentioned in memory")
    topic: Optional[str] = Field(None, description="Topic of the memory")


class QueryInput(BaseModel):
    """Input model for memory queries"""
    query: str = Field(..., description="Query string to search memories")


class QueryResponse(BaseModel):
    """Response model for memory queries"""
    answer: str = Field(..., description="Answer from SimpleMem")


class StatsResponse(BaseModel):
    """Response model for memory statistics"""
    count: int = Field(..., description="Total number of memories")
    table_name: str = Field(..., description="Name of the memory table")
    db_path: str = Field(..., description="Path to the database")
    db_type: str = Field(..., description="Type of database (lancedb, neo4j, etc.)")


class ClearRequest(BaseModel):
    """Request model for clearing memories"""
    confirmation: bool = Field(..., description="Must be true to confirm clearing all memories")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    simplemem_initialized: bool = Field(..., description="Whether SimpleMem is initialized")


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(..., description="Response message")
    success: bool = Field(True, description="Whether operation was successful")
