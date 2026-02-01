from __future__ import annotations


def test_delete_memory_success(client):
    """Test deleting a memory that exists."""
    c, fake = client
    
    # Add a dialogue first
    r = c.post(
        "/dialogue",
        json={
            "speaker": "Alice",
            "content": "I love pizza",
        },
    )
    assert r.status_code == 201, r.text
    
    # Delete using index 0 as entry_id (fake storage implementation)
    delete_response = c.delete("/memory/0")
    assert delete_response.status_code == 200, delete_response.text
    body = delete_response.json()
    assert body["success"] is True
    assert "deleted successfully" in body["message"].lower()


def test_delete_memory_not_found(client):
    """Test deleting a memory that doesn't exist."""
    c, fake = client
    
    # Try to delete non-existent memory
    delete_response = c.delete("/memory/nonexistent")
    assert delete_response.status_code == 404, delete_response.text
    body = delete_response.json()
    assert "not found" in body["detail"].lower()


def test_delete_memory_when_storage_not_initialized(monkeypatch):
    """Test that delete fails gracefully when storage is not initialized."""
    from fastapi.testclient import TestClient
    import app.main as main
    
    # Mock storage as None
    monkeypatch.setattr(main, "storage", None)
    
    with TestClient(main.app) as c:
        delete_response = c.delete("/memory/some_id")
        assert delete_response.status_code == 503
        assert "not initialized" in delete_response.json()["detail"].lower()


def test_delete_after_batch_add(client):
    """Test deleting one memory after adding multiple."""
    c, fake = client
    
    # Add multiple dialogues
    r = c.post(
        "/dialogues",
        json={
            "dialogues": [
                {"speaker": "Alice", "content": "First dialogue"},
                {"speaker": "Bob", "content": "Second dialogue"},
                {"speaker": "Charlie", "content": "Third dialogue"},
            ]
        },
    )
    assert r.status_code == 201, r.text
    
    # Delete the second one (index 1)
    delete_response = c.delete("/memory/1")
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["success"] is True
    
    # Verify stats show 2 remaining (if stats endpoint counts correctly)
    stats = c.get("/stats")
    assert stats.status_code == 200
    # Note: In fake storage, we track dialogues, so count should be 2 after deletion
    assert stats.json()["count"] == 2


def test_delete_memory_with_sql_injection_attempt(client):
    """Test that SQL injection attempts are properly handled."""
    c, fake = client
    
    # Try to delete with SQL injection payload
    malicious_entry_id = "abc' OR '1'='1"
    delete_response = c.delete(f"/memory/{malicious_entry_id}")
    
    # Should return 404 (not found) not delete everything
    assert delete_response.status_code == 404
    assert "not found" in delete_response.json()["detail"].lower()
    
    # Verify no memories were deleted by checking stats
    stats = c.get("/stats")
    assert stats.status_code == 200
    # Count should still be 0 since we didn't add any memories
    assert stats.json()["count"] == 0
