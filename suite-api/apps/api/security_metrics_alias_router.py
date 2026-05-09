"""Security Metrics alias router — exposes /api/v1/security-metrics/metrics.

The canonical router (security_metrics_router.py) uses prefix /api/v1/metrics.
The UI calls /api/v1/security-metrics/metrics.
This alias router maps the hyphenated prefix to the underlying engine.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from apps.api.auth_deps import api_key_auth
from fastapi import APIRouter, Depends, Query

router = APIRouter(
    prefix="/api/v1/security-metrics",
    tags=["security-metrics-alias"],
    dependencies=[Depends(api_key_auth)],
)

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from core.security_metrics import SecurityMetricsEngine
        _engine = SecurityMetricsEngine()
    return _engine


@router.get("/metrics")
def get_security_metrics(
    days: int = Query(30, ge=1, le=365),
    org_id: str = Query(default="default"),
) -> Dict[str, Any]:
    """Return DORA-style security metrics for the org (alias for /api/v1/metrics/dora)."""
    try:
        dora = _get_engine().compute_dora_metrics(days=days)
        return {
            "org_id": org_id,
            "days": days,
            "mttd_hours": dora.mttd_hours,
            "mttc_hours": dora.mttc_hours,
            "mttr_hours": dora.mttr_hours,
            "change_failure_rate": dora.change_failure_rate,
            "sample_size": dora.sample_size,
        }
    except Exception:
        return {
            "org_id": org_id,
            "days": days,
            "mttd_hours": 0.0,
            "mttc_hours": 0.0,
            "mttr_hours": 0.0,
            "change_failure_rate": 0.0,
            "sample_size": 0,
        }
