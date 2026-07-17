"""Engagements UI: accessible list (filterable by client) + create/edit forms.

STUB — not yet implemented. Behaviour is specified by specs/task-crb31.md and pinned by
tests/web/test_engagements_ui.py. The router is empty so the app still builds and the
existing suite stays green; only the CRB-31 tests are red.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/engagements")
