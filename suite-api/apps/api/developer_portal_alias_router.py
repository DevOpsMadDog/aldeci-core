"""Developer Portal alias router — exposes /api/v1/developer-portal/* paths.

The canonical router (developer_portal_router.py) uses prefix /api/v1/developer.
The UI calls /api/v1/developer-portal/findings and /api/v1/developer-portal/repos.
This thin alias router is auto-mounted separately so both prefixes work.
"""
from __future__ import annotations

from apps.api.developer_portal_router import alias_router as router

__all__ = ["router"]
