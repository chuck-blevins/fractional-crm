"""CRB-40: SqliteInteractionRepository.list_all() — every interaction, newest first."""
from fractional_crm.interaction import Interaction
from fractional_crm.sqlite_interaction_repository import SqliteInteractionRepository


def test_list_all_empty():
    repo = SqliteInteractionRepository(":memory:")
    assert repo.list_all() == []


def test_list_all_returns_every_client_newest_first():
    repo = SqliteInteractionRepository(":memory:")
    # Insert out of date order and across three clients.
    repo.add(Interaction("ada@acme.io", "2026-01-01", "note", "OLD"))
    repo.add(Interaction("bob@beta.io", "2026-06-01", "email", "NEW"))
    repo.add(Interaction("cy@gamma.io", "2026-03-01", "call", "MID"))
    got = repo.list_all()
    # Newest first, regardless of client.
    assert [i.summary for i in got] == ["NEW", "MID", "OLD"]
    assert {i.client_email for i in got} == {"ada@acme.io", "bob@beta.io", "cy@gamma.io"}
