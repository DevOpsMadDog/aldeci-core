"""
Dashboard alias router — exposes /api/v1/dashboard/* paths that the UI expects.

The canonical data lives in analytics_router under /api/v1/analytics/dashboard/*.
This router is a thin alias layer so both paths return the same data.
"""
from __future__ import annotations

from typing import Any, Dict

from apps.api.auth_deps import api_key_auth
from apps.api.dependencies import get_org_id
from fastapi import APIRouter, Depends, Request

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get(
    "/executive",
    summary="Executive dashboard summary",
    description=(
        "Returns executive security summary: total findings, critical/high counts, "
        "MTTR in hours, and top-5 risks. Alias for /api/v1/analytics/dashboard/executive."
    ),
    dependencies=[Depends(api_key_auth)],
)
async def get_executive_dashboard(
    request: Request,
    org_id: str = Depends(get_org_id),
) -> Dict[str, Any]:
    """Thin alias — delegates to analytics_router executive_summary logic."""
    # Import here to avoid circular imports at module load time.
    from apps.api.analytics_router import get_dashboard_executive as _exec
    result = await _exec(request=request, org_id=org_id)
    return result
