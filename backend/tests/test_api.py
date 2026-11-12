"""Automated API tests. Run from the backend folder:  python -m pytest -v
Uses an in-memory SQLite database and the labelled AI fallback (no API key needed)."""
import io

import pytest

from app import create_app
from app.config import TestConfig
from app.models import db
from app.cli import SQL_DIR, run_sql_file

PDF = b"%PDF-1.4 test file"


@pytest.fixture()
def client():
    app = create_app(TestConfig)
    with app.app_context():
        # same SQL files an evaluator runs in Supabase: departments + test accounts
        run_sql_file(SQL_DIR / "reference_data.sql")
        run_sql_file(SQL_DIR / "demo_accounts.sql")
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def login(client, email, password="Demo@1234"):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.json
    return {"Authorization": f"Bearer {r.json['token']}"}


def submit(client, headers, **extra):
    data = {"district": "Ernakulam", "category": "Water Supply",
            "subject": "No water supply in our street",
            "description": "There has been no drinking water in our street for four days. Urgent help needed.",
            **extra}
    return client.post("/api/grievances", data=data, headers=headers,
                       content_type="multipart/form-data")


# ---------- auth ----------
def test_register_and_login(client):
    r = client.post("/api/auth/register", json={"name": "Test User", "email": "t@x.com",
                                                "mobile": "9876543210", "password": "Passw0rd!"})
    assert r.status_code == 201 and r.json["user"]["role"] == "citizen"
    login(client, "t@x.com", "Passw0rd!")


def test_register_validation(client):
    r = client.post("/api/auth/register", json={"name": "A", "email": "bad", "mobile": "12",
                                                "password": "short"})
    assert r.status_code == 400
    assert set(r.json["fields"]) == {"name", "email", "mobile", "password"}


def test_wrong_password(client):
    r = client.post("/api/auth/login", json={"email": "cmo@demo.com", "password": "nope"})
    assert r.status_code == 401


def test_protected_routes_need_token(client):
    assert client.get("/api/grievances").status_code == 401
    assert client.get("/api/grievances", headers={"Authorization": "Bearer junk"}).status_code == 401


# ---------- role-based access ----------
def test_citizen_cannot_use_cmo_endpoints(client):
    h = login(client, "citizen@demo.com")
    assert client.get("/api/officers", headers=h).status_code == 403
    assert client.post("/api/grievances/1/assign", json={"department_id": 1}, headers=h).status_code == 403


def test_citizen_sees_only_own_grievances(client):
    h1, h2 = login(client, "citizen@demo.com"), login(client, "citizen2@demo.com")
    ref = submit(client, h1).json["grievance"]["id"]
    assert client.get(f"/api/grievances/{ref}", headers=h2).status_code == 404
    mine = client.get("/api/grievances", headers=h2).json
    assert all(g["citizen"].startswith("Fathima") for g in mine)


def test_officer_sees_only_department(client):
    cit, cmo = login(client, "citizen@demo.com"), login(client, "cmo@demo.com")
    h = login(client, "officer.kwa@demo.com")
    gid = submit(client, cit).json["grievance"]["id"]
    depts = {d["code"]: d["id"] for d in client.get("/api/departments").json}
    assert client.get("/api/grievances", headers=h).json == []
    client.post(f"/api/grievances/{gid}/assign", headers=cmo, json={"department_id": depts["KWA"]})
    items = client.get("/api/grievances", headers=h).json
    assert len(items) == 1 and items[0]["department"] == "Water Authority"
    # an officer of another department still sees nothing
    other = login(client, "officer.pwd@demo.com")
    assert client.get("/api/grievances", headers=other).json == []


def test_cmo_creates_officer(client):
    cmo, cit = login(client, "cmo@demo.com"), login(client, "citizen@demo.com")
    dept = client.get("/api/departments").json[0]["id"]
    body = {"name": "New Officer", "email": "new.officer@gov.test", "mobile": "9876501234",
            "password": "Officer123", "department_id": dept}
    assert client.post("/api/officers", json=body, headers=cit).status_code == 403
    r = client.post("/api/officers", json=body, headers=cmo)
    assert r.status_code == 201 and r.json["role"] == "officer" and r.json["department_id"] == dept
    login(client, "new.officer@gov.test", "Officer123")
    assert client.post("/api/officers", json=body, headers=cmo).status_code == 400  # duplicate email
    bad = client.post("/api/officers", json={**body, "email": "x@y.test", "department_id": 0}, headers=cmo)
    assert bad.status_code == 400 and "department_id" in bad.json["fields"]


