from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pytest
from fastapi.testclient import TestClient

import app.main as main


@dataclass
class _Dialogue:
    speaker: str
    content: str
    timestamp: str


class FakeStorageAdapter:
    """In-memory storage adapter for API tests.

    Avoids importing/initializing SimpleMem, embedding models, or external services.
    """

    def __init__(self) -> None:
        self._initialized = False
        self._dialogues: List[_Dialogue] = []

    def initialize(self) -> None:
        self._initialized = True

    def add_dialogue(self, dialogue: Any) -> Dict[str, Any]:
        self._dialogues.append(
            _Dialogue(
                speaker=dialogue.speaker,
                content=dialogue.content,
                timestamp=dialogue.timestamp
                or datetime.utcnow().isoformat() + "Z",
            )
        )
        return {"success": True, "message": "Dialogue added successfully"}

    def add_dialogues(self, dialogues: List[Any]) -> Dict[str, Any]:
        for d in dialogues:
            self.add_dialogue(d)
        return {"success": True, "message": f"Added {len(dialogues)} dialogues", "count": len(dialogues)}

    def finalize(self) -> Dict[str, Any]:
        return {"success": True, "message": "Memory storage finalized"}

    def query(self, query: str, limit: int = 10, threshold: Optional[float] = None) -> str:
        # Simple, deterministic behavior for tests: return any matching dialogues.
        matches = [d for d in self._dialogues if query.lower() in d.content.lower() or query.lower() in d.speaker.lower()]
        matches = matches[:limit]
        if not matches:
            return "No matching memories found"
        joined = " | ".join(f"{d.speaker}: {d.content}" for d in matches)
        return f"Matches: {joined}"

    def retrieve_all(self, limit: Optional[int] = None):
        """Retrieve all stored memories as MemoryRecord objects."""
        from app.models import MemoryRecord
        
        memories = []
        dialogues_to_convert = self._dialogues if limit is None else self._dialogues[:limit]
        
        for i, d in enumerate(dialogues_to_convert):
            memory = MemoryRecord(
                entry_id=str(i),
                lossless_restatement=d.content,
                keywords=None,
                timestamp=d.timestamp,
                location=None,
                persons=[d.speaker],
                entities=None,
                topic=None,
            )
            memories.append(memory)
        
        return memories

    def get_stats(self) -> Dict[str, Any]:
        return {"count": len(self._dialogues), "table_name": "fake", "db_path": ":memory:", "db_type": "fake"}

    def clear(self) -> Dict[str, Any]:
        self._dialogues.clear()
        return {"success": True, "message": "All memories cleared"}

    def is_initialized(self) -> bool:
        return self._initialized

    def delete_memory(self, entry_id: str) -> Dict[str, Any]:
        """Delete a specific memory by entry_id."""
        # Find and remove the dialogue with matching entry_id
        # Since our fake storage uses a simple list, we'll need to track entry_ids
        # For simplicity, we'll search by content match or implement basic entry_id tracking
        try:
            # Try to find by content or speaker matching the entry_id
            # For better testing, let's just remove the first one if entry_id matches its index
            # Find the index first, then remove to avoid modifying list during iteration
            index_to_remove = None
            for i, d in enumerate(self._dialogues):
                # Simple mock: use content hash or index as entry_id
                if str(i) == entry_id or d.content == entry_id:
                    index_to_remove = i
                    break
            
            if index_to_remove is not None:
                self._dialogues.pop(index_to_remove)
                return {"success": True, "message": f"Memory with entry_id '{entry_id}' deleted successfully"}
            else:
                return {"success": False, "message": f"Memory with entry_id '{entry_id}' not found"}
        except Exception as e:
            return {"success": False, "message": f"Failed to delete memory: {str(e)}"}
    
    def semantic_search(self, query: str, top_k: int = 10):
        """Perform semantic search (mock implementation using keyword matching)."""
        from app.models import MemoryRecord
        
        # Simple keyword-based matching for testing
        matches = []
        for i, d in enumerate(self._dialogues):
            if query.lower() in d.content.lower() or query.lower() in d.speaker.lower():
                # Convert dialogue to MemoryRecord format
                memory = MemoryRecord(
                    entry_id=str(i),
                    lossless_restatement=d.content,
                    keywords=None,
                    timestamp=d.timestamp,
                    location=None,
                    persons=[d.speaker],
                    entities=None,
                    topic=None,
                )
                matches.append(memory)
                if len(matches) >= top_k:
                    break
        
        return matches

@pytest.fixture()
def client(monkeypatch) -> Tuple[TestClient, FakeStorageAdapter]:
    """FastAPI TestClient with fake storage injected into lifespan."""

    fake = FakeStorageAdapter()

    # app.main imports get_storage_adapter into its module namespace.
    monkeypatch.setattr(main, "get_storage_adapter", lambda: fake)

    with TestClient(main.app) as c:
        yield c, fake
