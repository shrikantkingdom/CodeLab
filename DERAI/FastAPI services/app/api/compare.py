"""Comparison results retrieval endpoint."""

from fastapi import APIRouter, Query

from app.models.response_models import ComparisonResult

router = APIRouter(prefix="/api/v1", tags=["Comparison"])

# In-memory store for demo. Replace with a real persistence layer.
_results_store: dict[str, ComparisonResult] = {}


def store_result(result: ComparisonResult) -> None:
    """Save a comparison result (called by orchestrator after processing)."""
    key = f"{result.account_number}_{result.document_type.value}_{result.processed_at.isoformat()}"
    _results_store[key] = result


@router.get("/compare-results", response_model=list[ComparisonResult])
async def get_compare_results(
    account_number: str | None = Query(None, description="Filter by account number"),
    limit: int = Query(50, ge=1, le=500),
) -> list[ComparisonResult]:
    """Retrieve past comparison results, optionally filtered by account."""
    results = list(_results_store.values())

    if account_number:
        results = [r for r in results if r.account_number == account_number]

    # Most recent first
    results.sort(key=lambda r: r.processed_at, reverse=True)
    return results[:limit]
