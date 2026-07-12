from typing import List, Dict
import csv
import json

class ImportResult:
    """Holds the outcome of an import."""
    
    def __init__(self, imported: List = None, errors: List = None):
        self.imported = imported if imported is not None else []
        self.errors = errors if errors is not None else []

class ClientImporter:
    """Imports client data into a repository."""
    
    def __init__(self, repository):
        self._repository = repository
    
    def _import_rows(self, rows) -> ImportResult:
        imported = []
        errors = []
        for index, row in enumerate(rows, start=1):
            try:
                client = Client(name=row["name"], company=row["company"], email=row["email"], status=row["status"], engagement_type=row["engagement_type"])
                self._repository.add(client)
                imported.append(client)
            except (ValueError, KeyError, TypeError) as exc:
                errors.append({"row": index, "error": str(exc)})
        return ImportResult(imported, errors)
    
    def import_csv(self, text: str) -> ImportResult:
        """Imports client data from CSV text."""
        reader = csv.DictReader(io.StringIO(text))
        return self._import_rows(reader)
    
    def import_json(self, text: str) -> ImportResult:
        """Imports client data from JSON text."""
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("Invalid JSON format")
        return self._import_rows(data)
