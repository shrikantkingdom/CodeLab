"""Utility functions for account number padding and formatting."""


def pad_office(value: str) -> str:
    """Pad office code to 3 digits with leading zeros."""
    return value.strip().zfill(3)


def pad_account(value: str) -> str:
    """Pad account number to 6 digits with leading zeros."""
    return value.strip().zfill(6)


def format_full_account(office: str, account: str) -> str:
    """Format full account as 'office-account' with proper padding."""
    return f"{pad_office(office)}-{pad_account(account)}"
