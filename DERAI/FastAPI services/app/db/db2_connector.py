"""DB2 database connector for letters and confirms records."""

import logging
from typing import Any

from app.config import settings
from app.db.base import DBConnector

logger = logging.getLogger(__name__)


class DB2Connector(DBConnector):
    """Connects to DB2 to fetch letter and confirm data.

    Uses mock data when DB2 credentials are not configured.
    """

    async def fetch_record(
        self,
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if not settings.db2_host:
            logger.info("DB2 not configured — returning mock data")
            return self._mock_record(account_office, account_number, params)

        return await self._query_db2(account_office, account_number, params)

    async def _query_db2(
        self,
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute actual DB2 query."""
        import ibm_db  # optional dependency

        conn_str = (
            f"DATABASE={settings.db2_database};"
            f"HOSTNAME={settings.db2_host};"
            f"PORT={settings.db2_port};"
            f"PROTOCOL=TCPIP;"
            f"UID={settings.db2_user};"
            f"PWD={settings.db2_password};"
        )
        conn = ibm_db.connect(conn_str, "", "")
        try:
            doc_type = params.get("document_type", "letter")
            table = "letters" if doc_type == "letter" else "confirms"
            sql = f"SELECT * FROM {table} WHERE office_code = ? AND account_number = ? FETCH FIRST 1 ROWS ONLY"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, account_office)
            ibm_db.bind_param(stmt, 2, account_number)
            ibm_db.execute(stmt)
            row = ibm_db.fetch_assoc(stmt)
            return {k.lower(): v for k, v in row.items()} if row else {}
        finally:
            ibm_db.close(conn)

    def _mock_record(
        self,
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Return mock letter/confirm data for development/testing."""
        doc_type = params.get("document_type", "letter")

        if doc_type == "letter":
            return {
                "account_number": f"{account_office}-{account_number}",
                "letter_date": str(params.get("load_date", "2026-03-15")),
                "letter_type": params.get("letter_type", "notification"),
                "recipient_name": "John Doe",
                "subject": "Account Update Notification",
                "key_details": {"status": "active", "action_required": False},
            }
        else:
            return {
                "account_number": f"{account_office}-{account_number}",
                "confirm_date": str(params.get("date_from", "2026-03-15")),
                "trade_date": str(params.get("date_from", "2026-03-15")),
                "settlement_date": str(params.get("date_to", "2026-03-17")),
                "confirm_type": params.get("confirm_type", "trade"),
                "security_name": "APPLE INC",
                "symbol": "AAPL",
                "quantity": 100,
                "price": 185.50,
                "net_amount": 18550.00,
                "product": params.get("product", "wealth_management"),
                "branding": "Premium",
            }

    async def health_check(self) -> bool:
        if not settings.db2_host:
            return True  # mock mode
        try:
            import ibm_db
            conn_str = (
                f"DATABASE={settings.db2_database};"
                f"HOSTNAME={settings.db2_host};"
                f"PORT={settings.db2_port};"
                f"PROTOCOL=TCPIP;"
                f"UID={settings.db2_user};"
                f"PWD={settings.db2_password};"
            )
            conn = ibm_db.connect(conn_str, "", "")
            ibm_db.close(conn)
            return True
        except Exception:
            return False
