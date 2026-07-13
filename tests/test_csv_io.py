import pytest

from fractional_crm.client import Client
from fractional_crm.repository import ClientRepository
from fractional_crm.csv_io import export_clients_csv, import_clients_csv

HEADER = "name,company,email,status,engagement_type"


def _c(name="Ann", company="Acme", email="a@b.co", status="active", engagement_type="coo"):
    return Client(name=name, company=company, email=email, status=status,
                  engagement_type=engagement_type)


def _fields(c):
    return (c.name, c.company, c.email, c.status, c.engagement_type)


def _repo(clients):
    r = ClientRepository()
    for c in clients:
        r.add(c)
    return r


def test_export_returns_str_with_header_first():
    text = export_clients_csv(_repo([_c()]))
    assert isinstance(text, str)
    assert text.splitlines()[0] == HEADER


def test_export_empty_repo_is_header_only():
    assert export_clients_csv(ClientRepository()).splitlines() == [HEADER]


def test_export_one_row_per_client():
    r = _repo([_c(email="a@b.co"), _c(email="c@d.co")])
    assert len(export_clients_csv(r).splitlines()) == 3  # header + 2 rows


def test_import_returns_list_of_clients():
    clients = import_clients_csv(export_clients_csv(_repo([_c()])))
    assert isinstance(clients, list)
    assert len(clients) == 1
    assert isinstance(clients[0], Client)


def test_import_empty_repo_export_returns_empty_list():
    assert import_clients_csv(export_clients_csv(ClientRepository())) == []


def test_roundtrip_preserves_fields_and_order():
    originals = [
        _c(name="Ann", company="Acme", email="a@b.co", status="active", engagement_type="coo"),
        _c(name="Bob", company="Beta", email="b@c.co", status="prospect", engagement_type="advisor"),
        _c(name="Cy", company="Gamma", email="c@d.co", status="paused", engagement_type="cpo"),
    ]
    imported = import_clients_csv(export_clients_csv(_repo(originals)))
    assert [_fields(c) for c in imported] == [_fields(c) for c in originals]


def test_roundtrip_preserves_field_with_comma():
    imported = import_clients_csv(export_clients_csv(_repo([_c(company="Acme, Inc.")])))
    assert imported[0].company == "Acme, Inc."


def test_roundtrip_stable_double_export():
    r = _repo([_c(name="Ann", company="Acme, Inc.", email="a@b.co"), _c(email="c@d.co")])
    once = export_clients_csv(r)
    twice = export_clients_csv(_repo(import_clients_csv(once)))
    assert once == twice


def test_import_too_few_columns_raises():
    text = HEADER + "\nAnn,Acme,a@b.co,active\n"
    with pytest.raises(ValueError):
        import_clients_csv(text)


def test_import_too_many_columns_raises():
    text = HEADER + "\nAnn,Acme,a@b.co,active,coo,extra\n"
    with pytest.raises(ValueError):
        import_clients_csv(text)


def test_import_invalid_email_raises():
    text = HEADER + "\nAnn,Acme,not-an-email,active,coo\n"
    with pytest.raises(ValueError):
        import_clients_csv(text)


def test_import_invalid_status_raises():
    text = HEADER + "\nAnn,Acme,a@b.co,bogus,coo\n"
    with pytest.raises(ValueError):
        import_clients_csv(text)


def test_import_invalid_engagement_type_raises():
    text = HEADER + "\nAnn,Acme,a@b.co,active,bogus\n"
    with pytest.raises(ValueError):
        import_clients_csv(text)


def test_import_wrong_header_raises():
    text = "wrong,header,cols,x,y\nAnn,Acme,a@b.co,active,coo\n"
    with pytest.raises(ValueError):
        import_clients_csv(text)


def test_import_missing_header_empty_text_raises():
    with pytest.raises(ValueError):
        import_clients_csv("")
