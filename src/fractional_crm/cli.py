import argparse
import sys

from fractional_crm.client import Client
from fractional_crm.engagement import Engagement
from fractional_crm.sqlite_repository import (SqliteClientRepository,
                                              SqliteEngagementRepository)


def _client_add(args) -> None:
    repo = SqliteClientRepository(args.db)
    try:
        repo.add(Client(name=args.name, company=args.company, email=args.email,
                        status=args.status, engagement_type=args.engagement_type))
    finally:
        repo.close()


def _client_list(args) -> None:
    repo = SqliteClientRepository(args.db)
    try:
        for c in repo.list():
            print(f"{c.email}\t{c.name}\t{c.company}\t{c.status}\t{c.engagement_type}")
    finally:
        repo.close()


def _engagement_add(args) -> None:
    repo = SqliteEngagementRepository(args.db)
    try:
        repo.add(Engagement(client_email=args.client_email, role=args.role,
                            monthly_rate=float(args.monthly_rate), start_date=args.start_date,
                            status=args.status, end_date=args.end_date))
    finally:
        repo.close()


def _engagement_list(args) -> None:
    repo = SqliteEngagementRepository(args.db)
    try:
        for e in repo.list():
            print(f"{e.client_email}\t{e.role}\t{e.monthly_rate}\t{e.start_date}\t{e.end_date or ''}\t{e.status}")
    finally:
        repo.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fractional_crm.cli")
    p.add_argument("--db", required=True, help="path to the SQLite database file")
    entity = p.add_subparsers(dest="entity", required=True)

    client = entity.add_parser("client").add_subparsers(dest="action", required=True)
    ca = client.add_parser("add")
    for opt in ("name", "company", "email", "status", "engagement-type"):
        ca.add_argument(f"--{opt}", required=True)
    ca.set_defaults(func=_client_add)
    client.add_parser("list").set_defaults(func=_client_list)

    eng = entity.add_parser("engagement").add_subparsers(dest="action", required=True)
    ea = eng.add_parser("add")
    for opt in ("client-email", "role", "monthly-rate", "start-date", "status"):
        ea.add_argument(f"--{opt}", required=True)
    ea.add_argument("--end-date", default=None)
    ea.set_defaults(func=_engagement_add)
    eng.add_parser("list").set_defaults(func=_engagement_list)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
