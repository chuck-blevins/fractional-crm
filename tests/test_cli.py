"""Smoke tests for the argparse CLI (CRB-16).

The CLI is a thin wrapper over the domain models and the SQLite repositories.
Every case drives the real ``python -m fractional_crm.cli`` entry point as a
subprocess against a temp SQLite file, so persistence and validation are
exercised end to end.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def run_cli(db, *args):
    """Invoke the CLI as a subprocess against the given SQLite db file."""
    cmd = [sys.executable, "-m", "fractional_crm.cli", "--db", str(db), *args]
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    return subprocess.run(
        cmd, cwd=str(ROOT), env=env, capture_output=True, text=True
    )


def add_client(db, email="ceo@acme.io", name="Ada Lovelace",
               company="Acme", status="active", engagement_type="coo"):
    return run_cli(
        db, "client", "add",
        "--name", name, "--company", company, "--email", email,
        "--status", status, "--engagement-type", engagement_type,
    )


def add_engagement(db, client_email="ceo@acme.io", role="coo",
                   monthly_rate="5000", start_date="2026-01-01",
                   status="active", end_date=None):
    args = [
        "engagement", "add",
        "--client-email", client_email, "--role", role,
        "--monthly-rate", monthly_rate, "--start-date", start_date,
        "--status", status,
    ]
    if end_date is not None:
        args += ["--end-date", end_date]
    return run_cli(db, *args)


def test_client_add_succeeds(tmp_path):
    r = add_client(tmp_path / "crm.db")
    assert r.returncode == 0, r.stderr


def test_client_add_then_list(tmp_path):
    db = tmp_path / "crm.db"
    assert add_client(db).returncode == 0
    r = run_cli(db, "client", "list")
    assert r.returncode == 0, r.stderr
    assert "ceo@acme.io" in r.stdout
    assert "Ada Lovelace" in r.stdout


def test_client_list_empty_is_clean(tmp_path):
    r = run_cli(tmp_path / "crm.db", "client", "list")
    assert r.returncode == 0, r.stderr
    assert "ceo@acme.io" not in r.stdout


def test_client_persists_to_a_fresh_process(tmp_path):
    db = tmp_path / "crm.db"
    assert add_client(db).returncode == 0
    # A brand-new process must read the row back -> real SQLite persistence.
    r = run_cli(db, "client", "list")
    assert "ceo@acme.io" in r.stdout


def test_duplicate_client_is_rejected(tmp_path):
    db = tmp_path / "crm.db"
    assert add_client(db).returncode == 0
    assert add_client(db).returncode != 0


def test_invalid_client_email_is_rejected(tmp_path):
    # Email cannot be an argparse choice: the domain validator must run.
    r = add_client(tmp_path / "crm.db", email="not-an-email")
    assert r.returncode != 0


def test_engagement_add_then_list(tmp_path):
    db = tmp_path / "crm.db"
    assert add_engagement(db).returncode == 0
    r = run_cli(db, "engagement", "list")
    assert r.returncode == 0, r.stderr
    assert "ceo@acme.io" in r.stdout
    assert "coo" in r.stdout


def test_engagement_end_date_preserved(tmp_path):
    db = tmp_path / "crm.db"
    r = add_engagement(
        db, client_email="cto@acme.io", role="advisor",
        monthly_rate="3000", end_date="2026-06-30",
    )
    assert r.returncode == 0, r.stderr
    r2 = run_cli(db, "engagement", "list")
    assert "2026-06-30" in r2.stdout


def test_invalid_engagement_role_is_rejected(tmp_path):
    r = add_engagement(tmp_path / "crm.db", role="wizard")
    assert r.returncode != 0
