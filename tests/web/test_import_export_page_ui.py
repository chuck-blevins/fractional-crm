"""CRB-41 acceptance: the dedicated /import-export page.

Reuses the existing CSV endpoints — the export link (/api/clients/csv/export) and the
/clients/import upload handler. This page just gives them a home off the nav, closing the
dead Import/Export nav link found during the 2026-07-21 go-live sweep.
"""
from htmlcheck import assert_valid_html


def test_page_ok(client):
    assert client.get("/import-export").status_code == 200


def test_has_export_link(client):
    html = client.get("/import-export").text
    assert "/api/clients/csv/export" in html


def test_has_accessible_import_form(client):
    html = client.get("/import-export").text
    assert 'action="/clients/import"' in html
    assert 'enctype="multipart/form-data"' in html
    assert 'method="post"' in html
    assert 'type="file"' in html
    assert 'name="file"' in html
    assert "<label" in html


def test_valid_html(client):
    assert_valid_html(client.get("/import-export").text, context="GET /import-export")
