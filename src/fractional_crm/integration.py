import datetime

#: The fixed set of supported providers. Public so the UI can list every provider,
#: connected or not, without re-encoding the list (CRB-33).
PROVIDERS = ("slack", "github", "gitlab", "figma", "intercom", "zendesk")
_ALLOWED_PROVIDERS = PROVIDERS  # retained so existing private references keep working
#: Allowed integration statuses (CRB-33).
STATUSES = ("connected", "disconnected", "error")
_ALLOWED_STATUSES = STATUSES  # retained so existing private references keep working


class Integration:
    """A third-party integration. Timestamps are kept as their original ISO strings."""

    def __init__(self, provider: str, external_id: str, status: str = "connected",
                 last_synced_at: str | None = None) -> None:
        self.provider = self._validate_provider(provider)
        self.external_id = self._validate_external_id(external_id)
        self.status = self._validate_status(status)
        self.last_synced_at = self._validate_ts(last_synced_at) if last_synced_at is not None else None

    @staticmethod
    def _validate_provider(provider: str) -> str:
        if provider not in _ALLOWED_PROVIDERS:
            raise ValueError(f"invalid provider: {provider!r}")
        return provider

    @staticmethod
    def _validate_external_id(external_id: str) -> str:
        stripped = external_id.strip()
        if not stripped:
            raise ValueError("external_id must be non-empty")
        return stripped

    @staticmethod
    def _validate_status(status: str) -> str:
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"invalid status: {status!r}")
        return status

    @staticmethod
    def _validate_ts(ts: str) -> str:
        try:
            datetime.datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            raise ValueError(f"invalid timestamp: {ts!r}")
        return ts

    def mark_synced(self, timestamp: str) -> None:
        validated = self._validate_ts(timestamp)  # raises before any mutation
        self.last_synced_at = validated
        self.status = "connected"

    def disconnect(self) -> None:
        self.status = "disconnected"


class IntegrationRegistry:
    """Registry of integrations keyed by provider (one per provider)."""

    def __init__(self) -> None:
        self._by_provider: dict[str, Integration] = {}

    def connect(self, integration: Integration) -> None:
        if integration.provider in self._by_provider:
            raise ValueError(f"provider {integration.provider!r} is already connected")
        self._by_provider[integration.provider] = integration

    def get(self, provider: str) -> Integration:
        return self._by_provider[provider]

    def list(self) -> list:
        return list(self._by_provider.values())

    def disconnect(self, provider: str) -> None:
        if provider not in self._by_provider:
            raise KeyError(f"provider {provider!r} is not connected")
        self._by_provider[provider].disconnect()
