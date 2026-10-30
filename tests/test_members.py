def test_member_crud_and_filter(client, member_payload):
    created = client.post("/api/v1/members", json=member_payload)
    assert created.status_code == 201
    member = created.json()
    assert member["membership_status"] == "Active"
    assert member["membership_date"]

    assert client.get("/api/v1/members").json()["total"] == 1
    assert client.get("/api/v1/members?membership_status=Inactive").json()["total"] == 0
    assert client.get(f"/api/v1/members/{member['id']}").json()["email"] == member_payload["email"]
    updated = client.put(
        f"/api/v1/members/{member['id']}",
        json={"membership_status": "Inactive", "name": "Alex R"},
    )
    assert updated.status_code == 200
    assert updated.json()["membership_status"] == "Inactive"
    assert updated.json()["name"] == "Alex R"
    assert client.delete(f"/api/v1/members/{member['id']}").status_code == 204
    assert client.get(f"/api/v1/members/{member['id']}").status_code == 404


def test_member_email_unique_and_invalid_id(client, member_payload):
    assert client.post("/api/v1/members", json=member_payload).status_code == 201
    duplicate = client.post("/api/v1/members", json=member_payload)
    assert duplicate.status_code == 409
    assert client.get("/api/v1/members/999").status_code == 404
    assert client.post("/api/v1/members", json={**member_payload, "email": "bad"}).status_code == 422
