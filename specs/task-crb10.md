# CRB-10 - Engagement model + validation
Implement Engagement in src/fractional_crm/engagement.py so every test in tests/test_engagement.py passes.
Fields: client_email, role (coo/cpo/advisor), monthly_rate (must be > 0, int or float), start_date (ISO date string YYYY-MM-DD), end_date (optional ISO date or None; if present must be >= start_date), status (proposed/active/completed/cancelled).
Validate all fields; raise ValueError on any invalid input. Validate dates with datetime.date.fromisoformat. Validate client_email as a basic address. Do not modify tests.
