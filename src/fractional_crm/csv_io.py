import csv
import io
from typing import List

from fractional_crm.client import Client

_HEADER = ["name", "company", "email", "status", "engagement_type"]


def export_clients_csv(repository) -> str:
    """Serialize every client in the repository to CSV text (header row first)."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(_HEADER)
    for c in repository.list():
        writer.writerow([c.name, c.company, c.email, c.status, c.engagement_type])
    return buf.getvalue()


def import_clients_csv(text: str) -> List[Client]:
    """Parse CSV text into a list of validated Client objects.

    Raises ValueError on a missing/incorrect header, a wrong column count, or any
    value the Client validator rejects.
    """
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("CSV is empty; a header row is required")
    if header != _HEADER:
        raise ValueError(f"invalid header {header!r}; expected {_HEADER!r}")
    clients: List[Client] = []
    for lineno, row in enumerate(reader, start=2):
        if not row:
            continue
        if len(row) != len(_HEADER):
            raise ValueError(f"row {lineno}: expected {len(_HEADER)} columns, got {len(row)}")
        name, company, email, status, engagement_type = row
        clients.append(Client(name=name, company=company, email=email,
                              status=status, engagement_type=engagement_type))
    return clients
