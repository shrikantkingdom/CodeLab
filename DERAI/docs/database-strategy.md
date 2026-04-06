# Database Strategy

## Overview
DERAI connects to two enterprise databases to fetch "source of truth" records for comparison:
- **Snowflake**: Account statements (financial data)
- **DB2**: Client letters and confirms (correspondence documents)

## Architecture

```
Orchestrator
├── DocumentType = STATEMENT
│   └── DBFactory → SnowflakeConnector
│       └── SELECT * FROM statements WHERE office='001' AND account='123456'
│
├── DocumentType = LETTER
│   └── DBFactory → DB2Connector
│       └── SELECT * FROM letters WHERE account_id='001123456' AND type='...'
│
└── DocumentType = CONFIRM
    └── DBFactory → DB2Connector
        └── SELECT * FROM confirms WHERE account_id='001123456' AND type='...'
```

## Mock-First Development Strategy

**Problem**: Snowflake and DB2 require enterprise accounts, VPN, and credentials that aren't available in local development.

**Solution**: Each connector has a built-in mock mode that activates when credentials are empty:

```python
class SnowflakeConnector(DBConnector):
    async def fetch_record(self, account, doc_type, **kwargs):
        if not self._settings.snowflake_account:
            return self._mock_data(account, doc_type)  # Realistic fake data
        # Real Snowflake query...
```

### Mock Data Is Realistic
Mock data mirrors the exact schema of production data:
- **Statements**: Account name, balance, date range, transaction count, currency
- **Letters**: Letter type, subject, date, recipient, signer
- **Confirms**: Trade details, settlement date, amount, counterparty

This allows the full pipeline to work without any database setup.

## Snowflake Configuration

```env
SNOWFLAKE_ACCOUNT=xyz12345.us-east-1
SNOWFLAKE_USER=derai_service
SNOWFLAKE_PASSWORD=<secret>
SNOWFLAKE_DATABASE=FINANCIAL_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

**Connection pattern**: Uses `snowflake-connector-python` with cursor-based queries.

## DB2 Configuration

```env
DB2_HOST=db2-server.internal.com
DB2_PORT=50000
DB2_DATABASE=CORR_DB
DB2_USER=derai_user
DB2_PASSWORD=<secret>
```

**Connection pattern**: Uses `ibm_db` Python driver with parameterized queries.

## Data Privacy & Security

1. **No data caching**: DB results are used for comparison only, never persisted
2. **Parameterized queries**: All SQL uses bind parameters (no string interpolation)
3. **Connection pooling**: Single connection per request, closed after use
4. **Credential isolation**: All credentials via environment variables
5. **Network**: In production, connections go through VPN/private endpoints

## Future Enhancements

1. **Connection pooling**: Use SQLAlchemy or dedicated pool for high throughput
2. **Read replicas**: Point queries to read replicas to reduce load
3. **Caching layer**: Redis cache for frequently accessed account records
4. **Audit logging**: Log all DB queries with timestamps for compliance
