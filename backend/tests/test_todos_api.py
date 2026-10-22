"""API tests covering the ToDo list contract."""

from __future__ import annotations

from fastapi.testclient import TestClient

TITLE_LIMIT = 200
DESCRIPTION_LIMIT = 2000


def create_item(client: TestClient, title: str = "Write tests", description: str = "") -> dict:
    response = client.post("/api/todos", json={"title": title, "description": description})
    assert response.status_code == 201, response.text
    return response.json()


def test_empty_list(client: TestClient):
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_create_returns_item_with_all_fields(client: TestClient):
    response = client.post(
        "/api/todos",
        json={"title": "Buy groceries", "description": "Milk and bread"},
    )

    assert response.status_code == 201
    item = response.json()
    assert item["id"] > 0
    assert item["title"] == "Buy groceries"
    assert item["description"] == "Milk and bread"
    assert item["completed"] is False
    assert item["created_at"]


def test_create_with_title_only(client: TestClient):
    response = client.post("/api/todos", json={"title": "Call mom"})

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_created_item_is_listed_and_fetchable(client: TestClient):
    created = create_item(client, "Book flight")

    listing = client.get("/api/todos")
    single = client.get(f"/api/todos/{created['id']}")

    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()] == [created["id"]]
    assert single.status_code == 200
    assert single.json() == created


def test_list_contains_every_item_oldest_first(client: TestClient):
    first = create_item(client, "First")
    second = create_item(client, "Second")

    items = client.get("/api/todos").json()

    assert [item["id"] for item in items] == [first["id"], second["id"]]


def test_blank_title_is_rejected_and_nothing_is_stored(client: TestClient):
    for title in ("", "   ", "\t"):
        response = client.post("/api/todos", json={"title": title})
        assert response.status_code == 422, title

    assert client.get("/api/todos").json() == []


def test_title_over_limit_is_rejected(client: TestClient):
    response = client.post("/api/todos", json={"title": "x" * (TITLE_LIMIT + 1)})

    assert response.status_code == 422


def test_description_over_limit_is_rejected(client: TestClient):
    response = client.post(
        "/api/todos",
        json={"title": "Too long", "description": "x" * (DESCRIPTION_LIMIT + 1)},
    )

    assert response.status_code == 422


def test_edit_updates_values_and_keeps_id_and_creation_date(client: TestClient):
    created = create_item(client, "Draft", "First version")

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={"title": "Final", "description": "Second version"},
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == created["id"]
    assert updated["created_at"] == created["created_at"]
    assert updated["title"] == "Final"
    assert updated["description"] == "Second version"
    assert updated["completed"] is False


def test_edit_with_blank_title_keeps_previous_values(client: TestClient):
    created = create_item(client, "Keep me")

    response = client.patch(f"/api/todos/{created['id']}", json={"title": "   "})

    assert response.status_code == 422
    stored = client.get(f"/api/todos/{created['id']}").json()
    assert stored["title"] == "Keep me"


def test_completion_toggle_preserves_other_fields(client: TestClient):
    created = create_item(client, "Water plants", "Kitchen and balcony")

    completed = client.patch(f"/api/todos/{created['id']}", json={"completed": True}).json()
    assert completed["completed"] is True
    assert completed["title"] == created["title"]
    assert completed["description"] == created["description"]
    assert completed["created_at"] == created["created_at"]

    reopened = client.patch(f"/api/todos/{created['id']}", json={"completed": False}).json()
    assert reopened["completed"] is False
    assert reopened["title"] == created["title"]
    assert reopened["created_at"] == created["created_at"]


def test_missing_item_returns_json_404(client: TestClient):
    get_response = client.get("/api/todos/4242")
    patch_response = client.patch("/api/todos/4242", json={"completed": True})
    delete_response = client.delete("/api/todos/4242")

    for response in (get_response, patch_response, delete_response):
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"


def test_delete_removes_item(client: TestClient):
    created = create_item(client, "Temporary")

    response = client.delete(f"/api/todos/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/api/todos").json() == []


def test_items_persist_across_app_instances(client: TestClient, fastapi_app):
    created = create_item(client, "Survive restart")
    client.patch(f"/api/todos/{created['id']}", json={"completed": True})

    with TestClient(fastapi_app) as second_client:
        items = second_client.get("/api/todos").json()

    assert len(items) == 1
    assert items[0]["id"] == created["id"]
    assert items[0]["title"] == "Survive restart"
    assert items[0]["completed"] is True
    assert items[0]["created_at"] == created["created_at"]


def test_api_returns_json_content_type(client: TestClient):
    response = client.get("/api/todos")

    assert response.headers["content-type"].startswith("application/json")
