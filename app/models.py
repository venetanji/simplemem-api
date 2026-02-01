"""
Data models for SimpleMem API
Matches SimpleMem data schema for compatibility
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DialogueInput(BaseModel):
    """Input model for a single dialogue/memory"""
    content: str = Field(..., description="The dialogue/memory content to store")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the dialogue")
    location: Optional[str] = Field(None, description="Location where dialogue occurred")
    persons: Optional[List[str]] = Field(None, description="People involved in the dialogue")
    entities: Optional[List[str]] = Field(None, description="Named entities in the dialogue")
    topic: Optional[str] = Field(None, description="Topic or category of the dialogue")


class DialogueBatchInput(BaseModel):
    """Input model for batch dialogue addition"""
    dialogues: List[DialogueInput] = Field(..., description="List of dialogues to add")


class MemoryRecord(BaseModel):
    """Complete memory record matching SimpleMem schema"""
    lossless_restatement: str = Field(..., description="Lossless restatement of the memory")
    keywords: Optional[List[str]] = Field(None, description="Keywords extracted from memory")
    timestamp: Optional[datetime] = Field(None, description="When the memory was created")
    location: Optional[str] = Field(None, description="Location associated with memory")
    persons: Optional[List[str]] = Field(None, description="People mentioned in memory")
    entities: Optional[List[str]] = Field(None, description="Entities mentioned in memory")
    topic: Optional[str] = Field(None, description="Topic of the memory")
    vector: Optional[List[float]] = Field(None, description="Embedding vector")


class QueryInput(BaseModel):
    """Input model for memory queries"""
    query: str = Field(..., description="Query string to search memories")
    limit: Optional[int] = Field(10, description="Maximum number of results to return")
    threshold: Optional[float] = Field(None, description="Similarity threshold for results")


class QueryResponse(BaseModel):
    """Response model for memory queries"""
    results: List[MemoryRecord] = Field(..., description="Matching memories")
    count: int = Field(..., description="Number of results returned")


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
