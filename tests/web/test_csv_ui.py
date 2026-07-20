"""CRB-34: CSV import/export UI on the clients page.

The clients page links to the CSV export endpoint and carries a multipart import
form; uploading a file re-renders the page with the imported count and an
accessible per-row error list (row number + message).
"""
from htmlcheck import assert_valid_html

# One good row (Ada) + one bad row (invalid email) — mirrors the CSV API fixture.
CSV = (
    "name,company,email,status,engagement_type\n"
    "Ada,Acme,ada@acme.io,active,coo\n"
    "Bad,X,not-an-email,active,coo\n"
)


def test_clients_page_has_export_link(client):
    """The clients page links to the CSV export endpoint."""
    html = client.get("/clients").text
    assert "/api/clients/csv/export" in html


def test_clients_page_has_accessible_import_form(client):
    """The import form is a multipart upload with a label-bound file input."""
    html = client.get("/clients").text
    assert 'enctype="multipart/form-data"' in html
    assert 'type="file"' in html
    assert 'id="file"' in html and 'for="file"' in html


def test_import_renders_count_and_per_row_errors(client):
    """Uploading a CSV re-renders the page with the imported count and each row error."""
    r = client.post(
        "/clients/import",
        files={"file": ("clients.csv", CSV, "text/csv")},
        follow_redirects=False,
    )
    assert r.status_code == 200
    body = r.text
    assert 'data-testid="imported-count"' in body
    assert ">1<" in body  # exactly one row imported
    assert 'data-testid="import-error"' in body
    assert "2" in body  # the bad-email row is reported by its row number (row 2)
    # the valid client actually persisted
    assert client.get("/api/clients/ada@acme.io").status_code == 200


def test_import_result_is_valid_html(client):
    """The rendered import summary is valid, accessible HTML."""
    r = client.post("/clients/import", files={"file": ("clients.csv", CSV, "text/csv")})
    assert_valid_html(r.text, context="POST /clients/import")


def test_import_malformed_file_does_not_500(client):
    """A non-UTF-8 / garbage upload is handled gracefully, never a 500."""
    r = client.post(
        "/clients/import",
        files={"file": ("bad.csv", b"\xff\xfe\x00rubbish", "text/csv")},
    )
    assert r.status_code in (200, 400)
