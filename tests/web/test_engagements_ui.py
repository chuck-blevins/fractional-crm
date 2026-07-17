"""CRB-31 acceptance: Engagements UI + dashboard reporting widgets.

Engagements are keyed by client_email (one per client), mirroring the Clients UI (CRB-30).
The dashboard (`/`) fills the CRB-29 slots with an active-engagement count and a monthly
run-rate, both read from the reporting summary.
"""


def _seed(client, **over):
    """Create an engagement via the JSON API and return the payload."""
    payload = {"client_email": "ada@acme.io", "role": "coo", "monthly_rate": 5000,
               "start_date": "2026-01-01", "status": "active"}
    payload.update(over)
    r = client.post("/api/engagements", json=payload)
    assert r.status_code == 201, r.text
    return payload


# --------------------------------------------------------------------------- list


def test_engagements_list_renders_seeded_rows(client):
    _seed(client, client_email="ada@acme.io")
    _seed(client, client_email="grace@navy.mil", role="cpo")
    r = client.get("/engagements")
    assert r.status_code == 200
    html = r.text
    assert "<table" in html.lower()
    assert "ada@acme.io" in html
    assert "grace@navy.mil" in html


def test_list_is_filterable_by_client(client):
    _seed(client, client_email="ada@acme.io")
    _seed(client, client_email="grace@navy.mil")
    html = client.get("/engagements?client_email=ada@acme.io").text
    assert "ada@acme.io" in html
    assert "grace@navy.mil" not in html


# --------------------------------------------------------------------------- create validation


def test_create_rejects_nonpositive_rate_accessibly(client):
    r = client.post(
        "/engagements",
        data={"client_email": "new@acme.io", "role": "coo", "monthly_rate": "0",
              "start_date": "2026-01-01", "status": "proposed", "end_date": ""},
        follow_redirects=False,
    )
    # Domain error surfaced in the form, not a redirect and not a 422.
    assert r.status_code == 200
    lower = r.text.lower()
    assert 'role="alert"' in lower
    assert "rate" in lower and ("positive" in lower or "must" in lower)
    # Nothing persisted.
    assert client.get("/api/engagements/new@acme.io").status_code == 404


def test_create_rejects_end_before_start_accessibly(client):
    r = client.post(
        "/engagements",
        data={"client_email": "new@acme.io", "role": "coo", "monthly_rate": "4000",
              "start_date": "2026-06-01", "status": "proposed", "end_date": "2026-01-01"},
        follow_redirects=False,
    )
    assert r.status_code == 200
    lower = r.text.lower()
    assert 'role="alert"' in lower
    assert "end_date" in lower or "on or after" in lower
    assert client.get("/api/engagements/new@acme.io").status_code == 404


def test_valid_create_persists_and_redirects(client):
    r = client.post(
        "/engagements",
        data={"client_email": "kj@nasa.gov", "role": "advisor", "monthly_rate": "7500",
              "start_date": "2026-02-01", "status": "proposed", "end_date": ""},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303, 307)
    assert "/engagements" in r.headers["location"]
    got = client.get("/api/engagements/kj@nasa.gov")
    assert got.status_code == 200
    assert got.json()["monthly_rate"] == 7500


def test_new_form_selects_limited_to_allowed_enums(client):
    html = client.get("/engagements/new").text
    for role in ("coo", "cpo", "advisor"):
        assert f'value="{role}"' in html
    for status in ("proposed", "active", "completed", "cancelled"):
        assert f'value="{status}"' in html
    # A value outside the domain enums must never be offered.
    assert 'value="ceo"' not in html
    assert 'value="prospect"' not in html  # that's a *client* status, not an engagement one


# --------------------------------------------------------------------------- dashboard widgets


def test_dashboard_shows_active_count_and_currency_run_rate(client):
    _seed(client, client_email="ada@acme.io", monthly_rate=5000, status="active")
    _seed(client, client_email="grace@navy.mil", monthly_rate=9999, status="completed")
    html = client.get("/").text
    # Exactly one active engagement; run-rate counts only the active one.
    assert 'data-testid="dash-active-count">1<' in html
    assert 'data-testid="dash-run-rate">$5,000<' in html


def test_dashboard_run_rate_is_zero_dollars_when_none(client):
    html = client.get("/").text
    assert 'data-testid="dash-run-rate">$0<' in html
    assert 'data-testid="dash-active-count">0<' in html
