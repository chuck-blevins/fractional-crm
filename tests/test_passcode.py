import pytest

from fractional_crm.client import Client
from fractional_crm.passcode import PasscodeAuth


def _client(email="ada@analytical.io"):
    return Client(name="Ada Lovelace", company="Analytical Engines",
                  email=email, status="active", engagement_type="cpo")


def _all_stored_strings(obj, acc=None):
    """Recursively collect every str found in obj's attribute/collection graph."""
    if acc is None:
        acc = []
    if isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _all_stored_strings(k, acc)
            _all_stored_strings(v, acc)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            _all_stored_strings(v, acc)
    elif hasattr(obj, "__dict__"):
        _all_stored_strings(vars(obj), acc)
    return acc


# --- optional: a new client has no passcode ---

def test_new_client_has_no_passcode():
    a = PasscodeAuth()
    assert a.has_passcode(_client()) is False


def test_authenticate_without_passcode_raises_keyerror():
    a = PasscodeAuth()
    with pytest.raises(KeyError):
        a.authenticate(_client(), "1234")


# --- enrolling / authenticating ---

def test_set_passcode_marks_enrolled():
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, "824617")
    assert a.has_passcode(c) is True


def test_authenticate_with_correct_passcode_returns_true():
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, "824617")
    assert a.authenticate(c, "824617") is True


def test_authenticate_with_wrong_passcode_returns_false():
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, "824617")
    assert a.authenticate(c, "000000") is False


def test_wrong_passcode_leaves_client_enrolled():
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, "824617")
    a.authenticate(c, "000000")
    assert a.has_passcode(c) is True
    assert a.authenticate(c, "824617") is True


# --- per-client isolation ---

def test_passcode_is_per_client():
    a = PasscodeAuth()
    x = _client("x@b.co")
    y = _client("y@d.co")
    a.set_passcode(x, "111111")
    assert a.has_passcode(y) is False
    with pytest.raises(KeyError):
        a.authenticate(y, "111111")


def test_same_passcode_authenticates_only_matching_client():
    a = PasscodeAuth()
    x = _client("x@b.co")
    y = _client("y@d.co")
    a.set_passcode(x, "424242")
    a.set_passcode(y, "424242")
    assert a.authenticate(x, "424242") is True
    assert a.authenticate(y, "424242") is True


# --- update / clear (opt out) ---

def test_set_passcode_replaces_previous():
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, "111111")
    a.set_passcode(c, "222222")
    assert a.authenticate(c, "111111") is False
    assert a.authenticate(c, "222222") is True


def test_clear_passcode_removes_enrollment():
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, "824617")
    a.clear_passcode(c)
    assert a.has_passcode(c) is False
    with pytest.raises(KeyError):
        a.authenticate(c, "824617")


def test_clear_passcode_without_enrollment_raises_keyerror():
    a = PasscodeAuth()
    with pytest.raises(KeyError):
        a.clear_passcode(_client())


# --- validation: 4-8 digit numeric only ---

@pytest.mark.parametrize("bad", ["", "123", "abc", "12ab", "12 34", "123456789", "1234.5"])
def test_set_passcode_rejects_invalid(bad):
    a = PasscodeAuth()
    with pytest.raises(ValueError):
        a.set_passcode(_client(), bad)


@pytest.mark.parametrize("good", ["1234", "00000", "12345678"])
def test_set_passcode_accepts_valid_lengths(good):
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, good)
    assert a.authenticate(c, good) is True


def test_invalid_passcode_does_not_enroll():
    a = PasscodeAuth()
    c = _client()
    with pytest.raises(ValueError):
        a.set_passcode(c, "12")
    assert a.has_passcode(c) is False


# --- security: passcode is not stored in plaintext ---

def test_passcode_not_stored_in_plaintext():
    a = PasscodeAuth()
    c = _client()
    a.set_passcode(c, "824617")
    assert "824617" not in _all_stored_strings(a)
