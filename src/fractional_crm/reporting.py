from fractional_crm.engagement import Engagement


def active_engagements(engagements: list[Engagement]) -> list[Engagement]:
    """Return a new list containing only engagements whose .status == "active", preserving input order."""
    return [eng for eng in engagements if eng.status == "active"]


def monthly_run_rate(engagements: list[Engagement]) -> float:
    """Return the sum of .monthly_rate over engagements whose .status == "active". Return 0 when there are no active engagements."""
    return sum(eng.monthly_rate for eng in engagements if eng.status == "active")
