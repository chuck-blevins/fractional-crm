import pytest

from fractional_crm.integration import Integration, IntegrationRegistry


# --- Integration construction & validation ---------------------------------

def test_valid_integration_stores_fields_with_defaults():
    i = Integration(provider="slack", external_id="T012AB3CD")
    assert i.provider == "slack"
    assert i.external_id == "T012AB3CD"
    assert i.status == "connected"          # default
    assert i.last_synced_at is None         # default


def test_external_id_is_stripped():
    i = Integration(provider="github", external_id="  chuck/fractional-crm  ")
    assert i.external_id == "chuck/fractional-crm"


def test_all_allowed_providers_accepted():
    for provider in ("slack", "github", "gitlab", "figma", "intercom", "zendesk"):
        assert Integration(provider=provider, external_id="x").provider == provider


def test_invalid_provider_rejected():
    with pytest.raises(ValueError):
        Integration(provider="dropbox", external_id="x")


def test_empty_external_id_rejected():
    with pytest.raises(ValueError):
        Integration(provider="slack", external_id="   ")


def test_invalid_status_rejected():
    with pytest.raises(ValueError):
        Integration(provider="slack", external_id="x", status="pending")


def test_all_allowed_statuses_accepted():
    for status in ("connected", "disconnected", "error"):
        assert Integration(provider="slack", external_id="x", status=status).status == status


# --- last_synced_at: ISO datetime string, stored verbatim ------------------

def test_last_synced_at_stored_as_original_string():
    i = Integration(provider="slack", external_id="x",
                    last_synced_at="2026-07-11T09:30:00")
    assert i.last_synced_at == "2026-07-11T09:30:00"
    assert isinstance(i.last_synced_at, str)


def test_last_synced_at_accepts_plain_iso_date():
    i = Integration(provider="slack", external_id="x", last_synced_at="2026-07-11")
    assert i.last_synced_at == "2026-07-11"


def test_invalid_last_synced_at_rejected():
    with pytest.raises(ValueError):
        Integration(provider="slack", external_id="x", last_synced_at="not-a-timestamp")


# --- behaviours -------------------------------------------------------------

def test_mark_synced_sets_timestamp_and_status():
    i = Integration(provider="slack", external_id="x", status="error")
    i.mark_synced("2026-07-11T12:00:00")
    assert i.last_synced_at == "2026-07-11T12:00:00"   # original string preserved
    assert i.status == "connected"


def test_mark_synced_rejects_invalid_timestamp():
    i = Integration(provider="slack", external_id="x")
    with pytest.raises(ValueError):
        i.mark_synced("yesterday")
    assert i.last_synced_at is None                     # unchanged on failure


def test_disconnect_sets_status():
    i = Integration(provider="slack", external_id="x")
    i.disconnect()
    assert i.status == "disconnected"


# --- IntegrationRegistry ----------------------------------------------------

def test_connect_and_get():
    reg = IntegrationRegistry()
    i = Integration(provider="github", external_id="chuck/fractional-crm")
    reg.connect(i)
    assert reg.get("github") is i


def test_connect_duplicate_provider_rejected():
    reg = IntegrationRegistry()
    reg.connect(Integration(provider="slack", external_id="a"))
    with pytest.raises(ValueError):
        reg.connect(Integration(provider="slack", external_id="b"))


def test_get_missing_provider_raises_keyerror():
    reg = IntegrationRegistry()
    with pytest.raises(KeyError):
        reg.get("figma")


def test_list_returns_all_in_insertion_order():
    reg = IntegrationRegistry()
    a = Integration(provider="slack", external_id="a")
    b = Integration(provider="github", external_id="b")
    reg.connect(a)
    reg.connect(b)
    assert reg.list() == [a, b]


def test_registry_disconnect_marks_integration_disconnected():
    reg = IntegrationRegistry()
    i = Integration(provider="slack", external_id="a")
    reg.connect(i)
    reg.disconnect("slack")
    assert reg.get("slack").status == "disconnected"


def test_registry_disconnect_missing_raises_keyerror():
    reg = IntegrationRegistry()
    with pytest.raises(KeyError):
        reg.disconnect("slack")
