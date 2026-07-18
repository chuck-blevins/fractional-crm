"""Every server-rendered page must be structurally valid HTML (CRB-32 follow-up).

The CRB-32 timeline shipped a ``<p>`` directly inside an ``<ol>`` and all six story tests
passed, because they assert on strings, not structure. These tests close that gap across the
whole UI surface: each page is rendered with realistic data and checked against the content
model, id uniqueness, label binding and single-h1 rules in ``tests/web/htmlcheck.py``.

The first block is a meta-test suite for the checker itself. A validator that silently passes
everything is worse than no validator — it converts an unchecked risk into a false sense of
safety — so the checker is pinned against known-bad markup, including the exact CRB-32 defect.
"""
import pytest

from htmlcheck import assert_valid_html, validate

# --------------------------------------------------------------------- the checker itself


def test_checker_catches_the_crb32_defect():
    """The exact regression this module exists for: a <p> nested directly in an <ol>."""
    errors = validate("<ol id='timeline'><p>No interactions yet</p></ol>", fragment=True)
    assert any("<p> is not allowed as a direct child of <ol>" in e for e in errors), errors


def test_checker_accepts_the_fixed_markup():
    """The shipped fix — the empty state as a sibling of the list, not a child."""
    good = "<p>No interactions yet</p>"
    assert validate(good, fragment=True) == []
    good_list = "<ol id='timeline'><li><time datetime='2026-01-01'>2026-01-01</time></li></ol>"
    assert validate(good_list, fragment=True) == []


@pytest.mark.parametrize("markup, expected", [
    ("<table><li>x</li></table>", "not allowed as a direct child of <table>"),
    ("<select><div>x</div></select>", "not allowed as a direct child of <select>"),
    ("<ul>loose text</ul>", "text is not allowed as a direct child of <ul>"),
    ("<div><span>x</div>", "is not closed"),
    ("<div>x</div></section>", "stray </section>"),
    ("<div><p>x</p>", "is never closed"),
    ("<div id='a'></div><div id='a'></div>", "duplicate id='a'"),
    ("<label for='nope'>N</label>", "does not match any element id"),
    ("<form><input type='text' name='q'></form>", "has no associated <label>"),
    ("<select name='k'><option value='1'>1</option></select>", "has no associated <label>"),
])
def test_checker_catches_known_bad_markup(markup, expected):
    """Each rule fires on markup that violates it."""
    errors = validate(markup, fragment=True)
    assert any(expected in e for e in errors), f"{expected!r} not in {errors}"


@pytest.mark.parametrize("markup", [
    # Optional end tags are legal HTML5 and must not be reported.
    "<ul><li>one<li>two</ul>",
    "<dl><dt>k<dd>v</dl>",
    "<table><tr><td>a<td>b</table>",
    "<select id='k' name='k'><option value='1'>1<option value='2'>2</select>"
    "<label for='k'>Kind</label>",
    # Void elements, self-closing syntax, and labelled controls.
    "<br><hr><img src='x.png' alt='x'>",
    "<label for='q'>Q</label><input id='q' name='q'>",
    "<label>Wrapped<input name='q'></label>",
    "<input type='hidden' name='csrf'><button type='submit'>Go</button>",
    "<input name='q' aria-label='Search'>",
])
def test_checker_accepts_valid_markup(markup):
    """The checker stays quiet on conformant markup — no false positives."""
    assert validate(markup, fragment=True) == []


def test_assert_valid_html_reports_every_problem_at_once():
    """The assertion lists all findings, so one run fixes everything."""
    with pytest.raises(AssertionError) as excinfo:
        assert_valid_html("<ol><p>x</p></ol><div id='a'></div><div id='a'></div>",
                          context="sample", fragment=True)
    message = str(excinfo.value)
    assert "sample" in message
    assert "not allowed as a direct child of <ol>" in message
    assert "duplicate id='a'" in message


def test_full_page_needs_exactly_one_h1():
    """Pages get the single-h1 rule; fragments are exempt."""
    assert any("exactly one <h1>" in e for e in validate("<main><h1>a</h1><h1>b</h1></main>"))
    assert any("exactly one <h1>" in e for e in validate("<main>no heading</main>"))
    assert validate("<main>no heading</main>", fragment=True) == []


# ------------------------------------------------------------------------- the real pages


def _seed_client(client, **over):
    """Create a client via the JSON API."""
    payload = {"name": "Ada Lovelace", "company": "Acme", "email": "ada@acme.io",
               "status": "active", "engagement_type": "coo"}
    payload.update(over)
    assert client.post("/api/clients", json=payload).status_code == 201


