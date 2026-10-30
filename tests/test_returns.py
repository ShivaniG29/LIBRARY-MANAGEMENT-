from datetime import date, timedelta

from sqlalchemy import select

from app.database.database import get_db
from app.models.issue import Issue


def test_return_updates_copies_status_details_and_fine(client, book_payload, member_payload, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "fine_per_day", 2.5)
    book = client.post("/api/v1/books", json=book_payload).json()
    member = client.post("/api/v1/members", json=member_payload).json()
    issue = client.post("/api/v1/issues", json={"book_id": book["id"], "member_id": member["id"]}).json()

    db = next(client.app.dependency_overrides[get_db]())
    try:
        record = db.scalar(select(Issue).where(Issue.id == issue["id"]))
        record.due_date = date.today() - timedelta(days=3)
        db.commit()
    finally:
        db.close()

    returned = client.post(f"/api/v1/returns/{issue['id']}")
    assert returned.status_code == 200
    assert returned.json()["status"] == "Returned"
    assert returned.json()["overdue_days"] == 3
    assert returned.json()["fine_amount"] == 7.5
    assert client.get(f"/api/v1/books/{book['id']}/availability").json()["available_copies"] == 2
    assert client.get(f"/api/v1/returns/{issue['id']}").json()["fine_amount"] == 7.5
    assert client.get("/api/v1/issues").json()["total"] == 0
    assert client.post(f"/api/v1/returns/{issue['id']}").status_code == 409


def test_return_on_time_has_no_fine_and_unknown_issue_errors(client, book_payload, member_payload):
    book = client.post("/api/v1/books", json=book_payload).json()
    member = client.post("/api/v1/members", json=member_payload).json()
    issue = client.post("/api/v1/issues", json={"book_id": book["id"], "member_id": member["id"]}).json()
    assert client.get(f"/api/v1/returns/{issue['id']}").status_code == 409
    returned = client.post(f"/api/v1/returns/{issue['id']}")
    assert returned.status_code == 200
    assert returned.json()["fine_amount"] == 0
    assert returned.json()["overdue_days"] == 0
    assert client.post("/api/v1/returns/999").status_code == 404
