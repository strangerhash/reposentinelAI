# API Design

REST and GraphQL API specification for RepoSentinel AI v1.

**Base URL:** `https://api.reposentinel.ai/v1`  
**Auth:** Bearer JWT or `X-API-Key` header  
**Content-Type:** `application/json`

---

## Authentication

### Obtain Token (OAuth / SSO)

```
POST /auth/token
{ "grant_type": "authorization_code", "code": "...", "redirect_uri": "..." }

Response 200:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### API Key (Service Accounts)

```
Header: X-API-Key: rsl_live_abc123...
Scope: embedded in key metadata (read:flags, write:remediation, etc.)
```

---

## Organizations & Users

### Get Current Org

```
GET /org
Authorization: Bearer {token}

Response 200:
{
  "id": "org_xyz",
  "name": "Acme Corp",
  "plan_tier": "business",
  "settings": { "default_criticality": "medium" },
  "white_label": null
}
```

### List Users

```
GET /org/users?role=security_lead&team_id=team_abc
```

### Invite User

```
POST /org/users/invite
{
  "email": "seclead@acme.com",
  "role": "security_lead",
  "team_id": null
}
```

---

## Repositories

### Connect Repository

```
POST /repos/connect
{
  "platform": "github",
  "installation_id": "12345",  // GitHub App
  "repos": ["acme/payment-service", "acme/auth-gateway"]
}

Response 201:
{
  "connected": 2,
  "repos": [{ "id": "repo_abc", "full_name": "acme/payment-service", "status": "scanning" }]
}
```

### List Repositories

```
GET /repos?platform=github&team_id=team_abc&criticality=critical

Response 200:
{
  "data": [{
    "id": "repo_abc",
    "full_name": "acme/payment-service",
    "platform": "github",
    "criticality_tier": "critical",
    "last_scan_at": "2026-07-07T10:00:00Z",
    "open_flags": 3,
    "posture_score": 87
  }],
  "pagination": { "cursor": "...", "has_more": false }
}
```

---

## Flags (Risk Register)

### List Flags

```
GET /flags?severity=critical,high&status=open,assigned&repo_id=repo_abc&assignee_id=user_xyz

Response 200:
{
  "data": [{
    "id": "flag_abc",
    "title": "CVE-2024-1234 in lodash@4.17.20",
    "severity": "high",
    "status": "assigned",
    "repository": { "id": "repo_abc", "full_name": "acme/payment-service" },
    "assignee": { "id": "user_xyz", "name": "Jane Dev" },
    "sla_due_at": "2026-07-10T00:00:00Z",
    "remediation_pr_url": null,
    "findings_count": 2,
    "created_at": "2026-07-07T10:05:00Z"
  }]
}
```

### Get Flag Detail

```
GET /flags/{flag_id}

Response 200:
{
  "id": "flag_abc",
  "title": "CVE-2024-1234 in lodash@4.17.20",
  "severity": "high",
  "severity_rule_version": "3.2.1",
  "status": "assigned",
  "explanation": "lodash versions below 4.17.21 are vulnerable to prototype pollution...",
  "remediation_steps": [
    { "step": 1, "action": "Upgrade lodash to >=4.17.21", "automated": true }
  ],
  "findings": [{
    "id": "finding_xyz",
    "scanner": "sca",
    "rule_id": "cve-2024-1234",
    "file_path": "package.json",
    "line_start": 42,
    "metadata": { "package": "lodash", "installed": "4.17.20", "fixed_in": "4.17.21" }
  }],
  "events": [{
    "action": "flag.assigned",
    "actor": { "type": "user", "id": "user_sec", "name": "Security Lead" },
    "created_at": "2026-07-07T11:00:00Z"
  }],
  "citations": [{ "type": "file", "path": "package.json", "line": 42, "commit": "abc123" }]
}
```

### Update Flag Status

```
PATCH /flags/{flag_id}
{
  "status": "assigned",
  "assignee_id": "user_xyz"
}
```

### Create Remediation PR

```
POST /flags/{flag_id}/remediate
{ "auto_merge": false }  // always false — draft PR only

Response 202:
{
  "agent_run_id": "run_abc",
  "status": "queued",
  "estimated_completion": "2026-07-07T10:06:00Z"
}

