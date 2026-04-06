"""Snowflake database connector for statement records."""

import logging
from typing import Any

from app.config import settings
from app.db.base import DBConnector

logger = logging.getLogger(__name__)


class SnowflakeConnector(DBConnector):
    """Connects to Snowflake to fetch statement data.

    Uses mock data when Snowflake credentials are not configured.
    """

    async def fetch_record(
        self,
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if not settings.snowflake_account:
            logger.info("Snowflake not configured — returning mock data")
            return self._mock_record(account_office, account_number, params)

        return await self._query_snowflake(account_office, account_number, params)

    async def _query_snowflake(
        self,
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute actual Snowflake query."""
        import snowflake.connector  # optional dependency

        conn = snowflake.connector.connect(
            account=settings.snowflake_account,
            user=settings.snowflake_user,
            password=settings.snowflake_password,
            database=settings.snowflake_database,
            schema=settings.snowflake_schema,
            warehouse=settings.snowflake_warehouse,
        )
        try:
            cursor = conn.cursor()
            product = params.get("product", "")

            # Use wealth_statements table for wealth management products
            if product == "wealth_management":
                cursor.execute(
                    """
                    SELECT * FROM wealth_statements
                    WHERE office_code = %s
                      AND account_number = %s
                      AND period_start <= %s
                      AND period_end >= %s
                    LIMIT 1
                    """,
                    (
                        account_office,
                        account_number,
                        params.get("date_from"),
                        params.get("date_to"),
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM statements
                    WHERE office_code = %s
                      AND account_number = %s
                      AND statement_date BETWEEN %s AND %s
                    LIMIT 1
                    """,
                    (
                        account_office,
                        account_number,
                        params.get("date_from"),
                        params.get("date_to"),
                    ),
                )
            columns = [desc[0].lower() for desc in cursor.description]
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else {}
        finally:
            conn.close()

    def _mock_record(
        self,
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Return mock data for development/testing.

        Returns wealth management mock data when product is wealth_management.
        """
        product = params.get("product", "")
        if product == "wealth_management":
            return self._mock_wealth_record(account_office, account_number, params)

        return {
            "account_number": f"{account_office}-{account_number}",
            "statement_date": str(params.get("date_from", "2026-03-01")),
            "period_start": str(params.get("date_from", "2026-03-01")),
            "period_end": str(params.get("date_to", "2026-03-31")),
            "account_name": "John Doe",
            "account_type": "Investment",
            "beginning_balance": 50000.00,
            "ending_balance": 52350.75,
            "total_deposits": 5000.00,
            "total_withdrawals": 2649.25,
            "product": params.get("product", "wealth_management"),
            "branding": "Premium",
        }

    @staticmethod
    def _mock_wealth_record(
        account_office: str,
        account_number: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Return mock wealth management statement data matching PDF structure.

        Schema: wealth_statements table
        Columns: account_number, account_name, period_start, period_end,
                 starting_value, ending_value, deposits_withdrawals,
                 dividends_interest, change_in_value_of_investments,
                 total_ending_value, total_accruals,
                 cash_value, cash_pct, equity_value, equity_pct,
                 fixed_income_value, fixed_income_pct, accruals_value, accruals_pct,
                 realized_gain_loss_short_term_period, realized_gain_loss_short_term_ytd,
                 realized_gain_loss_long_term_period, realized_gain_loss_long_term_ytd,
                 product, branding
        """
        return {
            "account_number": f"{account_office}-{account_number}",
            "account_name": "Sample Wealth Client",
            "period_start": str(params.get("date_from", "2023-09-01")),
            "period_end": str(params.get("date_to", "2023-09-30")),
            "starting_value": 1227825.75,
            "ending_value": 1185818.40,
            "deposits_withdrawals": 0.00,
            "dividends_interest": 3609.75,
            "change_in_value_of_investments": -45617.10,
            "total_ending_value": 1191107.29,
            "total_accruals": 5288.89,
            "cash_value": 18513.03,
            "cash_pct": 2.0,
            "equity_value": 645355.64,
            "equity_pct": 54.0,
            "fixed_income_value": 521949.73,
            "fixed_income_pct": 44.0,
            "accruals_value": 5288.89,
            "accruals_pct": 0.0,
            "realized_gain_loss_short_term_period": 250.07,
            "realized_gain_loss_short_term_ytd": -4827.95,
            "realized_gain_loss_long_term_period": 0.00,
            "realized_gain_loss_long_term_ytd": -22891.06,
            "product": "wealth_management",
            "branding": "First United Bank & Trust",
        }

    async def health_check(self) -> bool:
        if not settings.snowflake_account:
            return True  # mock mode
        try:
            import snowflake.connector
            conn = snowflake.connector.connect(
                account=settings.snowflake_account,
                user=settings.snowflake_user,
                password=settings.snowflake_password,
            )
            conn.close()
            return True
        except Exception:
            return False
