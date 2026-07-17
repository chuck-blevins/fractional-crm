"""Repo-wide test configuration.

Marks the whole suite as a NON-production run before any test builds the app.

``fractional_crm.web.auth`` fails secure: an unset ``CRM_ENV`` counts as production, which
would (a) make ``CRM_SESSION_SECRET`` mandatory and (b) issue the session cookie with the
Secure flag — which TestClient's plaintext http:// transport would silently drop, logging
every authenticated test out. Declaring the environment here keeps that fail-secure default
intact in production while letting the suite run unconfigured.
"""
import os

os.environ.setdefault("CRM_ENV", "test")
