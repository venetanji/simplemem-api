"""
Storage abstraction layer for SimpleMem
Provides unified interface for different storage backends (LanceDB, Neo4j)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path

from app.config import settings
from app.models import MemoryRecord, DialogueInput


class StorageAdapter(ABC):
    """Abstract base class for storage adapters"""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage backend"""
        pass
    
    @abstractmethod
    def add_dialogue(self, dialogue: DialogueInput) -> Dict[str, Any]:
        """Add a single dialogue to memory"""
        pass
    
    @abstractmethod
    def add_dialogues(self, dialogues: List[DialogueInput]) -> Dict[str, Any]:
        """Add multiple dialogues to memory"""
        pass
    
    @abstractmethod
    def finalize(self) -> Dict[str, Any]:
        """Finalize memory storage (process pending items)"""
        pass
    
    @abstractmethod
    def query(self, query: str, limit: int = 10, threshold: Optional[float] = None) -> List[MemoryRecord]:
        """Query memories"""
        pass
    
    @abstractmethod
    def retrieve_all(self, limit: Optional[int] = None) -> List[MemoryRecord]:
        """Retrieve all memories"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        pass
    
    @abstractmethod
    def clear(self) -> Dict[str, Any]:
        """Clear all memories"""
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if storage is initialized"""
        pass


