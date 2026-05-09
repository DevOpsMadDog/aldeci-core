# ALDECI — Working Repo (canonical, deploy source)

> **This is now the canonical repo.** Production deploys go from here. Iterative dev still uses `~/fixops/Fixops` as a fork.
> **Branch**: `main` (single trunk, deploy-ready)

---

## Quick context

- **Live**: https://aldeci.fly.dev (deployed from this repo, image `aldeci:deployment-...`)
- **GitHub**: https://github.com/DevOpsMadDog/aldeci-core
- **Fly app**: `aldeci`, region `syd`, 2GB shared-cpu-1x, 10GB volume `aldeci_data`
- **Local API token** (Fly-generated): see `.env` (gitignored). Use as `X-API-Key` header.

## Local dev

```bash
cd ~/aldeci-core
source .venv/bin/activate
source .env
uvicorn apps.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload &
cd suite-ui/aldeci-ui-new && npm install && npm run dev    # vite on :5173
```

## Promotion flow

```
Fixops (dev/dogfood) → cherry-pick lean commits → aldeci-core/main → flyctl deploy
```

## NO MOCKS rule

Every UI task ends with: navigate → screenshot → DOM check → API call confirmed in network tab. See `~/fixops/Fixops/CLAUDE.md` for the full version.

## Stack

Python 3.11 + FastAPI + Pydantic v2 + SQLite per-domain + DuckDB analytics + React 19 + Vite 6 + Tailwind v4. ~683 routers, ~462 engines, ~289 UI pages, ~1353 tests.

## Tests

```bash
python -m pytest \
  tests/test_phase2_connectors.py tests/test_phase3_llm_council.py \
  tests/test_phase4_integration.py tests/test_phase5_enterprise.py tests/test_phase6_streaming.py \
  tests/test_phase7_analytics.py tests/test_phase8_mcp.py tests/test_phase9_playbooks.py \
  tests/test_phase10_e2e.py tests/test_connector_framework.py tests/test_trustgraph.py \
  tests/test_pipeline_api.py tests/test_persona_workflows.py \
  -x --tb=short --timeout=10 -q -o "addopts="
```

## Deploy

```bash
flyctl deploy --remote-only --app aldeci   # ~5min, 523MB image
flyctl logs --app aldeci                    # live logs
flyctl status --app aldeci                  # machine state
```

## Operating rules

1. CTO mode — delegate via Agent tool, don't write code yourself except small (<10 lines)
2. Auto-save every 15-20 min: `git add -A && git commit && git push`
3. Run Beast Mode tests only (13 phase files), zero regressions
4. NO MOCKS in UI — see `feedback_no_mocks_applies_to_routers.md` in memory
5. Commit format: `beast-mode(feature): desc` + `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`