def _seed_engagement(client, **over):
    """Create an engagement via the JSON API."""
    payload = {"client_email": "ada@acme.io", "role": "coo", "monthly_rate": 5000,
               "start_date": "2026-01-01", "status": "active"}
    payload.update(over)
    assert client.post("/api/engagements", json=payload).status_code == 201


def _seed_all(client):
    """Populate enough data that every page renders a non-empty state."""
    _seed_client(client)
    _seed_client(client, email="grace@navy.mil", name="Grace Hopper", company="Navy")
    _seed_engagement(client)
    for date, kind, summary in [("2026-01-01", "note", "Kickoff notes"),
                                ("2026-03-01", "email", "Follow-up email")]:
        assert client.post("/api/clients/ada@acme.io/interactions",
                           json={"date": date, "kind": kind, "summary": summary}).status_code == 201


PAGES = [
    "/",
    "/clients",
    "/clients/new",
    "/clients/ada@acme.io",
    "/clients/ada@acme.io/edit",
    "/engagements",
    "/engagements?client_email=ada@acme.io",
    "/engagements/new",
    "/engagements/ada@acme.io/edit",
]


@pytest.mark.parametrize("path", PAGES)
def test_populated_pages_are_valid_html(client, path):
    """Every UI page renders valid HTML with data present."""
    _seed_all(client)
    response = client.get(path)
    assert response.status_code == 200, response.text
    assert_valid_html(response.text, context=f"GET {path} (populated)")


@pytest.mark.parametrize("path", PAGES)
def test_empty_state_pages_are_valid_html(client, path):
    """Empty states are valid too — this is where the CRB-32 defect lived."""
    if path.startswith("/clients/ada") or path.startswith("/engagements/ada"):
        pytest.skip("detail/edit pages require the record to exist")
    response = client.get(path)
    assert response.status_code == 200, response.text
    assert_valid_html(response.text, context=f"GET {path} (empty)")


def test_detail_page_with_no_interactions_is_valid_html(client):
    """THE regression case: a client that exists but has logged nothing.

    This is the exact branch the CRB-32 defect lived in — the empty-state ``<p>`` inside the
    ``<ol>``. It only renders when the timeline is empty, so a fixture that seeds interactions
    never reaches it. Verified by reintroducing the bad markup and watching this test fail.
    """
    _seed_client(client, email="grace@navy.mil", name="Grace Hopper")
    response = client.get("/clients/grace@navy.mil")
    assert response.status_code == 200
    assert "no interactions" in response.text.lower()  # the empty branch really did render
    assert_valid_html(response.text, context="GET /clients/{email} with an empty timeline")


def test_empty_htmx_timeline_fragment_is_valid_html(client):
    """The same empty branch as an HTMX partial."""
    _seed_client(client, email="grace@navy.mil")
    response = client.post("/clients/grace@navy.mil/interactions",
                           data={"date": "2026-05-01", "kind": "call", "summary": "  "},
                           headers={"HX-Request": "true"}, follow_redirects=False)
    assert response.status_code == 200
    assert_valid_html(response.text, context="HTMX timeline fragment (empty)", fragment=True)


def test_login_page_is_valid_html(anon_client):
    """The one page rendered outside the session gate."""
    response = anon_client.get("/login")
    assert response.status_code == 200
    assert_valid_html(response.text, context="GET /login")


def test_error_state_pages_are_valid_html(client):
    """Re-rendered forms carry a role=alert region — validate that path too."""
    _seed_all(client)
    bad_interaction = client.post("/clients/ada@acme.io/interactions",
                                  data={"date": "2026-02-01", "kind": "call", "summary": "   "},
                                  follow_redirects=False)
    assert bad_interaction.status_code == 200
    assert_valid_html(bad_interaction.text, context="POST interaction (invalid summary)")

    bad_client = client.post("/clients", data={"name": "", "company": "X", "email": "bad",
                                               "status": "active", "engagement_type": "coo"},
                             follow_redirects=False)
    assert bad_client.status_code == 200
    assert_valid_html(bad_client.text, context="POST /clients (invalid)")


def test_htmx_fragments_are_valid_html(client):
    """HTMX partials are checked as fragments (no <h1>, no document shell)."""
    _seed_all(client)
    timeline = client.post("/clients/ada@acme.io/interactions",
                           data={"date": "2026-04-01", "kind": "meeting", "summary": "QBR"},
                           headers={"HX-Request": "true"}, follow_redirects=False)
    assert timeline.status_code == 200
    assert_valid_html(timeline.text, context="HTMX timeline fragment", fragment=True)

    table = client.get("/clients", headers={"HX-Request": "true"})
    assert table.status_code == 200
    assert_valid_html(table.text, context="HTMX clients table fragment", fragment=True)
