from __future__ import annotations


def test_add_dialogue_then_query(client):
    c, _fake = client

    r = c.post(
        "/dialogue",
        json={
            "speaker": "Alice",
            "content": "I love pizza and robotics.",
        },
    )
    assert r.status_code == 201, r.text

    q = c.post("/query", json={"query": "pizza"})
    assert q.status_code == 200, q.text
    body = q.json()
    assert "answer" in body
    assert "pizza" in body["answer"].lower()


def test_add_dialogues_batch_then_query(client):
    c, _fake = client

    r = c.post(
        "/dialogues",
        json={
            "dialogues": [
                {"speaker": "Bob", "content": "We discussed FastAPI testing."},
                {"speaker": "Cara", "content": "The endpoint should be deterministic."},
            ]
        },
    )
    assert r.status_code == 201, r.text

    q = c.post("/ask", json={"query": "fastapi"})
    assert q.status_code == 200, q.text
    assert "fastapi" in q.json()["answer"].lower()


def test_health_reports_initialized(client):
    c, _fake = client

    r = c.get("/health")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "healthy"
    assert body["simplemem_initialized"] is True
