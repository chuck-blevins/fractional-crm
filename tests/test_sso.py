"""Acceptance tests for Gmail (Google) SSO integration.

CRB-7: link a Google account (subject id) to a Client whose email is a Gmail
address, then authenticate the client against a signed SSO assertion token
(HMAC-SHA256 over the token body, mirroring an IdP-issued/verified assertion).
"""
import base64
import json

import pytest

from fractional_crm.client import Client
from fractional_crm.sso import GmailSSO


def make_client(email: str = "ada@gmail.com", status: str = "active",
                engagement_type: str = "coo") -> Client:
    return Client("Ada Lovelace", "Acme", email, status, engagement_type)


# ---- construction ---------------------------------------------------------

def test_empty_secret_rejected():
    with pytest.raises(ValueError):
        GmailSSO("")


# ---- linking --------------------------------------------------------------

def test_link_gmail_client():
    sso = GmailSSO("app-secret")
    client = make_client()
    assert sso.is_linked(client) is False
    sso.link(client, "google-sub-123")
    assert sso.is_linked(client) is True


def test_link_non_gmail_email_rejected():
    sso = GmailSSO("app-secret")
    client = make_client(email="ada@corp.com")
    with pytest.raises(ValueError):
        sso.link(client, "google-sub-123")


def test_link_empty_google_id_rejected():
    sso = GmailSSO("app-secret")
    client = make_client()
    with pytest.raises(ValueError):
        sso.link(client, "")


def test_same_google_id_cannot_link_two_clients():
    sso = GmailSSO("app-secret")
    a = make_client(email="ada@gmail.com")
    b = make_client(email="bob@gmail.com", status="prospect", engagement_type="cpo")
    sso.link(a, "google-sub-123")
    with pytest.raises(ValueError):
        sso.link(b, "google-sub-123")


def test_unlink():
    sso = GmailSSO("app-secret")
    client = make_client()
    sso.link(client, "google-sub-123")
    sso.unlink(client)
    assert sso.is_linked(client) is False


def test_unlink_when_not_linked_raises_keyerror():
    sso = GmailSSO("app-secret")
    with pytest.raises(KeyError):
        sso.unlink(make_client())


# ---- authentication -------------------------------------------------------

def test_authenticate_valid_token():
    sso = GmailSSO("app-secret")
    client = make_client()
    sso.link(client, "google-sub-123")
    token = sso.create_token("google-sub-123", "ada@gmail.com")
    assert sso.authenticate(client, token) is True


def test_authenticate_not_linked_raises_keyerror():
    sso = GmailSSO("app-secret")
    client = make_client()
    token = sso.create_token("google-sub-123", "ada@gmail.com")
    with pytest.raises(KeyError):
        sso.authenticate(client, token)


def test_authenticate_wrong_google_id_returns_false():
    sso = GmailSSO("app-secret")
    client = make_client()
    sso.link(client, "google-sub-123")
    # validly signed token, but for a different Google subject
    token = sso.create_token("google-sub-999", "ada@gmail.com")
    assert sso.authenticate(client, token) is False


def test_authenticate_email_mismatch_returns_false():
    sso = GmailSSO("app-secret")
    client = make_client()
    sso.link(client, "google-sub-123")
    # validly signed token for the linked subject, but a different email
    token = sso.create_token("google-sub-123", "bob@gmail.com")
    assert sso.authenticate(client, token) is False


def test_authenticate_tampered_token_raises_valueerror():
    sso = GmailSSO("app-secret")
    client = make_client()
    sso.link(client, "google-sub-123")
    token = sso.create_token("google-sub-123", "ada@gmail.com")
    body, sig = token.split(".")
    forged = json.dumps({"google_id": "google-sub-123", "email": "attacker@gmail.com"},
                        sort_keys=True)
    forged_body = base64.urlsafe_b64encode(forged.encode()).decode()
    tampered = f"{forged_body}.{sig}"
    with pytest.raises(ValueError):
        sso.authenticate(client, tampered)


def test_authenticate_wrong_secret_raises_valueerror():
    issuer = GmailSSO("attacker-secret")
    verifier = GmailSSO("app-secret")
    client = make_client()
    verifier.link(client, "google-sub-123")
    token = issuer.create_token("google-sub-123", "ada@gmail.com")
    with pytest.raises(ValueError):
        verifier.authenticate(client, token)


def test_authenticate_malformed_token_raises_valueerror():
    sso = GmailSSO("app-secret")
    client = make_client()
    sso.link(client, "google-sub-123")
    with pytest.raises(ValueError):
        sso.authenticate(client, "not-a-valid-token")
