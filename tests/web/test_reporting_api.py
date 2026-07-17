"""CRB-26: Reporting API."""


def _eng(**over):
    d = {"client_email": "a@a.io", "role": "coo", "monthly_rate": 5000,
         "start_date": "2026-01-01", "status": "active", "end_date": None}
    d.update(over); return d


def test_summary_empty(client):
    r = client.get("/api/reporting/summary")
    assert r.status_code == 200
    assert r.json() == {"active_count": 0, "monthly_run_rate": 0}


def test_summary_counts_active(client):
    client.post("/api/engagements", json=_eng(client_email="a@a.io", monthly_rate=5000, status="active"))
    client.post("/api/engagements", json=_eng(client_email="b@b.io", monthly_rate=3000, status="active"))
    client.post("/api/engagements", json=_eng(client_email="c@c.io", monthly_rate=9999, status="completed"))
    r = client.get("/api/reporting/summary").json()
    assert r["active_count"] == 2
    assert r["monthly_run_rate"] == 8000
