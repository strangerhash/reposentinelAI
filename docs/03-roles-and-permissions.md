# Roles & Permissions

Complete RBAC model for RepoSentinel AI across SaaS, multi-tenant MSP, and self-hosted deployments.

---

## Role Hierarchy

```
Platform Super Admin (Xenqube internal)
  └── Organization Owner
        └── Organization Admin
              ├── Security Lead (CISO delegate)
              ├── Compliance Officer
              ├── Engineering Manager
              ├── Developer
              ├── Auditor (read-only)
              └── MSP Client Admin (white-label tenant)
                    └── MSP Client Viewer
```

---

## Role Definitions

### Organization Owner
- **Who:** CTO, VP Engineering, or account creator
- **Scope:** Full org control
- **Typical count:** 1–2 per org

### Organization Admin
- **Who:** Platform team lead, IT admin
- **Scope:** User management, integrations, billing, tenant settings
- **Cannot:** Delete org, transfer ownership

### Security Lead
- **Who:** CISO, Head of AppSec, security engineer lead
- **Scope:** All security flags, posture config, compliance exports, remediation approval
- **Primary dashboard:** Risk Register, Posture, Compliance

### Compliance Officer
- **Who:** GRC analyst, internal audit, external auditor (time-limited)
- **Scope:** Read-only compliance views, evidence export, control mapping
- **Cannot:** Modify flags, approve remediations, change scanners

### Engineering Manager
- **Who:** Team lead, engineering director
- **Scope:** Team-scoped flags, knowledge base, onboarding mode, assign developers
- **Primary dashboard:** Knowledge Copilot, team posture

### Developer
- **Who:** Individual contributor
- **Scope:** View assigned flags, comment, request remediation PRs, query knowledge base
- **Cannot:** Change org settings, export compliance, approve critical remediations

### Auditor (Read-Only)
- **Who:** External auditor, board observer
- **Scope:** Read-only access to posture, flags, compliance evidence
- **Time-limited:** Expiring access tokens, full audit log of auditor actions

### MSP Client Admin (White-Label)
- **Who:** Consultancy managing client repos
- **Scope:** Full admin within assigned client tenant; white-label branding
- **Isolation:** Strict tenant boundary — cannot see other clients

### MSP Client Viewer
- **Who:** Client stakeholder receiving consultancy reports
- **Scope:** Read-only dashboard and exported reports for their tenant

### Agent Service Account
- **Who:** Internal system — not a human user
- **Scope:** Scoped API keys for agent orchestration, scanner runners, webhook receivers
- **Cannot:** UI access, billing, user management

---

## Permission Matrix

| Permission | Owner | Admin | Sec Lead | Compliance | Eng Mgr | Developer | Auditor | MSP Admin |
|------------|:-----:|:-----:|:--------:|:----------:|:-------:|:---------:|:-------:|:---------:|
| Manage billing | ✓ | ✓ | — | — | — | — | — | — |
| Manage users/roles | ✓ | ✓ | — | — | — | — | — | ✓* |
| Connect VCS repos | ✓ | ✓ | ✓ | — | — | — | — | ✓* |
| Configure scanners | ✓ | ✓ | ✓ | — | — | — | — | ✓* |
| View all flags | ✓ | ✓ | ✓ | ✓ | team | assigned | ✓ | ✓* |
| Triage/assign flags | ✓ | ✓ | ✓ | — | team | — | — | ✓* |
| Approve auto-fix PRs | ✓ | ✓ | ✓ | — | — | — | — | ✓* |
| View posture score | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* |
| Export compliance evidence | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓* |
| Query knowledge base | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓* |
| M&A due diligence mode | ✓ | ✓ | ✓ | — | — | — | — | ✓ |
| White-label branding | — | — | — | — | — | — | — | ✓ |
| View cost/token dashboard | ✓ | ✓ | ✓ | — | — | — | — | ✓ |
| Manage MCP servers | ✓ | ✓ | ✓ | — | — | — | — | ✓* |
| View AI-agent governance | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓* |

`*` = scoped to assigned client tenant only

---

## Resource Scoping

### Organization Level
- All repos, all teams, all flags, global posture score

### Team Level
- Repos tagged to a team
- Team posture score (rollup from repo scores)
- Team-scoped flag assignment

### Repository Level
- Per-repo scanner config, criticality tier, branch policies
- Repo-scoped knowledge base chunks

### Engagement Level (M&A Mode)
- Time-bounded access to target company repos
- Isolated report namespace — no cross-engagement data leakage

---

## Authentication Methods

| Method | Use Case |
|--------|----------|
| SSO (SAML/OIDC) | Enterprise — Okta, Azure AD, Google Workspace |
| GitHub/GitLab OAuth | Developer login + VCS connection |
| API keys (scoped) | CI/CD, agent service accounts, MCP servers |
| Magic link | Auditor time-limited access |

---

## Audit Trail Requirements

Every permission-sensitive action is logged:

```json
{
  "event_id": "uuid",
  "timestamp": "2026-07-07T12:00:00Z",
  "actor": { "type": "user|agent|api_key", "id": "...", "role": "security_lead" },
  "action": "flag.approve_remediation",
  "resource": { "type": "flag", "id": "flag_abc", "org_id": "org_xyz" },
  "metadata": { "pr_url": "https://github.com/...", "rule_id": "sca-cve-2024-1234" },
  "ip": "203.0.113.1",
  "result": "success"
}
```

Retained for: **7 years** (enterprise tier) / **1 year** (team tier).

---

## Default Role Assignment Rules

| Trigger | Default Role |
|---------|-------------|
| Org creator | Organization Owner |
| SSO group `security` | Security Lead |
| SSO group `engineering` | Developer |
| GitHub org admin connecting repos | Organization Admin |
| Marketplace install (free tier) | Organization Owner |
| MSP tenant provisioning | MSP Client Admin |
