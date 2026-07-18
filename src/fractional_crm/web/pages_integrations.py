"""Integrations UI: provider list with connect, disconnect, and sync-now actions."""
import datetime

from fastapi import APIRouter

router = APIRouter(prefix="/integrations")


def now_iso() -> str:
    """Return the current local time as an ISO-8601 string.

    A seam, not a convenience: the JSON API takes a caller-supplied timestamp, but a
    "sync now" button must stamp server-side. Tests replace this to pin the clock.
    """
    return datetime.datetime.now().isoformat(timespec="seconds")