class LanceDBAdapter(StorageAdapter):
    """
    LanceDB storage adapter using SimpleMem package
    This is the default local storage implementation
    """
    
    def __init__(self):
        self.simplemem = None
        self._initialized = False
        self.db_path = settings.db_path
        self.table_name = settings.table_name
    
    def initialize(self) -> None:
        """Initialize SimpleMem with LanceDB backend"""
        try:
            # Import simplemem here to avoid issues if not installed
            from simplemem import SimpleMem
            
            # Ensure the database directory exists
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            # Initialize SimpleMem with local LanceDB
            # Note: SimpleMem may require model_name and api_key for embeddings
            init_kwargs = {
                "db_path": self.db_path,
                "table_name": self.table_name,
            }
            
            # Add optional LLM settings if provided
            if settings.model_name:
                init_kwargs["model_name"] = settings.model_name
            if settings.api_key:
                init_kwargs["api_key"] = settings.api_key
            
            self.simplemem = SimpleMem(**init_kwargs)
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize SimpleMem with LanceDB: {str(e)}")
    
    def add_dialogue(self, dialogue: DialogueInput) -> Dict[str, Any]:
        """Add a single dialogue to memory"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Convert DialogueInput to dict for SimpleMem
            dialogue_data = {
                "content": dialogue.content,
                "timestamp": dialogue.timestamp,
                "location": dialogue.location,
                "persons": dialogue.persons,
                "entities": dialogue.entities,
                "topic": dialogue.topic,
            }
            
            # Remove None values
            dialogue_data = {k: v for k, v in dialogue_data.items() if v is not None}
            
            # Add to SimpleMem
            self.simplemem.add(dialogue.content, **dialogue_data)
            
            return {"success": True, "message": "Dialogue added successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to add dialogue: {str(e)}"}
    
    def add_dialogues(self, dialogues: List[DialogueInput]) -> Dict[str, Any]:
        """Add multiple dialogues to memory"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            count = 0
            for dialogue in dialogues:
                result = self.add_dialogue(dialogue)
                if result.get("success"):
                    count += 1
            
            return {
                "success": True,
                "message": f"Added {count} out of {len(dialogues)} dialogues",
                "count": count
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to add dialogues: {str(e)}"}
    
    def finalize(self) -> Dict[str, Any]:
        """Finalize memory storage"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # SimpleMem may have a finalize or commit method
            if hasattr(self.simplemem, 'finalize'):
                self.simplemem.finalize()
            elif hasattr(self.simplemem, 'commit'):
                self.simplemem.commit()
            
            return {"success": True, "message": "Memory storage finalized"}
        except Exception as e:
            return {"success": False, "message": f"Failed to finalize: {str(e)}"}
    
    def query(self, query: str, limit: int = 10, threshold: Optional[float] = None) -> List[MemoryRecord]:
        """Query memories using SimpleMem"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Query SimpleMem
            query_kwargs = {"limit": limit}
            if threshold is not None:
                query_kwargs["threshold"] = threshold
            
            results = self.simplemem.query(query, **query_kwargs)
            
            # Convert results to MemoryRecord models
            memories = []
            for result in results:
                memory = MemoryRecord(
                    lossless_restatement=result.get("lossless_restatement", result.get("content", "")),
                    keywords=result.get("keywords"),
                    timestamp=result.get("timestamp"),
                    location=result.get("location"),
                    persons=result.get("persons"),
                    entities=result.get("entities"),
                    topic=result.get("topic"),
                    vector=result.get("vector"),
                )
                memories.append(memory)
            
            return memories
        except Exception as e:
            raise RuntimeError(f"Failed to query memories: {str(e)}")
    
    def retrieve_all(self, limit: Optional[int] = None) -> List[MemoryRecord]:
        """Retrieve all memories"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Retrieve all memories from SimpleMem
            if hasattr(self.simplemem, 'get_all'):
                results = self.simplemem.get_all(limit=limit) if limit else self.simplemem.get_all()
            elif hasattr(self.simplemem, 'retrieve_all'):
                results = self.simplemem.retrieve_all(limit=limit) if limit else self.simplemem.retrieve_all()
            else:
                # Fallback: query with empty string or use table directly
                results = []
            
            # Convert results to MemoryRecord models
            memories = []
            for result in results:
                memory = MemoryRecord(
                    lossless_restatement=result.get("lossless_restatement", result.get("content", "")),
                    keywords=result.get("keywords"),
                    timestamp=result.get("timestamp"),
                    location=result.get("location"),
                    persons=result.get("persons"),
                    entities=result.get("entities"),
                    topic=result.get("topic"),
                    vector=result.get("vector"),
                )
                memories.append(memory)
            
            return memories
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve memories: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Get count of memories
            count = 0
            if hasattr(self.simplemem, 'count'):
                count = self.simplemem.count()
            elif hasattr(self.simplemem, 'get_count'):
                count = self.simplemem.get_count()
            
            return {
                "count": count,
                "table_name": self.table_name,
                "db_path": self.db_path,
                "db_type": "lancedb"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get stats: {str(e)}")
    
    def clear(self) -> Dict[str, Any]:
        """Clear all memories"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Clear all memories from SimpleMem
            if hasattr(self.simplemem, 'clear'):
                self.simplemem.clear()
            elif hasattr(self.simplemem, 'delete_all'):
                self.simplemem.delete_all()
            else:
                # Fallback: reinitialize
                self.initialize()
            
            return {"success": True, "message": "All memories cleared"}
        except Exception as e:
            return {"success": False, "message": f"Failed to clear memories: {str(e)}"}
    
    def is_initialized(self) -> bool:
        """Check if storage is initialized"""
        return self._initialized


class Neo4jAdapter(StorageAdapter):
    """
    Neo4j storage adapter (placeholder for future implementation)
    This will be used for remote/cloud deployments
    """
    
    def __init__(self):
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize Neo4j connection"""
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def add_dialogue(self, dialogue: DialogueInput) -> Dict[str, Any]:
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def add_dialogues(self, dialogues: List[DialogueInput]) -> Dict[str, Any]:
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def finalize(self) -> Dict[str, Any]:
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def query(self, query: str, limit: int = 10, threshold: Optional[float] = None) -> List[MemoryRecord]:
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def retrieve_all(self, limit: Optional[int] = None) -> List[MemoryRecord]:
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def get_stats(self) -> Dict[str, Any]:
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def clear(self) -> Dict[str, Any]:
        raise NotImplementedError("Neo4j adapter not yet implemented")
    
    def is_initialized(self) -> bool:
        return self._initialized


def get_storage_adapter() -> StorageAdapter:
    """
    Factory function to get the appropriate storage adapter based on configuration
    """
    db_type = settings.db_type.lower()
    
    if db_type == "lancedb":
        return LanceDBAdapter()
    elif db_type == "neo4j":
        return Neo4jAdapter()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