# ---------- submission, upload, tracking ----------
def test_submit_generates_reference_and_ai(client):
    h = login(client, "citizen@demo.com")
    r = submit(client, h, attachment=(io.BytesIO(PDF), "proof.pdf"))
    assert r.status_code == 201
    g = r.json["grievance"]
    assert r.json["ref_id"].startswith("CMK-")
    assert g["status"] == "Submitted" and len(g["attachments"]) == 1
    assert g["ai"]["source"] == "fallback" and g["ai"]["category"] == "Water Supply"
    # file can be downloaded by the owner
    f = client.get(f"/api/grievances/attachments/{g['attachments'][0]['id']}", headers=h)
    assert f.status_code == 200 and f.data == PDF
    # public tracking works without login
    t = client.get(f"/api/track/{r.json['ref_id']}")
    assert t.status_code == 200 and t.json["status"] == "Submitted"


def test_rejects_fake_file(client):
    h = login(client, "citizen@demo.com")
    r = submit(client, h, attachment=(io.BytesIO(b"not really a pdf"), "x.pdf"))
    assert r.status_code == 400


def test_track_unknown_reference(client):
    assert client.get("/api/track/CMK-0000-000000").status_code == 404


# ---------- full mandatory workflow ----------
def test_end_to_end_workflow(client):
    cit, cmo = login(client, "citizen@demo.com"), login(client, "cmo@demo.com")
    off = login(client, "officer.kwa@demo.com")
    gid = submit(client, cit).json["grievance"]["id"]

    # officer cannot see it before it is forwarded
    assert client.get(f"/api/grievances/{gid}", headers=off).status_code == 404

    depts = {d["code"]: d["id"] for d in client.get("/api/departments").json}
    r = client.post(f"/api/grievances/{gid}/assign", headers=cmo,
                    json={"department_id": depts["KWA"], "note": "Check urgently"})
    assert r.json["status"] == "Under Review"

    client.post(f"/api/grievances/{gid}/remarks", headers=cmo,
                json={"remark": "Internal note", "internal": True})

    r = client.patch(f"/api/grievances/{gid}/status", headers=off,
                     json={"status": "In Progress", "remark": "Team sent"})
    assert r.json["status"] == "In Progress"

    r = client.post(f"/api/grievances/{gid}/reports", headers=off,
                    data={"report": "Pipeline repaired and supply restored."},
                    content_type="multipart/form-data")
    assert r.status_code == 201
    rid = r.json["reports"][0]["id"]

    # citizen cannot resolve; CMO accepts the report -> Resolved
    assert client.patch(f"/api/grievances/{gid}/status", headers=cit,
                        json={"status": "Resolved", "remark": "x"}).status_code == 409
    r = client.post(f"/api/grievances/{gid}/reports/{rid}/review", headers=cmo,
                    json={"decision": "accept", "remark": "Verified"})
    assert r.json["status"] == "Resolved"

    # citizen sees public remarks but not internal ones
    d = client.get(f"/api/grievances/{gid}", headers=cit).json
    assert not any(h["is_internal"] for h in d["history"])

    # feedback, then reopen
    assert client.post(f"/api/grievances/{gid}/feedback", headers=cit,
                       json={"rating": 4, "comment": "Thanks"}).status_code == 201
    r = client.patch(f"/api/grievances/{gid}/status", headers=cit,
                     json={"status": "Reopened", "remark": "Water stopped again"})
    assert r.json["status"] == "Reopened"

    # every status change is stored with user and timestamp
    full = client.get(f"/api/grievances/{gid}", headers=cmo).json
    statuses = [h["to_status"] for h in full["history"]]
    for s in ("Submitted", "Under Review", "In Progress", "Resolved", "Reopened"):
        assert s in statuses
    assert all(h["by"] and h["at"] for h in full["history"])


def test_invalid_transition_blocked(client):
    cit, off = login(client, "citizen@demo.com"), login(client, "cmo@demo.com")
    gid = submit(client, cit).json["grievance"]["id"]
    r = client.patch(f"/api/grievances/{gid}/status", headers=off,
                     json={"status": "Resolved"})  # remark missing
    assert r.status_code == 400


# ---------- stats, AI, contact ----------
def test_stats(client):
    h = login(client, "cmo@demo.com")
    s = client.get("/api/stats", headers=h).json
    assert s["total"] == s["resolved"] + s["pending"]
    assert len(s["by_district"]) == 14


def test_ai_analyze_fallback_is_labelled(client):
    h = login(client, "citizen@demo.com")
    r = client.post("/api/ai/analyze", headers=h, json={
        "subject": "Live electric wire fallen", "district": "Kollam",
        "description": "A live electric wire has fallen on the road near the market. Danger to people."})
    assert r.status_code == 200
    assert r.json["source"] == "fallback" and "NOT AI output" in r.json["notice"]
    assert r.json["category"] == "Electricity" and r.json["priority"] == "High"


def test_contact_saved(client):
    r = client.post("/api/contact", json={"name": "A B", "email": "a@b.com",
                                          "subject": "Hi", "message": "Hello"})
    assert r.status_code == 201
    h = login(client, "cmo@demo.com")
    assert any(e["subject"] == "Hi" for e in client.get("/api/contact-enquiries", headers=h).json)
