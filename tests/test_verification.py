import pytest

from fractional_crm.client import Client
from fractional_crm.verification import EmailVerification


def _client(email="ada@analytical.io"):
    return Client(name="Ada Lovelace", company="Analytical Engines",
                  email=email, status="active", engagement_type="cpo")


def test_new_client_is_unverified():
    v = EmailVerification()
    assert v.is_verified(_client()) is False


def test_request_returns_nonempty_token():
    v = EmailVerification()
    token = v.request(_client())
    assert isinstance(token, str)
    assert token != ""


def test_request_returns_unique_tokens_per_client():
    v = EmailVerification()
    t1 = v.request(_client("a@b.co"))
    t2 = v.request(_client("c@d.co"))
    assert t1 != t2


def test_verify_with_correct_token_marks_verified():
    v = EmailVerification()
    c = _client()
    token = v.request(c)
    assert v.is_verified(c) is False
    result = v.verify(c, token)
    assert result is True
    assert v.is_verified(c) is True


def test_verify_wrong_token_raises_and_stays_unverified():
    v = EmailVerification()
    c = _client()
    v.request(c)
    with pytest.raises(ValueError):
        v.verify(c, "definitely-not-the-token")
    assert v.is_verified(c) is False


def test_verify_without_request_raises_keyerror():
    v = EmailVerification()
    with pytest.raises(KeyError):
        v.verify(_client("nobody@nowhere.io"), "anything")


def test_verification_is_per_client():
    v = EmailVerification()
    a = _client("a@b.co")
    b = _client("c@d.co")
    token = v.request(a)
    v.request(b)
    v.verify(a, token)
    assert v.is_verified(a) is True
    assert v.is_verified(b) is False


def test_token_is_single_use():
    v = EmailVerification()
    c = _client()
    token = v.request(c)
    v.verify(c, token)
    # once consumed, the pending request is gone
    with pytest.raises(KeyError):
        v.verify(c, token)


def test_require_verified_raises_when_unverified():
    v = EmailVerification()
    with pytest.raises(ValueError):
        v.require_verified(_client())


def test_require_verified_passes_when_verified():
    v = EmailVerification()
    c = _client()
    token = v.request(c)
    v.verify(c, token)
    assert v.require_verified(c) is None
