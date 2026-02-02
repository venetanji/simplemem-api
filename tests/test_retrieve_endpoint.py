from __future__ import annotations


def test_retrieve_all_without_query(client):
    """Test /retrieve endpoint without query parameter returns all memories."""
    c, _fake = client

    # Add some test dialogues
    c.post(
        "/dialogues",
        json={
            "dialogues": [
                {"speaker": "Alice", "content": "I love pizza and robotics."},
                {"speaker": "Bob", "content": "We discussed FastAPI testing."},
                {"speaker": "Cara", "content": "The meeting was at the downtown office."},
            ]
        },
    )

    # Retrieve all memories
    r = c.get("/retrieve")
    assert r.status_code == 200, r.text
    body = r.json()
    
    # Should return all 3 memories
    assert len(body) == 3
    assert all("lossless_restatement" in memory for memory in body)
    assert all("entry_id" in memory for memory in body)


def test_retrieve_with_limit(client):
    """Test /retrieve endpoint with limit parameter."""
    c, _fake = client

    # Add test dialogues
    c.post(
        "/dialogues",
        json={
            "dialogues": [
                {"speaker": "Alice", "content": "Memory one"},
                {"speaker": "Bob", "content": "Memory two"},
                {"speaker": "Cara", "content": "Memory three"},
                {"speaker": "Dave", "content": "Memory four"},
            ]
        },
    )

    # Retrieve with limit
    r = c.get("/retrieve?limit=2")
    assert r.status_code == 200, r.text
    body = r.json()
    
    # Should return only 2 memories
    assert len(body) == 2


def test_retrieve_with_semantic_search(client):
    """Test /retrieve endpoint with query parameter performs semantic search."""
    c, _fake = client

    # Add test dialogues with distinct content
    c.post(
        "/dialogues",
        json={
            "dialogues": [
                {"speaker": "Alice", "content": "I love pizza and robotics."},
                {"speaker": "Bob", "content": "We discussed FastAPI testing."},
                {"speaker": "Cara", "content": "The meeting was about pizza recipes."},
            ]
        },
    )

    # Search for "pizza" - should return matching memories
    r = c.get("/retrieve?query=pizza")
    assert r.status_code == 200, r.text
    body = r.json()
    
    # Should return memories containing "pizza"
    assert len(body) > 0
    # Check that returned memories contain "pizza" in content
    for memory in body:
        assert "pizza" in memory["lossless_restatement"].lower()


def test_retrieve_with_query_and_limit(client):
    """Test /retrieve endpoint with both query and limit parameters."""
    c, _fake = client

    # Add test dialogues
    c.post(
        "/dialogues",
        json={
            "dialogues": [
                {"speaker": "Alice", "content": "Testing is important for software quality."},
                {"speaker": "Bob", "content": "We need more testing coverage."},
                {"speaker": "Cara", "content": "Unit testing saves time."},
                {"speaker": "Dave", "content": "Integration testing is essential."},
            ]
        },
    )

    # Search for "testing" with limit of 2
    r = c.get("/retrieve?query=testing&limit=2")
    assert r.status_code == 200, r.text
    body = r.json()
    
    # Should return at most 2 memories
    assert len(body) <= 2
    assert len(body) > 0
    
    # Verify they contain "testing"
    for memory in body:
        assert "testing" in memory["lossless_restatement"].lower()


def test_retrieve_no_matches(client):
    """Test /retrieve with query that has no matches returns empty list.
    
    Note: Uses /dialogue (singular) endpoint to add a single memory.
    FakeStorageAdapter uses simple keyword matching for semantic search.
    """
    c, _fake = client

    # Add test dialogue using singular endpoint
    c.post(
        "/dialogue",
        json={"speaker": "Alice", "content": "I love pizza."}
    )

    # Search for something that doesn't exist in the content (keyword-based matching)
    r = c.get("/retrieve?query=quantum")
    assert r.status_code == 200, r.text
    body = r.json()
    
    # Should return empty list since "quantum" is not in "I love pizza"
    assert len(body) == 0


def test_retrieve_storage_not_initialized(client):
    """Test /retrieve endpoint when storage is not initialized."""
    from app import main
    
    c, _fake = client
    
    # Temporarily set storage to None
    original_storage = main.storage
    main.storage = None
    
    try:
        r = c.get("/retrieve")
        assert r.status_code == 503, r.text
        assert "not initialized" in r.json()["detail"].lower()
    finally:
        # Restore original storage
        main.storage = original_storage
