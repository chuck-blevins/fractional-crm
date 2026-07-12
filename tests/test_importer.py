import json

import pytest

from fractional_crm.client import Client
from fractional_crm.repository import ClientRepository
from fractional_crm.importer import ClientImporter, ImportResult


VALID_CSV = """name,company,email,status,engagement_type
Ada Lovelace,Analytical Engines,ada@analytical.example,active,cpo
Alan Turing,Bletchley,alan@bletchley.example,prospect,advisor
"""


def _make():
    """Return a fresh (importer, repository) pair."""
    repo = ClientRepository()
    return ClientImporter(repo), repo


def test_import_csv_adds_all_valid_clients_to_repository():
    importer, repo = _make()
    result = importer.import_csv(VALID_CSV)

    assert isinstance(result, ImportResult)
    assert len(result.imported) == 2
    assert result.errors == []

    # every imported item is a real Client
    assert all(isinstance(c, Client) for c in result.imported)
    assert {c.email for c in result.imported} == {
        "ada@analytical.example",
        "alan@bletchley.example",
    }

    # and the repository now holds them, keyed by email
    ada = repo.get("ada@analytical.example")
    assert ada.name == "Ada Lovelace"
    assert ada.company == "Analytical Engines"
    assert ada.status == "active"
    assert ada.engagement_type == "cpo"
    assert len(repo.list()) == 2


def test_import_csv_skips_invalid_rows_and_reports_them():
    importer, repo = _make()
    csv_text = (
        "name,company,email,status,engagement_type\n"
        "Good One,Co,good@example.com,active,coo\n"      # row 1 - valid
        "Bad Email,Co,not-an-email,active,coo\n"          # row 2 - bad email
        ",Co,valid@example.com,active,coo\n"              # row 3 - empty name
        "Bad Status,Co,status@example.com,frozen,coo\n"   # row 4 - bad status
    )
    result = importer.import_csv(csv_text)

    # only the first data row is valid
    assert len(result.imported) == 1
    assert result.imported[0].email == "good@example.com"
    assert len(repo.list()) == 1

    # the three bad rows are reported with their 1-based data-row number
    assert len(result.errors) == 3
    assert {e["row"] for e in result.errors} == {2, 3, 4}
    assert all(e["error"] for e in result.errors)  # every error has a message

    # invalid rows never make it into the repository
    with pytest.raises(KeyError):
        repo.get("not-an-email")


def test_import_csv_reports_duplicate_email_as_error_keeping_first():
    importer, repo = _make()
    csv_text = (
        "name,company,email,status,engagement_type\n"
        "First,Co,dup@example.com,active,coo\n"
        "Second,Co,dup@example.com,prospect,advisor\n"
    )
    result = importer.import_csv(csv_text)

    assert len(result.imported) == 1
    assert len(result.errors) == 1
    assert result.errors[0]["row"] == 2
    # first write wins; the duplicate is rejected
    assert repo.get("dup@example.com").name == "First"


def test_import_json_adds_valid_clients():
    importer, repo = _make()
    payload = json.dumps(
        [
            {
                "name": "Grace Hopper",
                "company": "Navy",
                "email": "grace@navy.example",
                "status": "active",
                "engagement_type": "advisor",
            }
        ]
    )
    result = importer.import_json(payload)

    assert isinstance(result, ImportResult)
    assert len(result.imported) == 1
    assert result.errors == []
    assert repo.get("grace@navy.example").name == "Grace Hopper"


def test_import_json_reports_invalid_row():
    importer, repo = _make()
    payload = json.dumps(
        [
            {"name": "Ok", "company": "Co", "email": "ok@example.com",
             "status": "active", "engagement_type": "coo"},
            {"name": "Bad", "company": "Co", "email": "bad",
             "status": "active", "engagement_type": "coo"},
        ]
    )
    result = importer.import_json(payload)

    assert len(result.imported) == 1
    assert len(result.errors) == 1
    assert result.errors[0]["row"] == 2
    assert len(repo.list()) == 1


def test_import_json_missing_field_is_reported_not_raised():
    importer, repo = _make()
    payload = json.dumps(
        [
            # engagement_type is missing entirely
            {"name": "Missing Type", "company": "Co",
             "email": "mt@example.com", "status": "active"},
        ]
    )
    result = importer.import_json(payload)

    assert len(result.imported) == 0
    assert len(result.errors) == 1
    assert result.errors[0]["row"] == 1
    assert len(repo.list()) == 0


def test_import_json_rejects_non_list_payload():
    importer, _ = _make()
    with pytest.raises(ValueError):
        importer.import_json(json.dumps({"name": "not in a list"}))
