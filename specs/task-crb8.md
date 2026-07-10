# CRB-8 - Client domain model + validation
Implement `Client` in src/fractional_crm/client.py so every test in tests/test_client.py passes.
Fields: name, company, email, status (prospect/active/paused/closed), engagement_type (coo/cpo/advisor).
Validate: non-empty stripped name; valid email (local@domain.tld); status and engagement_type from allowed sets. Raise ValueError on invalid. Do not modify tests.