// Poll: GET /agent-runs/{run_id}
Response 200:
{
  "status": "completed",
  "output": {
    "pr_url": "https://github.com/acme/payment-service/pull/99",
    "branch": "reposentinel/fix/cve-2024-1234",
    "files_changed": ["package.json", "package-lock.json"]
  }
}
```

---

## Posture

### Get Org Posture Score

```
GET /posture?scope=org

Response 200:
{
  "score": 87,
  "trend_90d": 12,
  "peer_percentile": 72,
  "breakdown": {
    "critical_open": 1,
    "high_open": 5,
    "auto_remediated_30d": 42,
    "repos_at_risk": 3
  },
  "history": [
    { "date": "2026-07-01", "score": 82 },
    { "date": "2026-07-07", "score": 87 }
  ]
}
```

---

## Knowledge Base

### Query

```
POST /knowledge/query
{
  "question": "Why does payment-service retry 3 times?",
  "mode": "default",  // default | onboarding
  "repository_ids": ["repo_abc"]  // optional scope
}

Response 200:
{
  "answer": "The retry logic is configured in src/http/client.ts...",
  "confidence": 0.87,
  "citations": [{
    "type": "code",
    "repository": "acme/payment-service",
    "path": "src/http/client.ts",
    "lines": "45-52",
    "commit": "def456",
    "snippet": "const MAX_RETRIES = 3;"
  }],
  "agent_tier_used": 0
}
```

---

## Compliance

### List Controls

```
GET /compliance/frameworks/soc2/controls?status=at_risk

Response 200:
{
  "framework": "SOC2",
  "controls": [{
    "control_id": "CC6.1",
    "title": "Logical Access Security",
    "status": "at_risk",
    "linked_flags": 3,
    "last_assessed": "2026-07-07T02:00:00Z"
  }]
}
```

### Export Evidence Package

```
POST /compliance/export
{
  "framework": "soc2",
  "control_ids": ["CC6.1", "CC7.2"],
  "format": "pdf",  // pdf | json | zip
  "date_range": { "from": "2026-01-01", "to": "2026-07-07" }
}

Response 202: { "export_id": "exp_abc", "status": "generating" }
GET /compliance/exports/{export_id} → { "download_url": "...", "expires_at": "..." }
```

---

## Engagements (M&A)

```
POST /engagements
{
  "name": "Acme acquisition — TargetCo",
  "target_org": "TargetCo",
  "repo_urls": ["https://github.com/targetco/api", "https://github.com/targetco/web"],
  "expires_at": "2026-08-07T00:00:00Z",
  "white_label": { "logo_url": "...", "report_title": "TargetCo Security Assessment" }
}

GET /engagements/{id}/report → PDF or web report URL
```

---

## MCP & AI Agent Governance

```
GET /mcp/servers
POST /mcp/servers
{
  "name": "cursor-workspace",
  "server_type": "external",
  "permissions": ["read:flags", "query:knowledge"]
}

GET /ai-agents/activity?repository_id=repo_abc&since=2026-07-01
```

---

## Webhooks (Outbound)

Customers configure webhook endpoints to receive events:

```
POST https://customer.com/webhooks/reposentinel
X-RepoSentinel-Signature: sha256=...

{
  "event": "flag.created",
  "timestamp": "2026-07-07T10:05:00Z",
  "data": { "flag_id": "flag_abc", "severity": "critical", ... }
}
```

**Event types:** `flag.created`, `flag.resolved`, `posture.updated`, `remediation.pr_opened`, `compliance.export_ready`

---

## WebSocket (Real-Time)

```
WSS /ws?token={jwt}

Subscribe: { "action": "subscribe", "channels": ["flags:org_xyz", "posture:org_xyz"] }

Push: { "channel": "flags:org_xyz", "event": "flag.updated", "data": {...} }
```

---

## Error Format

```json
{
  "error": {
    "code": "FLAG_NOT_FOUND",
    "message": "Flag flag_abc does not exist or you lack access",
    "status": 404,
    "request_id": "req_xyz"
  }
}
```

## Rate Limits

| Tier | Requests/min | Agent queries/day |
|------|-------------|-------------------|
| Free | 60 | 50 |
| Team | 300 | 500 |
| Business | 1000 | 5000 |
| Enterprise | Custom | Custom |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
