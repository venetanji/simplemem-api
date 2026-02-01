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
        # Not needed for these tests.
        raise NotImplementedError

    def get_stats(self) -> Dict[str, Any]:
        return {"count": len(self._dialogues), "table_name": "fake", "db_path": ":memory:", "db_type": "fake"}

    def clear(self) -> Dict[str, Any]:
        self._dialogues.clear()
        return {"success": True, "message": "All memories cleared"}

    def is_initialized(self) -> bool:
        return self._initialized


@pytest.fixture()
def client(monkeypatch) -> Tuple[TestClient, FakeStorageAdapter]:
    """FastAPI TestClient with fake storage injected into lifespan."""

    fake = FakeStorageAdapter()

    # app.main imports get_storage_adapter into its module namespace.
    monkeypatch.setattr(main, "get_storage_adapter", lambda: fake)

    with TestClient(main.app) as c:
        yield c, fake
