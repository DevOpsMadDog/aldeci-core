"""
Personas catalog API — returns the 30 enterprise personas defined in ALDECI.

GET /api/v1/personas — full catalog with role, description, and permissions summary.
"""
from __future__ import annotations

from typing import Any, Dict, List

from apps.api.auth_deps import api_key_auth
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])

# Canonical 30-persona catalog sourced from core.rbac.PersonaRoleMapping
# and extended with job-title / description metadata.
_PERSONA_CATALOG: List[Dict[str, Any]] = [
    # ── Admins ──────────────────────────────────────────────────────────────
    {"id": "sarah-chen",        "name": "Sarah Chen",        "role": "super_admin",      "title": "CISO",                        "department": "Security"},
    {"id": "marcus-johnson",    "name": "Marcus Johnson",    "role": "admin",             "title": "VP Engineering",              "department": "Engineering"},
    {"id": "maria-lopez",       "name": "Maria Lopez",       "role": "admin",             "title": "IT Director",                 "department": "IT"},
    {"id": "ryan-murphy",       "name": "Ryan Murphy",       "role": "admin",             "title": "Platform Engineer",           "department": "Engineering"},
    {"id": "daniel-thompson",   "name": "Daniel Thompson",   "role": "admin",             "title": "SecOps Manager",              "department": "Security"},
    # ── Security Analysts ───────────────────────────────────────────────────
    {"id": "alex-rivera",       "name": "Alex Rivera",       "role": "security_analyst",  "title": "SOC Analyst T1",              "department": "SOC"},
    {"id": "priya-sharma",      "name": "Priya Sharma",      "role": "security_analyst",  "title": "SOC Analyst T2",              "department": "SOC"},
    {"id": "james-wilson",      "name": "James Wilson",      "role": "security_analyst",  "title": "Security Engineer",           "department": "Security"},
    {"id": "emma-davis",        "name": "Emma Davis",        "role": "security_analyst",  "title": "DevSecOps Engineer",          "department": "Engineering"},
    {"id": "lisa-zhang",        "name": "Lisa Zhang",        "role": "security_analyst",  "title": "Penetration Tester",          "department": "Red Team"},
    {"id": "tom-anderson",      "name": "Tom Anderson",      "role": "security_analyst",  "title": "AppSec Lead",                 "department": "Security"},
    {"id": "jennifer-wu",       "name": "Jennifer Wu",       "role": "security_analyst",  "title": "Cloud Security Architect",    "department": "Cloud"},
    {"id": "karen-taylor",      "name": "Karen Taylor",      "role": "security_analyst",  "title": "Incident Response Lead",      "department": "IR"},
    {"id": "chris-lee",         "name": "Chris Lee",         "role": "security_analyst",  "title": "Security Data Scientist",     "department": "Security"},
    {"id": "nina-patel",        "name": "Nina Patel",        "role": "security_analyst",  "title": "Threat Intel Analyst",        "department": "Threat Intel"},
    {"id": "richard-adams",     "name": "Richard Adams",     "role": "security_analyst",  "title": "Security Architect",          "department": "Security"},
    {"id": "amanda-scott",      "name": "Amanda Scott",      "role": "security_analyst",  "title": "Supply Chain Security",       "department": "Supply Chain"},
    {"id": "brian-hall",        "name": "Brian Hall",        "role": "security_analyst",  "title": "QA Security Tester",          "department": "QA"},
    # ── Compliance Officers ──────────────────────────────────────────────────
    {"id": "robert-kim",        "name": "Robert Kim",        "role": "compliance_officer", "title": "Compliance Officer",         "department": "GRC"},
    {"id": "olivia-martin",     "name": "Olivia Martin",     "role": "compliance_officer", "title": "GRC Analyst",                "department": "GRC"},
    # ── Developers ───────────────────────────────────────────────────────────
    {"id": "emily-chang",       "name": "Emily Chang",       "role": "developer",          "title": "Developer (Security Champion)", "department": "Engineering"},
    # ── Viewers ──────────────────────────────────────────────────────────────
    {"id": "david-park",        "name": "David Park",        "role": "viewer",             "title": "Risk Manager",               "department": "Risk"},
    {"id": "michael-brown",     "name": "Michael Brown",     "role": "viewer",             "title": "Audit Manager",              "department": "Audit"},
    {"id": "catherine-williams","name": "Catherine Williams","role": "viewer",             "title": "Board Member",               "department": "Board"},
    {"id": "mark-roberts",      "name": "Mark Roberts",      "role": "viewer",             "title": "External Auditor",           "department": "Audit"},
    # ── Extended personas ────────────────────────────────────────────────────
    {"id": "soc-lead",          "name": "SOC Lead",          "role": "admin",              "title": "SOC Team Lead",              "department": "SOC"},
    {"id": "vuln-manager",      "name": "Vuln Manager",      "role": "security_analyst",   "title": "Vulnerability Manager",      "department": "Security"},
    {"id": "patch-engineer",    "name": "Patch Engineer",    "role": "developer",          "title": "Patch Release Engineer",     "department": "Engineering"},
    {"id": "devsecops-lead",    "name": "DevSecOps Lead",    "role": "security_analyst",   "title": "DevSecOps Team Lead",        "department": "Engineering"},
    {"id": "generic-user",      "name": "Generic User",      "role": "viewer",             "title": "General User",               "department": "General"},
]

# Role → permissions summary (informational)
_ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "super_admin":       ["admin:all"],
    "admin":             ["admin:all"],
    "security_analyst":  ["read:findings", "write:findings", "read:graph", "read:sbom", "read:feeds", "read:evidence", "write:evidence"],
    "compliance_officer":["read:findings", "read:evidence", "read:compliance", "write:compliance"],
    "developer":         ["read:findings", "read:sbom"],
    "viewer":            ["read:findings", "read:sbom"],
}


@router.get(
    "",
    summary="30-persona enterprise catalog",
    description="Returns the full ALDECI persona catalog (30 enterprise roles) with RBAC role assignments and permission scopes.",
    dependencies=[Depends(api_key_auth)],
)
async def list_personas() -> Dict[str, Any]:
    """Return all 30 enterprise personas with role and permission metadata."""
    personas_out = []
    for p in _PERSONA_CATALOG:
        personas_out.append({
            **p,
            "permissions": _ROLE_PERMISSIONS.get(p["role"], []),
        })
    roles_summary: Dict[str, int] = {}
    for p in _PERSONA_CATALOG:
        roles_summary[p["role"]] = roles_summary.get(p["role"], 0) + 1
    return {
        "personas": personas_out,
        "total": len(personas_out),
        "roles_summary": roles_summary,
    }
