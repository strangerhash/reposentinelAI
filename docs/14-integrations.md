# Integrations

Third-party integrations, marketplace listings, and notification channels for RepoSentinel AI.

---

## Version Control Systems

### GitHub

| Feature | Implementation |
|---------|---------------|
| Connection | GitHub App (preferred) or OAuth |
| Events | push, pull_request, release, workflow_run, repository |
| Permissions | Contents (read), Pull requests (read/write for remediation), Metadata |
| API | REST v3 + GraphQL v4 |
| Marketplace | GitHub Marketplace listing (primary distribution) |

**GitHub App Manifest:**
```yaml
name: RepoSentinel AI
url: https://reposentinel.ai
hook_attributes:
  url: https://api.reposentinel.ai/webhooks/github
redirect_url: https://app.reposentinel.ai/auth/github/callback
default_permissions:
  contents: read
  pull_requests: write
  metadata: read
  administration: read
default_events:
  - push
  - pull_request
  - release
  - workflow_run
```

### GitLab

| Feature | Implementation |
|---------|---------------|
| Connection | OAuth 2.0 or Project/Group Access Token |
| Events | Push, Merge Request, Pipeline, Repository Update |
| API | GitLab REST API v4 |
| Self-hosted | Supported (GitLab CE/EE Server) |
| Marketplace | GitLab Integrations page |

### Bitbucket

| Feature | Implementation |
|---------|---------------|
| Connection | OAuth 2.0 or App Password |
| Events | repo:push, pullrequest:created/updated/merged |
| API | Bitbucket REST API 2.0 |
| Server/DC | Supported via webhook + REST |
| Marketplace | Atlassian Marketplace |

---

## Notification Channels

### Slack

```yaml
integration: slack
events:
  - flag.created (severity >= high)
  - flag.sla_breach
  - posture.score_drop (>5 pts)
  - remediation.pr_opened
channels:
  - configurable per severity tier
format: Block Kit with action buttons (View Flag, Assign, Create Fix PR)
```

**Setup:** OAuth to Slack workspace → select channels per event type.

### Microsoft Teams

```yaml
integration: teams
transport: Incoming Webhook or Bot Framework
events: same as Slack
format: Adaptive Cards
```

### Email

| Email Type | Frequency | Recipients |
|-----------|-----------|-----------|
| Critical flag alert | Immediate | Security Lead |
| Weekly digest | Monday 09:00 local | Configurable distribution |
| SLA breach warning | 24h before due | Assignee + Security Lead |
| Compliance export ready | On completion | Requestor |
| Auditor invite | On invite | Auditor (time-limited) |

### PagerDuty / Opsgenie

```yaml
integration: pagerduty
trigger: flag.created WHERE severity = critical AND repo.criticality = critical
action: Create incident with flag details + link
```

---

## Issue Trackers

### Jira

```yaml
integration: jira
actions:
  - auto_create_ticket: on flag.assigned
  - sync_status: flag.resolved → ticket.done
  - link_flag: bidirectional URL link
fields:
  - summary: flag.title
  - description: flag.explanation + citations
  - priority: mapped from severity
  - labels: [reposentinel, scanner_type]
```

### Linear

```yaml
integration: linear
actions: same pattern as Jira
auth: Linear API key or OAuth
```

---

## Identity Providers (SSO)

| Provider | Protocol | Tier |
|----------|----------|------|
| Okta | SAML 2.0 / OIDC | Enterprise |
| Azure AD | SAML 2.0 / OIDC | Enterprise |
| Google Workspace | OIDC | Business+ |
| OneLogin | SAML 2.0 | Enterprise |
| Custom SAML | SAML 2.0 | Enterprise |

**SSO group mapping:**
```
IdP Group "security-team" → security_lead
IdP Group "engineering"   → developer
IdP Group "compliance"    → compliance
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/reposentinel.yml
name: RepoSentinel Gate
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: reposentinel/scan-action@v1
        with:
          api-key: ${{ secrets.REPOSENTINEL_API_KEY }}
          fail-on: critical,high
```

### GitLab CI

```yaml
reposentinel-scan:
  stage: security
  image: reposentinel/ci-scanner:latest
  script:
    - reposentinel scan --api-key $REPOSENTINEL_API_KEY --fail-on critical,high
```

### Pre-Merge Gate

Block PR merge if:
- Critical or high severity flags introduced
- Secrets detected in diff
- License violation (copyleft in proprietary repo)

Configurable per repo in scanner_config.

---

## Marketplace Listings

### GitHub Marketplace

| Field | Value |
|-------|-------|
| Name | RepoSentinel AI |
| Category | Security / Code quality |
| Pricing | Free tier + paid plans |
| Install flow | GitHub App install → OAuth → repo selection |
| Listing URL | github.com/marketplace/reposentinel-ai |

### GitLab Integrations

| Field | Value |
|-------|-------|
| Category | Security |
| Install | OAuth → group/project selection |

### Atlassian Marketplace

| Field | Value |
|-------|-------|
| Product | Bitbucket integration |
| Category | Security & compliance |

---

## Billing

### Stripe Integration

```yaml
integration: stripe
products:
  - tier_team:     price_xxx (per-seat monthly)
  - tier_business: price_yyy (flat monthly)
events:
  - checkout.session.completed → provision org tier
  - customer.subscription.updated → update tier
  - invoice.payment_failed → grace period + downgrade warning
```

### Usage Metering

| Metric | Billed |
|--------|--------|
| Seats | Team tier |
| Repos (above free limit) | Team tier |
| M&A engagements | Business (per-engagement) |
| Compliance exports | Business+ |
| Token overage (Tier 2) | Enterprise (optional) |

---

## MCP & IDE Integrations

| IDE | Integration | Package |
|-----|------------|---------|
| Cursor | MCP server (stdio) | `@reposentinel/mcp-server` |
| VS Code | MCP server (stdio) | `@reposentinel/mcp-server` |
| Windsurf | MCP server (stdio) | `@reposentinel/mcp-server` |
| Custom agents | MCP server (SSE) | Remote endpoint |

### Cursor Hooks

```json
{
  "hooks": {
    "afterFileEdit": [{
      "command": "npx @reposentinel/cursor-hook report-edit"
    }]
  }
}
```

---

## Webhook API (Outbound)

Customers configure outbound webhooks for custom integrations:

```yaml
webhook:
  url: https://customer.com/hooks/reposentinel
  secret: whsec_...
  events:
    - flag.created
    - flag.resolved
    - posture.updated
    - remediation.pr_opened
    - compliance.export_ready
  retry: 3 attempts, exponential backoff
  signature: HMAC-SHA256 in X-RepoSentinel-Signature header
```

---

## Integration Roadmap

| Integration | Phase | Priority |
|------------|-------|----------|
| GitHub | MVP | P0 |
| Slack | MVP | P0 |
| GitHub Marketplace | MVP | P0 |
| Jira | V1 | P1 |
| GitLab | V1 | P1 |
| Bitbucket | V1 | P1 |
| Email digests | V1 | P1 |
| Linear | V1 | P2 |
| MCP server (full) | V1 | P1 |
| Teams | V2 | P2 |
| PagerDuty | V2 | P2 |
| SSO (SAML) | V2 | P1 |
| GitLab Marketplace | V2 | P2 |
| Atlassian Marketplace | V2 | P2 |
| GitHub Actions gate | V1 | P1 |
| Cursor hooks | V2 | P2 |
