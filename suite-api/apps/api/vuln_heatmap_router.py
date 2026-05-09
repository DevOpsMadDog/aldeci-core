"""Vulnerability Heatmap Router — ALDECI.

Exposes /api/v1/vuln-heatmap/* endpoints consumed by the UI heatmap panel.
Aggregates vulnerability scoring data by asset for visual heatmap rendering.

Prefix: /api/v1/vuln-heatmap
Auth:   api_key_auth dependency
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from apps.api.auth_deps import api_key_auth
from fastapi import APIRouter, Depends, Query

_logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/vuln-heatmap",
    tags=["vuln-heatmap"],
    dependencies=[Depends(api_key_auth)],
)

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from core.vulnerability_scoring_engine import VulnerabilityScoringEngine
        _engine = VulnerabilityScoringEngine()
    return _engine


@router.get("/assets")
def get_heatmap_assets(
    org_id: str = Query(default="default"),
    min_score: float = Query(default=0.0, ge=0.0, le=100.0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> List[Dict[str, Any]]:
    """Return per-asset vulnerability heatmap data (asset_id, risk_score, vuln_count, tier)."""
    try:
        scores = _get_engine().list_scores(org_id)
    except Exception as exc:
        _logger.exception("vuln_heatmap get_heatmap_assets failed")
        return []

    asset_map: Dict[str, Dict[str, Any]] = {}
    for s in scores:
        if isinstance(s, dict):
            aid = s.get("asset_id", "")
            composite = float(s.get("composite_score", 0) or 0)
            tier = s.get("priority_tier", "low")
            cve = s.get("cve_id", "")
        else:
            aid = getattr(s, "asset_id", "")
            composite = float(getattr(s, "composite_score", 0) or 0)
            tier = getattr(s, "priority_tier", "low")
            cve = getattr(s, "cve_id", "")

        if not aid:
            continue
        if aid not in asset_map:
            asset_map[aid] = {
                "asset_id": aid,
                "vuln_count": 0,
                "max_score": 0.0,
                "avg_score": 0.0,
                "total_score": 0.0,
                "highest_tier": tier,
                "cves": [],
            }
        asset_map[aid]["vuln_count"] += 1
        asset_map[aid]["total_score"] += composite
        asset_map[aid]["max_score"] = max(asset_map[aid]["max_score"], composite)
        if cve and cve not in asset_map[aid]["cves"]:
            asset_map[aid]["cves"].append(cve)

    results = []
    for a in asset_map.values():
        cnt = a["vuln_count"]
        a["avg_score"] = round(a["total_score"] / cnt, 2) if cnt else 0.0
        del a["total_score"]
        if a["max_score"] >= min_score:
            results.append(a)

    results.sort(key=lambda x: x["max_score"], reverse=True)
    return results[:limit]


@router.get("/summary")
def get_heatmap_summary(org_id: str = Query(default="default")) -> Dict[str, Any]:
    """Return aggregate heatmap statistics."""
    try:
        dist = _get_engine().get_scoring_distribution(org_id)
        return dist if isinstance(dist, dict) else {}
    except Exception:
        return {"org_id": org_id, "tiers": {}, "total": 0}
