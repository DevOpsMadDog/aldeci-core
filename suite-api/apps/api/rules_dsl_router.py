"""Rules DSL Router — ALDECI.

Exposes /api/v1/rules/dsl/* endpoints consumed by the UI rules panel.
The canonical unified rules router uses /api/v1/rules/unified.
This router handles the /api/v1/rules/dsl/rules path the UI calls.

Prefix: /api/v1/rules/dsl
Auth:   api_key_auth dependency
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from apps.api.auth_deps import api_key_auth
from fastapi import APIRouter, Depends, Query

_logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/rules/dsl",
    tags=["rules-dsl"],
    dependencies=[Depends(api_key_auth)],
)


def _get_policy_engine():
    from core.policy_engine import get_policy_engine
    return get_policy_engine()


@router.get("/rules")
def list_dsl_rules(
    org_id: str = Query(default="default"),
    domain: Optional[str] = Query(default=None),
    enabled: Optional[bool] = Query(default=None),
) -> List[Dict[str, Any]]:
    """Return DSL rules from the policy engine rule registry."""
    try:
        engine = _get_policy_engine()
        rules = engine.list_rules() if hasattr(engine, "list_rules") else []
        if domain:
            rules = [r for r in rules if r.get("domain") == domain]
        if enabled is not None:
            rules = [r for r in rules if r.get("enabled", True) == enabled]
        return rules
    except Exception as exc:
        _logger.warning("rules_dsl list_dsl_rules: %s", exc)
        return []


@router.get("/taxonomy")
def get_dsl_taxonomy(org_id: str = Query(default="default")) -> Dict[str, Any]:
    """Return rule taxonomy schema for DSL rule authoring."""
    return {
        "domains": ["sast", "dast", "secrets", "iac", "container", "cspm", "api_security"],
        "severities": ["critical", "high", "medium", "low", "info"],
        "rule_types": ["detection", "validation", "compliance", "posture", "hardening"],
    }
