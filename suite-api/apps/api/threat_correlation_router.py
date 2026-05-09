"""Threat Correlation Router — ALDECI.

Endpoints for threat signal ingestion and correlated incident management.
Prefix: /api/v1/threat-correlation
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

_logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/threat-correlation",
    tags=["threat-correlation"],
)

# ---------------------------------------------------------------------------
# Lazy singleton
# ---------------------------------------------------------------------------

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        import os
        from pathlib import Path

        from core.threat_correlation_engine import ThreatCorrelationEngine

        # Resolve data dir — same priority as the engine itself:
        # 1. $FIXOPS_DATA_DIR (set to /app/.fixops_data in the Dockerfile)
        # 2. $HOME/.fixops_data
        # 3. __file__-relative fallback
        env = os.environ.get("FIXOPS_DATA_DIR", "").strip()
        if env:
            data_dir = Path(env)
        else:
            data_dir = Path.home() / ".fixops_data"
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            data_dir = Path(__file__).resolve().parents[4] / ".fixops_data"
            data_dir.mkdir(parents=True, exist_ok=True)

        db_path = str(data_dir / "threat_correlation_default.db")
        _engine = ThreatCorrelationEngine(db_path)
    return _engine


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

try:
    from apps.api.auth_deps import api_key_auth
except ImportError:
    def api_key_auth():
        return "anon"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class SignalIngest(BaseModel):
    signal_type: str = "alert"
    source_engine: str = "siem"
    signal_id: str = ""
    entity_type: str = "ip"
    entity_value: str
    severity: str = "medium"
    description: str = ""
    timestamp: Optional[str] = None
    ttl_minutes: int = 1440


class RuleCreate(BaseModel):
    rule_name: str
    signal_types: List[str] = Field(default_factory=list)
    time_window_minutes: int = 60
    min_signals: int = 3
    severity_threshold: str = "medium"
    correlation_field: str = "src_ip"
    auto_create_incident: bool = True
    mitre_tactic: str = ""
    enabled: bool = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/signals")
def ingest_signal(
    body: SignalIngest,
    org_id: str = Query(default="default"),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """Ingest a threat signal and attempt auto-correlation."""
    try:
        data = body.model_dump()
        if data.get("timestamp") is None:
            data.pop("timestamp", None)
        return _get_engine().ingest_signal(org_id, data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/signals")
def list_signals(
    org_id: str = Query(default="default"),
    signal_type: Optional[str] = Query(default=None),
    entity_value: Optional[str] = Query(default=None),
    source_engine: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """List threat signals with optional filters."""
    return {
        "signals": _get_engine().list_signals(
            org_id,
            signal_type=signal_type,
            entity_value=entity_value,
            source_engine=source_engine,
            limit=limit,
        )
    }


@router.get("/incidents")
def list_incidents(
    org_id: str = Query(default="default"),
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """List correlated incidents."""
    return {
        "incidents": _get_engine().list_incidents(
            org_id, status=status, severity=severity, limit=limit
        )
    }


@router.get("/incidents/{incident_id}")
def get_incident(
    incident_id: str,
    org_id: str = Query(default="default"),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """Get incident with full signal timeline."""
    result = _get_engine().get_incident(org_id, incident_id)
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return result


@router.post("/incidents/{incident_id}/resolve")
def resolve_incident(
    incident_id: str,
    org_id: str = Query(default="default"),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """Resolve a correlated incident."""
    ok = _get_engine().resolve_incident(org_id, incident_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return {"status": "resolved", "incident_id": incident_id}


@router.post("/rules")
def create_rule(
    body: RuleCreate,
    org_id: str = Query(default="default"),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """Create a correlation rule."""
    try:
        return _get_engine().create_rule(org_id, body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/rules")
def list_rules(
    org_id: str = Query(default="default"),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """List all correlation rules."""
    try:
        return {"rules": _get_engine().list_rules(org_id)}
    except Exception as exc:
        _logger.warning("threat-correlation/rules engine error: %s", exc, exc_info=True)
        return {"rules": [], "_warning": "engine initialising — no data yet"}


@router.get("/stats")
def get_stats(
    org_id: str = Query(default="default"),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """Get correlation statistics for an org."""
    try:
        return _get_engine().get_correlation_stats(org_id)
    except Exception as exc:
        _logger.warning("threat-correlation/stats engine error: %s", exc, exc_info=True)
        return {
            "total_signals": 0,
            "signals_by_type": {},
            "incidents_created": 0,
            "auto_created": 0,
            "by_severity": {},
            "top_entities": [],
            "correlation_rate": 0.0,
            "_warning": "engine initialising — no data yet",
        }


@router.get("/context/{entity_id}")
def get_trustgraph_context(
    entity_id: str,
    org_id: str = Query(default="default"),
    _: Any = Depends(api_key_auth),
) -> Dict[str, Any]:
    """Return TrustGraph cross-domain context for a threat entity (related assets, findings, incidents)."""
    return _get_engine().get_trustgraph_context(org_id, entity_id)
