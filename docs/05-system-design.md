# System Design

Detailed component design, service boundaries, data flows, and scaling strategy.

---

## Service Map

```
reposentinel/
├── apps/
│   ├── web/                    # Next.js dashboard + landing page
│   ├── api-gateway/            # Node.js BFF, auth, rate limiting
│   └── mcp-server/             # MCP protocol server
├── services/
│   ├── connector-github/       # GitHub webhook + API adapter
│   ├── connector-gitlab/       # GitLab webhook + API adapter
│   ├── connector-bitbucket/    # Bitbucket webhook + API adapter
│   ├── ingestion/              # Event normalization + bus publish
│   ├── scanner-orchestrator/   # Routes diffs to scanner workers
│   ├── scanner-secrets/        # Secret detection worker
│   ├── scanner-sast/           # SAST worker (multi-language)
│   ├── scanner-sca/            # SBOM + CVE matching worker
│   ├── scanner-iac/            # IaC policy worker
│   ├── scanner-drift/          # Architecture drift worker
│   ├── severity-engine/        # Rule-based severity computation
│   ├── flag-service/           # Flag CRUD + lifecycle state machine
│   ├── agent-orchestrator/     # LangGraph adapter + job dispatch
│   ├── remediation-service/    # Draft PR creation via VCS APIs
│   ├── knowledge-service/      # Embedding, retrieval, curation
│   ├── posture-service/        # Composite score computation
│   ├── compliance-service/     # Control mapping + evidence export
│   ├── engagement-service/     # M&A due diligence engagements
│   ├── notification-service/   # Slack, Jira, email, webhooks out
│   ├── billing-service/          # Stripe integration, tier enforcement
│   └── tenant-service/           # Multi-tenant provisioning, white-label
├── packages/
│   ├── shared-types/           # TypeScript + Python shared schemas
│   ├── event-schema/           # Canonical event definitions (Avro/JSON)
│   ├── scanner-sdk/            # Common finding schema for scanners
│   └── agent-contracts/          # Agent I/O JSON schemas
└── infra/
    ├── terraform/              # AWS infrastructure
    └── helm/                     # Self-hosted chart
```

---

## Core Data Flows

### Flow 1 — Commit to Flag (Happy Path)

```
1. Developer pushes to GitHub
2. connector-github receives webhook → validates signature
3. ingestion normalizes → publishes ChangeEvent to kafka.topic.changes
4. scanner-orchestrator consumes → fetches diff → fans out to scanners
5. Each scanner emits FindingEvents to kafka.topic.findings
6. severity-engine computes severity per finding (rule v3.2.1)
7. flag-service: new finding + severity >= medium → open Flag
8. agent-orchestrator dispatches Triage Agent (Tier 0, budget: 8k tokens)
9. Triage returns { signal: true, noise_reason: null }
10. agent-orchestrator dispatches Explainer Agent (Tier 1)
11. Explainer returns { summary, remediation_steps, citations[] }
12. flag-service attaches explanation to Flag
13. notification-service → Slack #security-alerts
14. Dashboard WebSocket pushes flag update to connected clients
```

**Latency target:** Flag visible in dashboard within **60 seconds** of push (p95).

### Flow 2 — Auto-Remediation

```
1. Security Lead clicks "Create fix PR" on SCA flag (CVE-2024-1234)
2. API validates permission: approve_auto_fix (security_lead role)
3. remediation-service dispatches Remediation Agent
4. Agent reads: finding + diff + package.json + lockfile context
5. Agent outputs: { branch_name, files[], commit_message, pr_title, pr_body }
6. remediation-service calls GitHub API:
   - Create branch fix/cve-2024-1234-abc123
   - Commit updated package.json + lockfile
   - Open draft PR with agent-generated description
7. flag-service: status → in_remediation, link pr_url
8. Audit log: flag.approve_remediation by user_xyz
```

**Human gate:** PR is always **draft** — never auto-merged.

### Flow 3 — Knowledge Query

```
1. Developer asks: "Why does payment-service retry 3 times?"
2. knowledge-service embeds query → hybrid search (vector + BM25)
3. Top-k chunks retrieved with metadata (repo, file, commit, PR)
4. Query Agent receives: query + chunks only (no raw repo)
5. Agent returns: { answer, citations[], confidence: 0.87 }
6. If confidence < 0.6 → escalate to Tier 2 with expanded retrieval
7. Response rendered with inline citation cards in UI
```

### Flow 4 — Posture Score Computation (Daily Batch)

```
1. posture-service cron (02:00 UTC per org timezone)
2. For each repo: weighted score from open flags by severity
   score = 100 - Σ(severity_weight × open_flag_count) + remediation_bonus
3. Roll up: repo → team → org
4. Store daily snapshot in posture_history table
5. Compute 90-day trend + peer benchmark percentile
6. Cache in Redis for dashboard (TTL: 1 hour)
```

