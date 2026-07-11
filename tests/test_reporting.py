import pytest
from fractional_crm.engagement import Engagement
from fractional_crm.reporting import active_engagements, monthly_run_rate


def _e(status="active", monthly_rate=10000, client_email="a@b.co"):
    return Engagement(client_email=client_email, role="cpo",
                      monthly_rate=monthly_rate, start_date="2026-01-01",
                      end_date=None, status=status)


def test_active_engagements_filters_by_status():
    active = _e(status="active", client_email="a@b.co")
    proposed = _e(status="proposed", client_email="b@b.co")
    completed = _e(status="completed", client_email="c@b.co")
    cancelled = _e(status="cancelled", client_email="d@b.co")
    result = active_engagements([active, proposed, completed, cancelled])
    assert result == [active]


def test_active_engagements_returns_all_active_preserving_order():
    a1 = _e(status="active", client_email="a@b.co")
    a2 = _e(status="active", client_email="b@b.co")
    p = _e(status="proposed", client_email="c@b.co")
    a3 = _e(status="active", client_email="d@b.co")
    assert active_engagements([a1, a2, p, a3]) == [a1, a2, a3]


def test_active_engagements_empty_list():
    assert active_engagements([]) == []


def test_active_engagements_none_active():
    assert active_engagements([_e(status="proposed"), _e(status="completed")]) == []


def test_active_engagements_returns_list():
    assert isinstance(active_engagements([_e()]), list)


def test_monthly_run_rate_sums_active_only():
    engagements = [
        _e(status="active", monthly_rate=10000, client_email="a@b.co"),
        _e(status="active", monthly_rate=15000, client_email="b@b.co"),
        _e(status="proposed", monthly_rate=99999, client_email="c@b.co"),
        _e(status="completed", monthly_rate=88888, client_email="d@b.co"),
        _e(status="cancelled", monthly_rate=77777, client_email="e@b.co"),
    ]
    assert monthly_run_rate(engagements) == 25000


def test_monthly_run_rate_empty_is_zero():
    assert monthly_run_rate([]) == 0


def test_monthly_run_rate_no_active_is_zero():
    assert monthly_run_rate([_e(status="proposed"), _e(status="cancelled")]) == 0


def test_monthly_run_rate_accepts_floats():
    engagements = [
        _e(status="active", monthly_rate=9999.99, client_email="a@b.co"),
        _e(status="active", monthly_rate=0.01, client_email="b@b.co"),
    ]
    assert monthly_run_rate(engagements) == pytest.approx(10000.0)


def test_monthly_run_rate_single_active():
    assert monthly_run_rate([_e(status="active", monthly_rate=12500)]) == 12500
