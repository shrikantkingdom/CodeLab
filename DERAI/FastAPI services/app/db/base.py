"""Abstract base class for database connectors."""

from abc import ABC, abstractmethod
from typing import Any


class DBConnector(ABC):
    """Base interface for database access.

    Implement this class to add a new database backend.
    Register in DBFactory.
    """

    @abstractmethod
    async def fetch_record(
        self,
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Fetch a document record from the database.

        Args:
            account_office: 3-digit office code.
            account_number: 6-digit account number.
            params: Additional query params (date range, types, etc.).

        Returns:
            Dictionary of field names to values.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        ...
