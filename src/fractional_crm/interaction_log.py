from typing import List
from fractional_crm.interaction import Interaction

class InteractionLog:
    """In-memory interaction log repository."""

    def __init__(self) -> None:
        self._interactions: List[Interaction] = []

    def add(self, interaction: Interaction) -> None:
        """Add an interaction to the log. Returns None."""
        self._interactions.append(interaction)

    def list_for_client(self, client_email: str) -> List[Interaction]:
        """Return interactions for a specific client, sorted by date DESCENDING."""
        return sorted(
            (i for i in self._interactions if i.client_email == client_email),
            key=lambda x: x.date,
            reverse=True
        )
