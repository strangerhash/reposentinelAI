# Roadmap & Pricing

Phased delivery plan, pricing tiers, and monetization strategy for RepoSentinel AI.

> **Competitive-informed roadmap.** See [Competitive Analysis](15-competitive-analysis.md) for market assessment. MVP is repositioned around consultancy wedge, not me-too GitHub scanning.

---

## Wedge-First Build Priority

Reordered based on competitive analysis (July 2026):

| Priority | What to Build | Phase | Why |
|:--------:|--------------|-------|-----|
| **P0** | Resolve naming / rebrand | Pre-build | Blocker vs [reposentinel.com](https://reposentinel.com/) |
| **P1** | M&A due diligence engagement mode | MVP | No direct competitor; revenue now |
| **P2** | GitHub + GitLab connectors | MVP | Real gap vs reposentinel.com (GitHub-only) |
| **P3** | Event-driven scanning + flag workflow | MVP | vs their scheduled scans |
| **P4** | Architecture map + drift | V1 | Unique vs all scanners |
| **P5** | Knowledge base + onboarding mode | V1 | vs Cursor; second buyer persona |
| **P6** | Posture score + auto-fix PRs | V1 | Table stakes; needed but not sufficient |
| **P7** | White-label MSP multi-tenant | V2 | Consultancy scale motion |
| **P8** | Compliance evidence export | V2 | Enterprise; long sales cycle |
| **P9** | MCP governance | V2 | 2026 narrative |
| **P10** | PLG free tier + Marketplace | V1 | Distribution — don't lead with this |

---

## Build-Effort vs. Sales-Impact Matrix

| Priority | Capability | Sales Impact | Build Effort | Phase |
|:--------:|-----------|--------------|--------------|-------|
| 1 | M&A due diligence mode | Very High (consultancy) | Medium | **MVP** |
| 2 | Multi-VCS (GitHub + GitLab) | Very High | Medium | **MVP** |
| 3 | Event-driven flag workflow | High | Medium | MVP |
| 4 | Architecture map + drift | High (unique) | Medium-High | V1 |
| 5 | Knowledge base + onboarding | Medium-High | Low-Medium | V1 |
| 6 | Auto-remediation (draft PR) | Very High | Medium-High | V1 |
| 7 | Posture score + trending | Very High (board deck) | Medium | V1 |
| 8 | White-label multi-tenant | High (MSP scale) | High | V2 |
| 9 | Compliance evidence packages | Very High (Legal co-sign) | High | V2 |
| 10 | Free / PLG tier | High (distribution) | Low | V1 (deferred from MVP) |

---

## Phase 1 — MVP (6–8 weeks)

**Goal:** Close 1 consultancy M&A engagement on Tool Hub. Prove wedge — not PLG scanner volume.

### Deliverables

| Area | Scope |
|------|-------|
| **Wedge** | **M&A due diligence engagement mode** — scoped report, white-label PDF |
| Connectors | **GitHub + GitLab** (GitLab moved from V1 — competitive differentiation) |
| Scanners | Secrets + SCA (dependency/CVE) — engine, not product |
| Ingestion | **Event-driven** (webhook per push) — vs reposentinel.com scheduled scans |
| Agents | Triage + Explainer (Tier 0/1) |
| Dashboard | Risk Register, Flag Detail, Engagement Report view |
| Knowledge | Manual seeding from pilot repos only |
| Design | Full design system, dark mode, landing page (rebrand-aware) |
| Auth | GitHub/GitLab OAuth + basic org/user model |
| MCP | Read-only tools: list_flags, query_knowledge |
| **Deferred** | Free PLG tier, GitHub Marketplace, Bitbucket |

### Exit Criteria

- [ ] 1 M&A or vendor-risk engagement delivered on Tool Hub pursuit
- [ ] GitHub + GitLab repos scanning event-driven
- [ ] Engagement report generated in < 4 hours for ≤20 repos
- [ ] Flag visible in dashboard < 60s after push (p95)
- [ ] Token cost < $0.02/repo/day
- [ ] Rebrand decision finalized (trademark search complete)

### Team (Suggested)

| Role | Count |
|------|-------|
| Full-stack (Next.js + FastAPI) | 2 |
| Backend (scanners + agents + engagement mode) | 1 |
| Product/Design | 0.5 |

---

## Phase 2 — V1 (Next Quarter)

**Goal:** First paying customers via consultancy SKU + team subscriptions. Not price war with reposentinel.com.

### Deliverables

| Area | Scope |
|------|-------|
| Connectors | Bitbucket |
| Scanners | SAST, IaC, license, architecture drift |
| Agents | + Correlation, Remediation, Knowledge-Curator |
| Monetization | Auto-remediation PR, posture score, onboarding mode |
| Dashboard | Architecture map, Knowledge Copilot, cost dashboard |
| Integrations | Slack, Jira, email digests |
| MCP | + create_fix_pr, get_posture_score, search_architecture |
| Distribution | Free PLG tier + GitHub Marketplace (now differentiated enough) |

### Exit Criteria

- [ ] ≥1 paid M&A engagement ($5K+) or ≥3 Team tier customers
- [ ] Auto-fix PR merge rate ≥30% of eligible flags
- [ ] Posture score used in ≥1 customer board deck
- [ ] Win/loss interviews document why buyer chose us over reposentinel.com / Cursor

---

## Phase 3 — V2 (Platform Tier)

**Goal:** Enterprise and MSP ready. Standalone commercial product.

### Deliverables

| Area | Scope |
|------|-------|
| Compliance | SOC 2 / ISO 27001 / PCI-DSS mapping + auditor-ready evidence export |
| Multi-tenant | White-label branding for MSPs/consultancies |
| AI Governance | MCP registry, AI-BOM, agent activity tracking |
| Deployment | VPC / self-hosted Helm chart |
| Enterprise | SSO/SAML, MFA, IP allowlisting, data residency |
| Agents | Tier 2 escalation |
| Distribution | GitLab + Atlassian Marketplace; peer benchmarking |

### Exit Criteria

- [ ] ≥1 Enterprise customer (VPC or SSO)
- [ ] ≥1 MSP with ≥3 client tenants
- [ ] Compliance evidence export used in ≥1 audit

---

## Pricing Tiers

> Pricing assumes rebrand complete. Do not launch as "RepoSentinel" without legal clearance.

### Tier 0 — Free (PLG) — V1, Not MVP

| Attribute | Value |
|-----------|-------|
| Price | $0 |
| Repos | Up to 5 |
| Purpose | Lead-gen **after** differentiation shipped — not MVP priority |
| Note | reposentinel.com already owns this segment at €0–10/mo |

### Tier 1 — Team

| Attribute | Value |
|-----------|-------|
| Price | $29/seat/month (min 5 seats) |
| Repos | Unlimited |
| Includes | Posture score, KB, flag workflow, Slack/Jira, multi-VCS |

### Tier 2 — Business

| Attribute | Value |
|-----------|-------|
| Price | Custom (~$2,000/month) |
| Includes | Auto-remediation, compliance mapping, M&A mode, onboarding mode |

### Tier 3 — Enterprise / MSP

| Attribute | Value |
|-----------|-------|
| Price | Custom annual ($50K–500K) |
| Includes | White-label, multi-tenant, VPC/self-hosted, AI-agent governance, evidence export |

### Engagement Pricing (Consultancy SKU)

| SKU | Price Range | Buyer |
|-----|-------------|-------|
| M&A Due Diligence Report | $5,000 – $25,000 per engagement | Consultancy / PE |
| Vendor Risk Assessment | $2,000 – $10,000 per vendor | Enterprise procurement |
| Compliance Audit Package | $2,000 – $10,000 per cycle | GRC / Legal |

---

## Go-to-Market Sequence (Revised)

```
Month 0:    Trademark search + rebrand decision
Month 1–2:  MVP on 1 Tool Hub consultancy pursuit (M&A engagement)
Month 3:    V1 features: architecture map, KB, auto-fix
Month 4:    Second consultancy engagement + first Team tier customer
Month 5:    Free tier + GitHub Marketplace (now differentiated)
Month 6–8:  MSP white-label pilot
Month 9+:   Enterprise VPC + compliance export
```

**Do not** lead with PLG free tier in Month 1 — reposentinel.com already owns that fight.

---

## Competitive Positioning

Full analysis: [15-competitive-analysis.md](15-competitive-analysis.md)

| Competitor | Their Strength | Our Edge |
|-----------|---------------|----------|
| [reposentinel.com](https://reposentinel.com/) | Live, cheap, GitHub health | Multi-VCS, event-driven, M&A mode, architecture, KB |
| Cursor / Claude | Developer copilot | Org-wide governance, audit trail, compliance — not IDE |
| Snyk | Brand, SCA depth | Multi-VCS, KB, consultancy SKUs |
| Aikido | Auto-fix, PLG | Architecture map, M&A mode, white-label |
| Apiiro | AppSec platform breadth | Token efficiency, Tool Hub, MCP governance |
| GitHub Advanced Security | Native GitHub | GitLab + Bitbucket, cross-VCS correlation |

---

## 90-Day Build Sequence (Revised)

| Week | Focus |
|------|-------|
| 1 | Rebrand research + trademark search; design system |
| 2 | GitHub + GitLab connectors + canonical event schema |
| 3–4 | Secrets + SCA scanners + event-driven ingestion |
| 5 | M&A engagement mode (scoped access, report generator) |
| 6 | Triage/Explainer agents + Risk Register UI |
| 7 | Engagement report UI + white-label PDF export |
| 8 | **First Tool Hub consultancy pilot** |
| 9–10 | Architecture drift scanner + map UI |
| 11–12 | Knowledge base + auto-remediation agent |
| 13 | V1 pricing + second pursuit |
