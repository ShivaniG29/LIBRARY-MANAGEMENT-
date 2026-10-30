from datetime import date, timedelta

from sqlalchemy import select

from app.database.database import get_db
from app.models.issue import Issue


def test_dashboard_statistics(client, book_payload, member_payload):
    book = client.post("/api/v1/books", json={**book_payload, "total_copies": 3}).json()
    member = client.post("/api/v1/members", json=member_payload).json()
    issue = client.post("/api/v1/issues", json={"book_id": book["id"], "member_id": member["id"]}).json()
    db = next(client.app.dependency_overrides[get_db]())
    try:
        record = db.scalar(select(Issue).where(Issue.id == issue["id"]))
        record.due_date = date.today() - timedelta(days=1)
        db.commit()
    finally:
        db.close()

    current = client.get("/api/v1/dashboard")
    assert current.status_code == 200
    assert current.json() == {
        "total_books": 1,
        "total_members": 1,
        "total_available_copies": 2,
        "currently_issued_books": 1,
        "overdue_books": 1,
        "returned_books": 0,
    }
    assert client.post(f"/api/v1/returns/{issue['id']}").status_code == 200
    assert client.get("/api/v1/dashboard").json()["returned_books"] == 1
