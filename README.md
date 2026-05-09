# ALDECI

**ASPM + CTEM + CSPM unified security platform — self-hosted, AI-native, multi-LLM consensus.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](LICENSE)

Replace your $500K security stack (Snyk + Apiiro + Aikido + Sonatype + Wiz) with one self-hosted platform. Your data never leaves your VPC.

---

## Quick start

```bash
git clone https://github.com/DevOpsMadDog/aldeci-core.git
cd aldeci-core
docker compose up -d
open http://localhost:8000/executive
```

Default admin token printed in `docker compose logs aldeci-api`.

---

## Features

- **Multi-LLM consensus** — 4 free models vote on every finding; Opus escalates only when needed (saves 95% of LLM cost vs single-model)
- **30 personas covered** — CISO, Board, SOC, DevSecOps, Compliance, DPO, Auditor, Architect — all in one UI
- **28+ threat-intel feeds** — KEV, NVD, EPSS, GHSA, OSV, ExploitDB, AbuseIPDB, OTX, MITRE ATT&CK
- **32 scanner adapters** — Snyk, Aikido, Wiz, Tenable, Qualys, GitLeaks, Trivy, Snyk, Semgrep, Grype, plus 22 more
- **4 compliance frameworks** — SOC2, PCI-DSS, HIPAA, ISO 27001 — auto-evidence pack as ZIP
- **GDPR-ready** — data portability export + right-to-be-forgotten endpoints

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  React 19 + Vite 6 + Tailwind v4    suite-ui/           │
│  21 hubs · 30 personas · /executive · /board            │
└─────────────────────┬───────────────────────────────────┘
                      │ apiFetch + JWT
                      ▼
┌─────────────────────────────────────────────────────────┐
│  FastAPI gateway       suite-api/   683 routers         │
│  /api/v1/auth · billing · import · findings · compliance│
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Engines              suite-core/   462 engines         │
│  Brain Pipeline (12 steps) · TrustGraph · LLM Council   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Feeds + Connectors   suite-feeds/  + suite-integrations│
│  28 threat-intel sources · 13 PULL · 7 bidirectional    │
└─────────────────────────────────────────────────────────┘
```

**Stack:** Python 3.11 · FastAPI · Pydantic v2 · SQLite (per-domain) · DuckDB analytics · React 19 · Vite 6 · Tailwind v4

---

## Deploy

| Target | Time | Cost | Doc |
|---|---|---|---|
| `docker compose up` (laptop) | 1 min | Free | `docs/INSTALL.md` |
| Fly.io (single region) | 5 min | ~$25/mo | `docs/DEPLOY_FLY.md` + `fly.toml` |
| Self-hosted production | 30 min | Your infra | `docs/INSTALL.md` |

Fly.io one-liner (after `flyctl auth login`):
```bash
./scripts/fly-deploy.sh syd
```

---

## Pricing

- **Starter** — $199/mo · 1 org · 100 assets · community support
- **Pro** — $499/mo · 5 orgs · unlimited assets · email support · multi-LLM consensus
- **Enterprise** — $1,499/mo · SAML SSO · custom integrations · dedicated CSM · on-prem support

Self-hosted is always free for personal/research use. Commercial use requires a tier subscription.

---

## Stats

```
683 API routers   ·   462 backend engines   ·   30 personas
21 UI hubs        ·   168 wired tabs        ·   1373 tests
28 threat feeds   ·   32 scanner adapters   ·   4 compliance frameworks
```

---

## Contributing

PRs welcome. See `CONTRIBUTING.md` (coming soon). For commercial integrations or custom feed adapters, email `hello@aldeci.com`.

---

## License

AGPL-3.0 — see [LICENSE](LICENSE). Commercial license available for proprietary deployments.
