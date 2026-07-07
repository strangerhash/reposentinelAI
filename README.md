# EstateGuard

**Governed control plane for mixed git estates** — security posture, architecture truth, and M&A due diligence across GitHub, GitLab, and Bitbucket.

> Rebranded from **RepoSentinel AI** due to collision with [reposentinel.com](https://reposentinel.com/). See [docs/16-rebrand-estateguard.md](docs/16-rebrand-estateguard.md).

## Quick Start (Docker)

```bash
./start.sh
# or
make start
```

This builds and starts **Postgres, Redis, API, and Web** via Docker, seeds demo data, and prints URLs.

```bash
./stop.sh      # stop containers
make logs      # follow logs
make check     # verify web + API are up
```

**Local dev (without Docker for app):** `make dev`

| Service | URL |
|---------|-----|
| Landing page | http://localhost:19000 |
| Dashboard | http://localhost:19000/dashboard |
| M&A Engagements | http://localhost:19000/dashboard/engagements |
| API docs | http://localhost:19001/docs |

Ports are configurable in `.env` (defaults **19000–19003** to avoid conflicts with 3000, 5432, 6379, 8000). Run `make ports` to print current mapping.

### Docker (recommended)

```bash
./start.sh
```

Uses ports from `.env` (default **19000–19003**). `start.sh` frees conflicting local processes before binding.

## MVP Wedge (What's Built)

| Feature | Status |
|---------|--------|
| M&A due diligence engagements | ✅ Create, scan, report |
| GitHub + GitLab webhooks | ✅ `/webhooks/github/{tenant}`, `/webhooks/gitlab/{tenant}` |
| Secrets + SCA scanners | ✅ Deterministic (regex + dependency stub) |
| Flag workflow | ✅ Risk register API + UI |
| Posture score | ✅ Computed from open flags |
| Landing page | ✅ Competitive positioning |
| Dashboard shell | ✅ Posture, Flags, Engagements |

## Project Structure

```
estateguard/  (repo: reposentinelAI)
├── apps/web/              Next.js 15 dashboard + landing
├── services/api/          FastAPI — monolith MVP
│   ├── app/models.py      SQLAlchemy models
│   ├── app/scanners/      Secrets + SCA engine
│   ├── app/routers/       REST + webhooks
│   └── scripts/seed.py    Demo data
├── docs/                  Product & architecture docs (15+ files)
├── docker-compose.yml
└── Makefile
```

## Documentation

| Doc | Description |
|-----|-------------|
| [Complete HTML](RepoSentinel_AI_Complete_Documentation.html) | All planning docs |
| [Competitive Analysis](docs/15-competitive-analysis.md) | vs reposentinel.com, Cursor, Snyk |
| [Roadmap](docs/13-roadmap-and-pricing.md) | Wedge-first phases |
| [Rebrand](docs/16-rebrand-estateguard.md) | EstateGuard naming decision |

## API Examples

```bash
# Health
curl http://localhost:19001/v1/health

# Create engagement
curl -X POST http://localhost:19001/v1/engagements \
  -H 'Content-Type: application/json' \
  -d '{"name":"Acme Acquisition","target_org":"Acme Corp"}'

# Run scan (uses demo repos if none linked)
curl -X POST http://localhost:19001/v1/engagements/{id}/scan

# Get report
curl http://localhost:19001/v1/engagements/{id}/report
```

## Next Build Steps

1. GitHub App OAuth + real diff fetching
2. GitLab connector parity
3. Triage + Explainer agents (vLLM)
4. PDF export for engagement reports
5. White-label report branding
