# Security Architecture

Security design for RepoSentinel AI — platform security, data protection, and customer trust.

---

## Threat Model

### Assets to Protect

| Asset | Sensitivity | Impact if Compromised |
|-------|------------|----------------------|
| Customer source code (diffs) | Critical | IP theft, vulnerability exposure |
| VCS OAuth tokens | Critical | Full repo access |
| Security findings & flags | High | Misleading security posture |
| Knowledge base content | High | Institutional knowledge leak |
| Compliance evidence | High | Audit failure, regulatory risk |
| LLM prompts/responses | Medium | Context leakage |
| User PII (email, name) | Medium | Privacy violation |

### Threat Actors

| Actor | Motivation | Vector |
|-------|-----------|--------|
| External attacker | Data theft, ransom | API exploitation, credential theft |
| Malicious insider | Sabotage, data exfil | Over-privileged access |
| Compromised AI agent | Unintended changes | MCP tool abuse, prompt injection |
| Tenant A attacking Tenant B | Cross-tenant data access | IDOR, RLS bypass |
| Supply chain | Backdoored dependency | Scanner pipeline compromise |

---

## Defense in Depth

```
┌─────────────────────────────────────────────────────────┐
│ Layer 7: Application Security                            │
│ Input validation, RBAC, audit logging, CSP headers       │
├─────────────────────────────────────────────────────────┤
│ Layer 6: Agent Governance                                │
│ Budget caps, schema validation, draft-only PRs             │
├─────────────────────────────────────────────────────────┤
│ Layer 5: API Security                                    │
│ JWT, API key scoping, rate limiting, WAF                 │
├─────────────────────────────────────────────────────────┤
│ Layer 4: Data Security                                   │
│ Encryption at rest/transit, RLS, short-lived diffs       │
├─────────────────────────────────────────────────────────┤
│ Layer 3: Network Security                                │
│ VPC isolation, security groups, private subnets          │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Infrastructure Security                         │
│ IAM least privilege, secrets manager, hardened AMIs      │
├─────────────────────────────────────────────────────────┤
│ Layer 1: Physical / Cloud Provider                       │
│ AWS SOC 2, ISO 27001 compliance                          │
└─────────────────────────────────────────────────────────┘
```

---

## Authentication & Authorization

### SaaS Authentication

| Method | Implementation |
|--------|---------------|
| SSO (Enterprise) | SAML 2.0 / OIDC via Auth0 or custom |
| OAuth (Developers) | GitHub, GitLab OAuth for login + VCS connect |
| API Keys | `rsl_live_*` / `rsl_test_*` prefixed, scoped, rotatable |
| MFA | Required for Owner/Admin roles (Enterprise) |

### Token Lifecycle

```
Access Token:  1 hour TTL, JWT signed RS256
Refresh Token: 30 days TTL, rotated on use, revocable
API Key:       No expiry (Enterprise: configurable), revocable instantly
Auditor Token: Time-limited (engagement duration + 7 days)
```

### RBAC Enforcement

- Every API request: extract `tenant_id` from JWT → set Postgres `app.tenant_id`
- Row-Level Security on all tenant tables
- Application-level permission check before destructive operations
- Agent service accounts: scoped to single agent type, no UI access

---

## Data Protection

### Encryption

| Data | At Rest | In Transit |
|------|---------|-----------|
| Database (Aurora) | AES-256 (AWS KMS) | TLS 1.3 |
| S3 artifacts | SSE-KMS | TLS 1.3 |
| Redis/Valkey | Encryption at rest enabled | TLS in transit |
| Secrets (tokens) | AWS Secrets Manager | Never in logs/env files |
| Backups | KMS-encrypted | N/A |

### Data Minimization

| Data Type | Retention | Rationale |
|-----------|-----------|-----------|
| Git diffs | 24 hours (S3 TTL) | Process and discard |
| Full file contents | Never stored | Diff-only processing |
| Findings | 1–7 years (tier-dependent) | Audit requirement |
| Agent prompts | 90 days | Debugging, no long-term storage |
| Audit logs | 1–7 years | Compliance |

### Tenant Isolation

```sql
-- Every query automatically scoped
SET app.tenant_id = 'tenant_uuid_from_jwt';

-- RLS policy example
CREATE POLICY tenant_isolation ON flags
  USING (tenant_id = current_setting('app.tenant_id')::UUID);
```

Additional checks:
- `tenant_id` in every application query (defense in depth beyond RLS)
- MSP tenants: separate schema or strict `parent_msp_id` hierarchy
- Cross-tenant API calls return 404 (not 403) to prevent enumeration

---

## Application Security

### API Security

