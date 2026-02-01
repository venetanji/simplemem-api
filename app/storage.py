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
    def query(self, query: str, limit: int = 10, threshold: Optional[float] = None) -> str:
        """Query memories and get an answer"""
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
            from simplemem import SimpleMemSystem
            
            # Ensure the database directory exists
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            # Initialize SimpleMemSystem with local LanceDB
            # Note: SimpleMem requires api_key and model for LLM operations
            init_kwargs = {
                "db_path": self.db_path,
                "table_name": self.table_name,
            }
            
            # Add optional LLM settings if provided
            if settings.model_name:
                init_kwargs["model"] = settings.model_name
            if settings.api_key:
                init_kwargs["api_key"] = settings.api_key
            
            self.simplemem = SimpleMemSystem(**init_kwargs)
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize SimpleMem with LanceDB: {str(e)}")
    
    def add_dialogue(self, dialogue: DialogueInput) -> Dict[str, Any]:
        """Add a single dialogue to memory"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Add dialogue using SimpleMem's add_dialogue method
            self.simplemem.add_dialogue(
                speaker=dialogue.speaker,
                content=dialogue.content,
                timestamp=dialogue.timestamp
            )
            
            return {"success": True, "message": "Dialogue added successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to add dialogue: {str(e)}"}
    
    def add_dialogues(self, dialogues: List[DialogueInput]) -> Dict[str, Any]:
        """Add multiple dialogues to memory"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Import Dialogue model from simplemem
            from simplemem import Dialogue
            import time
            
            # Convert DialogueInput list to Dialogue list
            # Use timestamp-based IDs to ensure uniqueness across calls
            base_id = int(time.time() * 1000000)  # microseconds since epoch
            simplemem_dialogues = []
            for idx, dialogue in enumerate(dialogues):
                simplemem_dialogue = Dialogue(
                    dialogue_id=base_id + idx,
                    speaker=dialogue.speaker,
                    content=dialogue.content,
                    timestamp=dialogue.timestamp
                )
                simplemem_dialogues.append(simplemem_dialogue)
            
            # Add dialogues using SimpleMem's add_dialogues method
            self.simplemem.add_dialogues(simplemem_dialogues)
            
            return {
                "success": True,
                "message": f"Added {len(dialogues)} dialogues",
                "count": len(dialogues)
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
    
    def query(self, query: str, limit: int = 10, threshold: Optional[float] = None) -> str:
        """Query memories using SimpleMem's ask method"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Use SimpleMem's ask method which returns a string answer
            answer = self.simplemem.ask(query)
            return answer
        except Exception as e:
            raise RuntimeError(f"Failed to query memories: {str(e)}")
    
    def retrieve_all(self, limit: Optional[int] = None) -> List[MemoryRecord]:
        """Retrieve all memories"""
        if not self._initialized:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        
        try:
            # Use SimpleMem's get_all_memories method
            memory_entries = self.simplemem.get_all_memories()
            
            # Convert MemoryEntry objects to MemoryRecord models
            memories = []
            for entry in memory_entries:
                if limit and len(memories) >= limit:
                    break
                    
                memory = MemoryRecord(
                    entry_id=entry.entry_id if hasattr(entry, 'entry_id') else None,
                    lossless_restatement=entry.lossless_restatement,
                    keywords=entry.keywords if hasattr(entry, 'keywords') and entry.keywords else None,
                    timestamp=entry.timestamp if hasattr(entry, 'timestamp') else None,
                    location=entry.location if hasattr(entry, 'location') else None,
                    persons=entry.persons if hasattr(entry, 'persons') and entry.persons else None,
                    entities=entry.entities if hasattr(entry, 'entities') and entry.entities else None,
                    topic=entry.topic if hasattr(entry, 'topic') else None,
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
            memories = self.simplemem.get_all_memories()
            count = len(memories)
            
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
            # SimpleMem doesn't have a clear method, so we need to reinitialize with clear_db=True
            from simplemem import SimpleMemSystem
            
            # Reinitialize with clear_db flag
            init_kwargs = {
                "db_path": self.db_path,
                "table_name": self.table_name,
                "clear_db": True,
            }
            
            if settings.model_name:
                init_kwargs["model"] = settings.model_name
            if settings.api_key:
                init_kwargs["api_key"] = settings.api_key
            
            self.simplemem = SimpleMemSystem(**init_kwargs)
            
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
    
    def query(self, query: str, limit: int = 10, threshold: Optional[float] = None) -> str:
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