### Flow 5 — M&A Due Diligence Engagement

```
1. Consultancy creates Engagement (target_org, repo_list, expiry_date)
2. engagement-service provisions scoped access tokens
3. Full baseline scan (not delta-only) on all target repos
4. posture-service computes engagement-scoped score
5. compliance-service generates control gap analysis
6. Report generator produces PDF + web report (white-label if configured)
7. Engagement auto-expires; all scoped tokens revoked
```

---

## State Machines

### Flag Lifecycle

```
                    ┌──────────┐
                    │   NEW    │
                    └────┬─────┘
                         │ triage (human or auto)
                    ┌────▼─────┐
              ┌─────┤ TRIAGED  ├─────┐
              │     └────┬─────┘     │
              │ dismiss  │ assign    │ escalate
         ┌────▼───┐ ┌───▼──────┐ ┌──▼───────┐
         │CLOSED  │ │ ASSIGNED │ │ESCALATED │
         │dismissed│ └───┬──────┘ └──────────┘
         └────────┘     │ remediate
                   ┌────▼──────────┐
                   │IN_REMEDIATION │
                   └────┬──────────┘
                        │ verify
                   ┌────▼─────┐
                   │ RESOLVED │
                   └────┬─────┘
                        │ re-scan confirms
                   ┌────▼─────┐
                   │ VERIFIED │
                   └──────────┘
```

### Agent Run Lifecycle

```
QUEUED → RUNNING → COMPLETED | FAILED | BUDGET_EXCEEDED | TIMEOUT
                        │
                        └── checkpoint saved to agent_runs table
                            (resumable on FAILED if retryable)
```

---

## Scaling Strategy

### Horizontal Scaling

| Component | Scale Trigger | Strategy |
|-----------|--------------|----------|
| Connectors | Webhook volume | Stateless pods, HPA on CPU |
| Scanner workers | Kafka lag on findings topic | Consumer group auto-scale |
| Agent workers | Celery queue depth | Worker pool per agent type |
| API | Request rate | ALB + pod HPA |
| vLLM | Token throughput | GPU node pool, request batching |

### Cost Controls

| Control | Mechanism |
|---------|-----------|
| Per-repo daily token budget | Hard stop + alert at 80% |
| Per-org monthly budget | Throttle Tier 1/2, Tier 0 continues |
| Delta-only processing | Full scan only on onboarding + weekly cadence |
| Finding deduplication | One agent call per unique finding hash |
| Prompt caching | Stable context cached across invocations |

### Performance Targets

| Metric | Target |
|--------|--------|
| Webhook → flag (p95) | < 60s |
| Dashboard page load | < 200ms (cached) |
| Knowledge query (p95) | < 3s |
| Posture score refresh | < 5s (from cache) |
| Compliance export (1000 flags) | < 30s |
| System availability | 99.9% (SaaS) |

---

## Integration Points

### Inbound

| Source | Protocol | Auth |
|--------|----------|------|
| GitHub | Webhooks + REST/GraphQL | GitHub App JWT |
| GitLab | Webhooks + REST | OAuth / PAT |
| Bitbucket | Webhooks + REST | OAuth |
| Stripe | Webhooks | Signature verification |
| SSO | SAML/OIDC | IdP certificate |

### Outbound

| Target | Protocol | Use |
|--------|----------|-----|
| GitHub/GitLab/Bitbucket | REST | Create branches, PRs, comments |
| Slack | Web API | Alerts, digests |
| Jira/Linear | REST | Ticket creation |
| SMTP | TLS | Weekly digests, auditor invites |
| S3 | AWS SDK | Report storage, evidence packages |

---

## Error Handling & Resilience

| Failure | Handling |
|---------|----------|
| VCS API rate limit | Exponential backoff + queue delay |
| Scanner timeout | Retry 2x, then mark finding as `scan_incomplete` |
| Agent budget exceeded | Save checkpoint, notify admin, no partial write to flag |
| Kafka consumer crash | Offset commit after processing; at-least-once delivery |
| vLLM unavailable | Fallback to hosted Tier 0 API; alert ops |
| Database failover | Aurora multi-AZ automatic failover (< 30s) |

---

## Security Design Decisions

1. **Tenant isolation:** Postgres RLS + application-level tenant_id checks on every query
2. **Code never stored long-term:** Diffs processed in-memory or short-lived S3 (24h TTL)
3. **Agent sandbox:** Agents receive findings + diffs only, never shell access to repos
4. **Remediation PRs:** Always draft, always require human merge approval
5. **API keys:** Scoped to single permission set, rotatable, expiring
6. **Audit log:** Append-only table, no DELETE permission for application role
