# CRB-9 - Client repository (in-memory CRUD)
Implement ClientRepository in src/fractional_crm/repository.py so every test in tests/test_repository.py passes.
Methods: add(client) [ValueError on duplicate email], get(email) [KeyError if missing], list() [all clients], update(client) [KeyError if missing], delete(email) [KeyError if missing]. Key clients by their email. Do not modify tests.
