"""Vendor Risk alias router — exposes /api/v1/vendor-risk/* paths.

The canonical router (vendor_risk_router.py) uses prefix /api/v1/vendors.
The UI calls /api/v1/vendor-risk/vendors, /vendor-risk/assessments,
/vendor-risk/risk-domains, /vendor-risk/risk-register.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from apps.api.auth_deps import api_key_auth
from fastapi import APIRouter, Depends, Query

_logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/vendor-risk",
    tags=["vendor-risk-alias"],
    dependencies=[Depends(api_key_auth)],
)

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from core.vendor_risk import get_engine as _ge
        _engine = _ge()
    return _engine


def _vendor_to_dict(v: Any) -> Dict[str, Any]:
    """Safely convert a Vendor model to dict, handling both Pydantic and plain dicts."""
    if hasattr(v, "model_dump"):
        d = v.model_dump()
        # Vendor uses .id internally; expose as vendor_id for API consistency
        if "vendor_id" not in d and "id" in d:
            d["vendor_id"] = d["id"]
        return d
    return dict(v) if hasattr(v, "__iter__") else {}


@router.get("/vendors")
def list_vendors_alias(
    org_id: str = Query(default="default"),
) -> List[Dict[str, Any]]:
    """List all vendors (alias for /api/v1/vendors)."""
    try:
        vendors = _get_engine().list_vendors()
        return [_vendor_to_dict(v) for v in vendors]
    except Exception as exc:
        _logger.exception("vendor_risk_alias list_vendors failed: %s", exc)
        return []


@router.get("/assessments")
def list_assessments_alias(
    org_id: str = Query(default="default"),
    limit: int = Query(default=5, ge=1, le=200),
) -> List[Dict[str, Any]]:
    """Return recent vendor assessments (alias endpoint for UI)."""
    try:
        vendors = _get_engine().list_vendors()
        results = []
        for v in vendors[:limit]:
            # Vendor model uses .id, not .vendor_id
            vid = getattr(v, "id", None) or (v.get("id") if isinstance(v, dict) else None)
            if not vid:
                continue
            try:
                a = _get_engine().get_assessment(vid)
                if a:
                    results.append(a.model_dump() if hasattr(a, "model_dump") else dict(a))
            except Exception:
                continue
        return results
    except Exception:
        return []


@router.get("/risk-domains")
def list_risk_domains(
    org_id: str = Query(default="default"),
) -> List[Dict[str, Any]]:
    """Return vendor risk domain breakdown (tiering overview)."""
    try:
        overview = _get_engine().get_tiering_overview()
        data = overview.model_dump() if hasattr(overview, "model_dump") else dict(overview)
        # TieringOverview has tier_counts or distribution field
        tiers = data.get("tier_counts") or data.get("tiers") or data.get("distribution") or {}
        if isinstance(tiers, dict):
            return [{"domain": k, "count": v} for k, v in tiers.items()]
        return [{"data": data}]
    except Exception as exc:
        _logger.warning("vendor_risk_alias list_risk_domains: %s", exc)
        return []


@router.get("/risk-register")
def get_risk_register(
    org_id: str = Query(default="default"),
) -> Dict[str, Any]:
    """Return vendor risk register — all vendors with current risk tier and score."""
    try:
        vendors = _get_engine().list_vendors()
        items = []
        for v in vendors:
            vd = _vendor_to_dict(v)
            items.append({
                "vendor_id": vd.get("vendor_id") or vd.get("id", ""),
                "name": vd.get("name", ""),
                "tier": str(vd.get("tier", "")),
                "risk_score": vd.get("risk_score", 0),
                "service_category": str(vd.get("service_category", "")),
            })
        return {"org_id": org_id, "total": len(items), "items": items}
    except Exception as exc:
        _logger.exception("vendor_risk_alias get_risk_register: %s", exc)
        return {"org_id": org_id, "total": 0, "items": []}