| Control | Implementation |
|---------|---------------|
| Rate limiting | Per-org, per-IP, per-API-key (Redis sliding window) |
| Input validation | Pydantic (FastAPI) + Zod (Node gateway) |
| SQL injection | Parameterized queries only (SQLAlchemy) |
| XSS | CSP headers, React auto-escaping, DOMPurify for rich text |
| CSRF | SameSite cookies + CSRF tokens for web |
| CORS | Allowlist per tenant custom domain |

### Webhook Security

```
GitHub:   X-Hub-Signature-256 (HMAC-SHA256)
GitLab:   X-Gitlab-Token (shared secret)
Bitbucket: X-Hook-UUID + IP allowlist
Outbound: X-RepoSentinel-Signature (HMAC-SHA256, customer secret)
```

### Dependency Security

- Dependabot / Snyk on all RepoSentinel repos (dogfooding)
- Container image scanning in CI (Trivy)
- SBOM generated per release
- No critical CVEs in production dependencies

---

## Agent & LLM Security

### Prompt Injection Defenses

| Vector | Defense |
|--------|---------|
| Malicious code in diff | Scanners run in sandbox; agents receive structured findings only |
| KB poisoning via PR | Knowledge-Curator validates source; human-review for critical repos |
| Query injection | Retrieval boundaries; no system prompt override via user input |
| MCP tool abuse | Scoped API keys; write tools require explicit permission |

### LLM Data Handling

- Customer code never sent to Tier 2 frontier API without explicit Enterprise opt-in
- Self-hosted vLLM (Tier 0/1) processes all routine agent work in customer region
- Prompt/response logs: 90-day retention, access restricted to ops + customer (Enterprise)
- No training on customer data (contractual + technical: no data export to model providers)

### Remediation Safety

```
1. Remediation Agent output → JSON schema validation
2. Files outside allowlist → flagged for human review, not auto-committed
3. PR created as DRAFT always
4. No force-push, no branch protection override
5. Audit log: remediation.pr_created with full agent output hash
```

---

## Infrastructure Security

### Network Architecture (SaaS)

```
Internet → CloudFront (WAF) → ALB (TLS termination)
  → Private subnets: EKS pods (no public IPs)
  → Private subnets: Aurora, MSK, ElastiCache
  → NAT Gateway for outbound only (VCS APIs, frontier LLM)
  → VPC endpoints for S3, Secrets Manager (no internet for AWS services)
```

### IAM

- EKS pods: IRSA (IAM Roles for Service Accounts) — no static credentials
- Scanner workers: read-only S3, write findings topic only
- Remediation service: VCS API write scoped to connected repos only
- Principle of least privilege on all roles

### Secrets Management

```
VCS OAuth tokens    → AWS Secrets Manager, per-tenant namespace
API keys (internal) → Secrets Manager, rotated quarterly
Database credentials → Secrets Manager, auto-rotation enabled
LLM API keys        → Secrets Manager, separate per environment
```

---

## Compliance & Certifications

### Platform Compliance (RepoSentinel as Vendor)

| Framework | Status | Notes |
|-----------|--------|-------|
| SOC 2 Type II | Target V2 | Control design from day one |
| ISO 27001 | Target V2 | |
| GDPR | Required | EU data residency option |
| DPA | Available | Enterprise tier |

### Customer-Facing Compliance Features

- Pre-built SOC 2 / ISO 27001 / PCI-DSS control mappings
- Auditor-ready evidence package export
- Time-limited auditor access (read-only role)
- Audit log export (7-year retention, Enterprise)

---

## Incident Response

### Severity Classification

| Severity | Example | Response Time |
|----------|---------|--------------|
| P1 | Cross-tenant data leak | 15 minutes |
| P2 | VCS token compromise | 1 hour |
| P3 | Scanner pipeline failure | 4 hours |
| P4 | Non-critical vulnerability in platform | 72 hours |

### Playbooks

1. **Token compromise:** Revoke all tokens for affected tenant, force re-auth, notify customer within 1 hour
2. **Data leak:** Isolate affected service, preserve logs, notify within 72 hours (GDPR)
3. **Agent misbehavior:** Disable agent type globally, rollback affected PRs, post-mortem

---

## Security Testing

| Test | Frequency |
|------|-----------|
| SAST (CodeQL) | Every PR |
| DAST (OWASP ZAP) | Weekly staging |
| Penetration test | Annual (third-party) |
| Tenant isolation test | Every release |
| RBAC regression tests | Every PR |
| Dependency audit | Daily |

---

## Customer Security Features

| Feature | Tier |
|---------|------|
| SSO / SAML | Business+ |
| MFA enforcement | Business+ |
| IP allowlisting | Enterprise |
| VPC / self-hosted | Enterprise |
| Custom data residency | Enterprise |
| Auditor access | Business+ |
| API key scoping | All tiers |
| Audit log export | Team+ |
