"""CRB-27: CSV import/export API."""
import json


def _client(**over):
    d = {"name": "Ada", "company": "Acme", "email": "ada@acme.io",
         "status": "active", "engagement_type": "coo"}
    d.update(over); return d


def test_export(client):
    client.post("/api/clients", json=_client())
    r = client.get("/api/clients/csv/export")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers.get("content-disposition", "").lower()
    lines = r.text.splitlines()
    assert lines[0] == "name,company,email,status,engagement_type"
    assert any("ada@acme.io" in ln for ln in lines[1:])


def test_import_csv_file(client):
    csv_text = ("name,company,email,status,engagement_type\n"
                "Ada,Acme,ada@acme.io,active,coo\n"
                "Bad,X,not-an-email,active,coo\n")
    r = client.post("/api/clients/csv/import", files={"file": ("clients.csv", csv_text, "text/csv")})
    assert r.status_code == 200
    body = r.json()
    assert body["imported"] == 1
    assert len(body["errors"]) == 1
    assert client.get("/api/clients/ada@acme.io").status_code == 200


def test_import_json_file(client):
    data = json.dumps([_client(email="grace@navy.mil", name="Grace")])
    r = client.post("/api/clients/csv/import", files={"file": ("clients.json", data, "application/json")})
    assert r.status_code == 200
    assert r.json()["imported"] == 1


def test_import_oversize_413(client):
    r = client.post("/api/clients/csv/import",
                    files={"file": ("big.csv", "x" * (5 * 1024 * 1024 + 1), "text/csv")})
    assert r.status_code == 413
