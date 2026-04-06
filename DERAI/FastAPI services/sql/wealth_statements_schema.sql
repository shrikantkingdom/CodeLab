-- Snowflake schema for Wealth Management Statements
-- Table: wealth_statements
-- Used by DERAI to store and compare wealth management account statement data

CREATE TABLE IF NOT EXISTS wealth_statements (
    id                                      NUMBER AUTOINCREMENT PRIMARY KEY,
    office_code                             VARCHAR(3)     NOT NULL,
    account_number                          VARCHAR(10)    NOT NULL,
    account_name                            VARCHAR(200),
    period_start                            DATE           NOT NULL,
    period_end                              DATE           NOT NULL,

    -- Account Summary
    starting_value                          NUMBER(18,2),
    ending_value                            NUMBER(18,2),
    deposits_withdrawals                    NUMBER(18,2),
    dividends_interest                      NUMBER(18,2),
    change_in_value_of_investments          NUMBER(18,2),
    total_ending_value                      NUMBER(18,2),
    total_accruals                          NUMBER(18,2),

    -- Asset Composition
    cash_value                              NUMBER(18,2),
    cash_pct                                NUMBER(5,2),
    equity_value                            NUMBER(18,2),
    equity_pct                              NUMBER(5,2),
    fixed_income_value                      NUMBER(18,2),
    fixed_income_pct                        NUMBER(5,2),
    accruals_value                          NUMBER(18,2),
    accruals_pct                            NUMBER(5,2),

    -- Realized Gain/Loss
    realized_gain_loss_short_term_period    NUMBER(18,2),
    realized_gain_loss_short_term_ytd       NUMBER(18,2),
    realized_gain_loss_long_term_period     NUMBER(18,2),
    realized_gain_loss_long_term_ytd        NUMBER(18,2),

    -- Metadata
    product                                 VARCHAR(50)    DEFAULT 'wealth_management',
    branding                                VARCHAR(200),
    created_at                              TIMESTAMP_NTZ  DEFAULT CURRENT_TIMESTAMP(),
    updated_at                              TIMESTAMP_NTZ  DEFAULT CURRENT_TIMESTAMP(),

    -- Indexes
    UNIQUE (office_code, account_number, period_start, period_end)
);

-- Investment Holdings child table (one-to-many with wealth_statements)
CREATE TABLE IF NOT EXISTS wealth_holdings (
    id                      NUMBER AUTOINCREMENT PRIMARY KEY,
    statement_id            NUMBER         NOT NULL REFERENCES wealth_statements(id),
    security_name           VARCHAR(200)   NOT NULL,
    symbol                  VARCHAR(20),
    asset_class             VARCHAR(50),   -- Cash, Equity, Fixed Income
    shares                  NUMBER(18,6),
    price                   NUMBER(18,4),
    yield_pct               NUMBER(8,4),
    est_annual_income       NUMBER(18,2),
    market_value            NUMBER(18,2),
    created_at              TIMESTAMP_NTZ  DEFAULT CURRENT_TIMESTAMP()
);
