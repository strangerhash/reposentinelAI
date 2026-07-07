# Product Overview

**RepoSentinel AI** — An Agentic Security, Architecture & Knowledge-Base Platform for Multi-Source Git Estates

| Field | Value |
|-------|-------|
| Version | 0.3 |
| Author | Satya / Xenqube |
| Date | July 2026 |
| Status | Internal product strategy — Tool Hub track |
| Naming | **Working title** — see [Competitive Analysis](15-competitive-analysis.md) for rebrand requirement |

---

## Executive Summary

RepoSentinel AI is a governed, agentic platform that connects to every git estate a company runs — GitHub, GitLab, and Bitbucket, cloud or self-hosted — and turns the raw churn of daily commits, PRs, pipelines, and infrastructure-as-code into three continuously-updated products:

1. **Live security & risk posture** — unified risk register across all VCS platforms
2. **Living architecture map** — dependency graph that stays honest as code drifts
3. **Queryable knowledge base** — answers "why does this exist" and "what breaks if I touch this" with citations

### Core Design Bets

**Enforcement boundary:** Static analysis, secret detection, dependency graphing, and policy checks run in deterministic scanners. LLM agents triage, summarize, correlate, and explain — but never silently decide severity or auto-merge fixes. Every flag is traceable to a rule or scanner finding.

**Token economics:** Incremental diffing, tiered model routing, prompt caching, and hierarchical summarization so steady-state cost scales with what changed, not estate size.

### Product Outputs

| Output | Description |
|--------|-------------|
| Multi-repo connector | GitHub, GitLab, Bitbucket (Cloud + Server/DC), normalized event model |
| Deterministic scanning | Secrets, SAST, SCA, IaC, license risk, architecture drift |
| Agentic reasoning | Triage, correlation, explainer, remediation, knowledge-curator, query agents |
| Knowledge base | RAG over code, docs, PRs, incidents — with citations |
| Dashboard | Risk register, flag lifecycle, architecture views, posture score |
| Compliance | SOC 2, ISO 27001, PCI-DSS control mapping + evidence export |

---

## Problem Statement

Mid-size and large engineering organizations rarely run one source control platform. Acquisitions bring Bitbucket, legacy teams stay on self-hosted GitLab, new teams default to GitHub — and security, architecture, and knowledge fragment along the same lines.

### What Breaks Today

- **Security visibility is per-tool** — no single risk register across the company
- **Architecture knowledge goes stale** — nobody can answer "what depends on this service" with confidence
- **Institutional knowledge is unsearchable** — scattered across PR comments, Slack, Confluence
- **AI security tools are expensive at scale** — re-analyze full repos instead of deltas

### What Good Looks Like

- One connector layer, one data model, one place to look
- Every flag has a deterministic, auditable reason
- Any engineer can query the knowledge base with citations
- Cost per repo per day is small and predictable

---

## Positioning

> For engineering organizations and technical consultancies managing mixed GitHub, GitLab, and Bitbucket estates, RepoSentinel AI is the governed control plane that unifies security posture, living architecture, and institutional knowledge — with consultancy-grade due diligence and white-label delivery that scanners alone cannot provide.

**Category:** Git estate control plane — not a GitHub security scanner, not an IDE copilot.

**Primary wedge:** M&A / vendor-risk due diligence for Tool Hub consultancies. The scanner is the engine; the engagement SKU and control plane are the product.

See [Competitive Analysis](15-competitive-analysis.md) for full market assessment.

### Target Buyers

| Persona | Pain | Value Prop |
|---------|------|------------|
| CISO / AppSec | Fragmented security across VCS | One risk register, posture score for board |
| Platform / Architecture | Stale architecture docs | Live dependency map with drift detection |
| Engineering Manager | Slow new-hire ramp | Knowledge copilot — ask instead of ping |
| Consultancy / MSP | Manual due diligence | M&A mode + white-label multi-tenant |
| Legal / Compliance | Audit prep is painful | Pre-built control mappings + evidence export |

### Strategic Fit

Flagship module inside **Tool Hub**, alongside Build Readiness Engine. Both are registry-driven wedge products for technical-services teams in blockchain, AI, and cybersecurity. Validate on 1–2 live pursuits before platform expansion.

### Why Not Claude, Cursor, or reposentinel.com?

| Alternative | Why it falls short at scale |
|-------------|----------------------------|
| **Cursor / Claude** | Session-scoped copilot for one developer — no org-wide risk register, compliance evidence, or 24/7 monitoring |
| **[reposentinel.com](https://reposentinel.com/)** | GitHub-only, scheduled scans, indie-dev pricing — overlaps our MVP but lacks multi-VCS, architecture, KB, M&A mode |
| **Snyk / Aikido** | Strong on dependency auto-fix — weak on mixed-VCS estates, architecture drift, consultancy white-label |

We win on **organizational governance at mixed-VCS scale**, not individual developer productivity.

---

## Core Product Pillars

### Pillar 1 — Unified Multi-Repo Connector Layer

Single ingestion service normalizes GitHub, GitLab, and Bitbucket webhooks and APIs into one canonical event schema. Scanners, agents, and dashboard never talk to VCS APIs directly.

### Pillar 2 — Deterministic Security & Architecture Engine

All ground-truth findings come from deterministic scanners and static graph analysis. LLMs live at the explanation boundary only.

### Pillar 3 — Agentic Reasoning & Knowledge Layer

Purpose-built agents with narrow responsibilities, strict tool contracts, and per-agent token budgets.

### Pillar 4 — Dashboard, Flags & Workflow

Unified risk register and architecture view with flag lifecycle: New → Triaged → Assigned → In Remediation → Resolved → Verified.

### Pillar 5 — Monetization Capabilities

Auto-remediation, posture score, compliance export, M&A due diligence, onboarding mode, white-label, PLG tier, AI-agent governance, VPC deployment.

---

## Success Metrics

| Phase | North Star | Supporting Metrics |
|-------|-----------|-------------------|
| MVP | Flags resolved per week | Cost per repo/day, scan latency |
| V1 | Paid conversion from free tier | Auto-fix PR merge rate, M&A engagements |
| V2 | ARR + net retention | Compliance exports/quarter, MSP tenant count |
