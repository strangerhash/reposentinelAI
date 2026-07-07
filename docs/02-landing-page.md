# Landing Page Specification

Complete copy, structure, and design specification for the RepoSentinel AI marketing site.

---

## Page Meta

```
Title: RepoSentinel AI — Security Posture, Living Architecture & Code Knowledge
Description: The governed AI layer above GitHub, GitLab, and Bitbucket. Turn every commit into security posture, architecture clarity, and searchable institutional knowledge.
OG Image: /og/posture-dashboard.png
URL: https://reposentinel.ai
```

---

## Navigation

```
Logo: RepoSentinel AI
Links: Product | Solutions | Pricing | Docs | Blog
CTA: Start Free → /signup
Secondary: Book Demo → /demo
```

---

## Section 1 — Hero

### Headline
**The control plane for mixed git estates.**

### Subheadline
Unify security posture, living architecture, and institutional knowledge across GitHub, GitLab, and Bitbucket — with consultancy-grade due diligence that scanners and IDE copilots cannot deliver.

### CTAs
- **Start free** — Scan up to 5 repos. No credit card.
- **Book a demo** — See auto-remediation and posture scoring live.

### Hero Visual
Animated dashboard mockup: posture score ring (87/100), trend line (+12 pts/90d), 3 critical flags with "Create fix PR" buttons.

### Trust Bar
```
Trusted by platform teams at [fintech] [crypto] [cybersecurity] logos
"As seen on GitHub Marketplace"
```

---

## Section 2 — Problem (3 columns)

| Column | Headline | Body |
|--------|----------|------|
| 1 | Security is fragmented | GitHub has code scanning. GitLab has its own. Bitbucket often has neither. No single risk register exists. |
| 2 | Architecture goes stale | The dependency map in Confluence was wrong the day it was written. Nobody knows what breaks if they touch a service. |
| 3 | Knowledge is trapped | Why was this built this way? The answer is in a PR comment from 2023 that nobody can find. |

---

## Section 3 — Solution (Product Pillars)

### Headline
**Three products. One platform. Zero re-analysis tax.**

### Pillar Cards

**Security Posture**
- Unified risk register across all VCS platforms
- Deterministic scanners — secrets, SAST, SCA, IaC, licenses
- Auto-remediation: draft PRs with fixes, not just flags
- Composite posture score with board-ready trend lines

**Living Architecture**
- Service dependency graph updated on every merge
- Drift detection against approved architecture snapshots
- Cross-repo correlation — one vulnerable library, one flag

**Institutional Knowledge**
- RAG over code, PRs, incidents, and ADRs
- Citations to exact file, commit, and line
- Onboarding mode: ask instead of pinging a senior engineer

---

## Section 4 — How It Works (4 steps)

```
1. Connect → OAuth to GitHub/GitLab/Bitbucket in 60 seconds
2. Scan → Deterministic engines analyze every diff — not full repos
3. Correlate → Agents triage, explain, and link findings across repos
4. Act → Triage flags, merge auto-fix PRs, export compliance evidence
```

### Diagram
Flow: VCS webhook → normalized events → scanners → agents → dashboard + PRs + reports

---

## Section 5 — Differentiators

### Headline
**Built different. On purpose.**

| Feature | Us | reposentinel.com | Cursor / Claude | Snyk / Aikido |
|---------|-----|------------------|-----------------|---------------|
| Multi-VCS | GitHub + GitLab + Bitbucket | GitHub only | N/A | Mostly single-platform |
| Scan model | Event-driven (every push) | Scheduled (hours) | On-demand only | CI/event-driven |
| M&A due diligence | Engagement reports | ❌ | ❌ | ❌ |
| Architecture + drift | Live service graph | ❌ | ❌ | ❌ |
| Knowledge base | RAG with citations | ❌ | Session only | ❌ |
| White-label MSP | Multi-tenant | ❌ | ❌ | ❌ |
| Severity source | Deterministic rules | Scanner-based | Model opinion | Scanner-based |
| Auto-fix | Draft PR with fix | ❌ | Ad-hoc | ✅ |
| Compliance export | Auditor-ready packages | Basic reports | ❌ | Partial |
| VPC / self-hosted | ✅ | Unclear | N/A | Enterprise only |

### Competitive FAQ (Landing Page Section)

**"Why not Cursor?"**  
Cursor is a copilot for one developer. We govern the entire estate — continuous monitoring, auditable flags, compliance evidence.

**"Why not reposentinel.com?"**  
They're GitHub-only with scheduled scans for small teams. We unify mixed VCS estates in real time with consultancy-grade due diligence.

**"Why not Snyk?"**  
Snyk excels at dependency fixes. We add architecture truth, institutional knowledge, and M&A engagements for mixed estates.

---

## Section 6 — Solutions by Persona

### For CISOs & AppSec
Posture score for the board deck. One risk register. Compliance mapping to SOC 2, ISO 27001, PCI-DSS with exportable evidence.

### For Platform Teams
Live architecture map. Drift alerts. Dependency graph that updates on every merge.

### For Engineering Managers
New-hire onboarding copilot. Ramp time reduction without scheduling another knowledge-transfer session.

### For Consultancies & MSPs
M&A due diligence reports in hours. White-label multi-tenant. One sale, N client engagements.

---

## Section 7 — Social Proof

### Testimonial Template
> "We went from three separate security tools to one posture score our CISO puts in every board deck. Auto-remediation closed 60% of our dependency flags without a human touching them."
> — VP Engineering, Series C Fintech

### Stats Bar
```
400+ repos monitored | 60% flags auto-remediated | 90-day posture trend | < $0.02/repo/day LLM cost
```

---

## Section 8 — Pricing Preview

| Tier | Price | For |
|------|-------|-----|
| Free | $0 | Up to 5 repos, secrets + SCA |
| Team | $29/seat/mo | Posture score, KB, workflows |
| Business | Custom | Auto-fix, compliance, M&A mode |
| Enterprise | Custom | White-label, VPC, AI-agent governance |

CTA: **See full pricing →**

---

## Section 9 — Integrations

```
GitHub · GitLab · Bitbucket · Slack · Jira · Linear · Teams
GitHub Marketplace · GitLab Integrations · Atlassian Marketplace
MCP-compatible · Cursor · VS Code
```

---

## Section 10 — Final CTA

### Headline
**Your repos are changing every day. Your security posture should too.**

### CTAs
- Start free — 5 repos, 60-second setup
- Book demo — 30-minute walkthrough with your stack

### Footer
```
Product: Features · Pricing · Docs · Changelog · Status
Company: About · Blog · Careers · Contact
Legal: Privacy · Terms · Security · DPA
Social: GitHub · LinkedIn · X
© 2026 Xenqube. All rights reserved.
```

---

## Landing Page Design Tokens

| Token | Value |
|-------|-------|
| Font | Inter (UI), JetBrains Mono (code) |
| Background | `#FAFAFA` light / `#0F1117` dark |
| Accent | `#3B82F6` |
| Success | `#10B981` |
| Warning | `#F59E0B` |
| Danger | `#EF4444` |
| Border radius | 8px cards, 12px modals |
| Max width | 1280px content, 1440px hero |
| Animation | 150ms ease-out hover states |

### Page Structure (Next.js)

```
/app
  /page.tsx          → Landing page
  /pricing/page.tsx  → Full pricing
  /demo/page.tsx     → Demo booking
  /signup/page.tsx   → OAuth onboarding
  /docs/page.tsx     → Documentation portal
```
