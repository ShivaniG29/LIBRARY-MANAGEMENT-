from datetime import date, timedelta

from sqlalchemy import select

from app.database.database import get_db
from app.models.issue import Issue


def add_book_and_member(client, book_payload, member_payload):
    book = client.post("/api/v1/books", json=book_payload).json()
    member = client.post("/api/v1/members", json=member_payload).json()
    return book, member


def test_issue_decreases_copies_and_rejects_duplicate(client, book_payload, member_payload):
    book, member = add_book_and_member(client, book_payload, member_payload)
    payload = {"book_id": book["id"], "member_id": member["id"]}
    issued = client.post("/api/v1/issues", json=payload)
    assert issued.status_code == 201
    issue = issued.json()
    assert issue["status"] == "Issued"
    assert issue["due_date"] > issue["issue_date"]
    assert client.get(f"/api/v1/books/{book['id']}/availability").json()["available_copies"] == 1
    assert client.post("/api/v1/issues", json=payload).status_code == 409
    assert client.get("/api/v1/issues").json()["total"] == 1
    assert client.get(f"/api/v1/issues?member_id={member['id']}").json()["total"] == 1
    assert client.get(f"/api/v1/issues/{issue['id']}").json()["id"] == issue["id"]


def test_issue_validations_and_active_delete_restrictions(client, book_payload, member_payload):
    book, member = add_book_and_member(client, {**book_payload, "total_copies": 1}, member_payload)
    payload = {"book_id": book["id"], "member_id": member["id"]}
    inactive = client.put(
        f"/api/v1/members/{member['id']}", json={"membership_status": "Inactive"}
    )
    assert inactive.status_code == 200
    assert client.post("/api/v1/issues", json=payload).status_code == 409
    client.put(f"/api/v1/members/{member['id']}", json={"membership_status": "Active"})

    assert client.post("/api/v1/issues", json=payload).status_code == 201
    assert client.post("/api/v1/issues", json=payload).status_code == 409
    assert client.delete(f"/api/v1/books/{book['id']}").status_code == 409
    assert client.delete(f"/api/v1/members/{member['id']}").status_code == 409
    assert client.post("/api/v1/issues", json={"book_id": 999, "member_id": member["id"]}).status_code == 404
    assert client.post("/api/v1/issues", json={"book_id": book["id"], "member_id": 999}).status_code == 404


def test_issue_rejects_unavailable_book(client, book_payload, member_payload):
    book, member = add_book_and_member(client, {**book_payload, "total_copies": 1}, member_payload)
    payload = {"book_id": book["id"], "member_id": member["id"]}
    assert client.post("/api/v1/issues", json=payload).status_code == 201
    other_member = client.post("/api/v1/members", json={**member_payload, "email": "other@example.com"}).json()
    unavailable = client.post("/api/v1/issues", json={"book_id": book["id"], "member_id": other_member["id"]})
    assert unavailable.status_code == 409
    assert client.get(f"/api/v1/books/{book['id']}/availability").json()["available"] is False


def test_issue_status_changes_to_overdue(client, book_payload, member_payload):
    book, member = add_book_and_member(client, book_payload, member_payload)
    issue = client.post("/api/v1/issues", json={"book_id": book["id"], "member_id": member["id"]}).json()
    db = next(app_db for app_db in client.app.dependency_overrides[get_db]())
    try:
        record = db.scalar(select(Issue).where(Issue.id == issue["id"]))
        record.due_date = date.today() - timedelta(days=1)
        db.commit()
    finally:
        db.close()
    assert client.get(f"/api/v1/issues/{issue['id']}").json()["status"] == "Overdue"
