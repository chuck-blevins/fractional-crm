import pytest
from fractional_crm.engagement import Engagement


def _e(**kw):
    d = dict(client_email="a@b.co", role="cpo", monthly_rate=10000,
             start_date="2026-01-01", end_date=None, status="active")
    d.update(kw)
    return Engagement(**d)


def test_valid():
    e = _e()
    assert e.client_email == "a@b.co"
    assert e.role == "cpo"
    assert e.monthly_rate == 10000
    assert e.start_date == "2026-01-01"
    assert e.end_date is None
    assert e.status == "active"


def test_valid_with_end_date():
    assert _e(end_date="2026-06-01").end_date == "2026-06-01"


def test_allowed_roles():
    for r in ["coo", "cpo", "advisor"]:
        assert _e(role=r).role == r


def test_invalid_role_rejected():
    with pytest.raises(ValueError):
        _e(role="ceo")


def test_allowed_statuses():
    for s in ["proposed", "active", "completed", "cancelled"]:
        assert _e(status=s).status == s


def test_invalid_status_rejected():
    with pytest.raises(ValueError):
        _e(status="pending")


def test_monthly_rate_must_be_positive():
    for bad in [0, -1, -100.5]:
        with pytest.raises(ValueError):
            _e(monthly_rate=bad)


def test_monthly_rate_accepts_float():
    assert _e(monthly_rate=9999.99).monthly_rate == 9999.99


def test_invalid_email_rejected():
    with pytest.raises(ValueError):
        _e(client_email="bad-email")


def test_invalid_start_date_rejected():
    for bad in ["not-a-date", "2026-13-01", "2026-01-32", ""]:
        with pytest.raises(ValueError):
            _e(start_date=bad)


def test_end_date_before_start_rejected():
    with pytest.raises(ValueError):
        _e(start_date="2026-06-01", end_date="2026-01-01")


def test_end_date_equal_start_ok():
    assert _e(start_date="2026-06-01", end_date="2026-06-01").end_date == "2026-06-01"
