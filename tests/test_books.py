def test_book_crud_search_and_availability(client, book_payload):
    created = client.post("/api/v1/books", json=book_payload)
    assert created.status_code == 201
    book = created.json()
    assert book["available_copies"] == 2
    assert book["id"] > 0

    listed = client.get("/api/v1/books?title=Hobbit").json()
    assert listed["total"] == 1
    assert listed["items"][0]["isbn"] == book_payload["isbn"]
    search = client.get("/api/v1/books/search?q=tolkien").json()
    assert search["total"] == 1
    assert client.get(f"/api/v1/books/{book['id']}").json()["title"] == "The Hobbit"
    assert client.get(f"/api/v1/books/{book['id']}/availability").json() == {
        "book_id": book["id"], "available": True, "available_copies": 2
    }

    updated = client.put(f"/api/v1/books/{book['id']}", json={"total_copies": 3, "category": "Classics"})
    assert updated.status_code == 200
    assert updated.json()["available_copies"] == 3
    assert updated.json()["category"] == "Classics"
    assert client.delete(f"/api/v1/books/{book['id']}").status_code == 204
    assert client.get(f"/api/v1/books/{book['id']}").status_code == 404


def test_book_validation_unique_isbn_and_missing_id(client, book_payload):
    assert client.post("/api/v1/books", json=book_payload).status_code == 201
    duplicate = client.post("/api/v1/books", json=book_payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "HTTP_409"
    assert client.get("/api/v1/books/999").status_code == 404
    invalid = client.post("/api/v1/books", json={**book_payload, "total_copies": 0})
    assert invalid.status_code == 422
