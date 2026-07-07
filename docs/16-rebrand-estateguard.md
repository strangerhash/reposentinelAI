# Rebrand Decision: EstateGuard

| Field | Value |
|-------|-------|
| Date | July 2026 |
| Decision | **Adopt EstateGuard** as product name for development |
| Supersedes | RepoSentinel AI (working title) |
| Reason | Trademark collision with [reposentinel.com](https://reposentinel.com/) |

---

## Why EstateGuard

| Criterion | EstateGuard |
|-----------|-------------|
| Collision with reposentinel.com | None identified (verify trademark before launch) |
| Describes product | "Guard" for mixed git **estate** security + architecture |
| Enterprise tone | Professional, not indie-scanner |
| Domain | estateguard.io / estateguard.dev — verify availability |

---

## What Changed in Codebase

| Area | New Name |
|------|----------|
| API product name | EstateGuard API |
| Web app | estateguard-web |
| Docker services | estateguard postgres/db user |
| Package scope | `@estateguard/*` (future MCP server) |

## What Stayed

- `docs/` folder retains RepoSentinel AI planning history
- `RepoSentinel_AI_Product_Plan.docx` — historical
- Competitive analysis doc references reposentinel.com as competitor

---

## Positioning (unchanged)

> Governed control plane for mixed git estates — M&A due diligence wedge for Tool Hub consultancies.

---

## Pre-Launch Checklist

- [ ] USPTO / EU trademark search for "EstateGuard"
- [ ] Register domain
- [ ] Update all customer-facing docs to EstateGuard
- [ ] Rebuild HTML documentation bundle with rebrand note
