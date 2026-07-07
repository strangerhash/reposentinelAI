# Agent Framework

Specification for RepoSentinel AI's governed agentic layer — orchestration, contracts, and runtime behavior.

---

## Design Principles

1. **Small, typed agents** — narrow responsibility per agent, not one general-purpose loop
2. **Deterministic state ownership** — Postgres owns run state, not the LLM or LangGraph memory
3. **Budget-capped invocations** — hard token limits per run; exceed → human escalation, not truncation
4. **Structured I/O only** — JSON schema validated inputs and outputs; no freeform text in flag records
5. **Diff-scoped context** — agents never receive full repos, only diffs + bounded neighbor context

---

## Orchestration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Agent Orchestrator                        │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Job Queue   │  │ State Store  │  │ Budget Enforcer│  │
│  │ (Celery)    │  │ (Postgres)   │  │ (per-run caps) │  │
│  └──────┬──────┘  └──────────────┘  └────────────────┘  │
│         │                                                │
│  ┌──────▼──────────────────────────────────────────┐    │
│  │ LangGraph Adapter (thin — flow only, no state)  │    │
│  │  nodes: triage → correlate → explain → remediate│    │
│  └──────┬──────────────────────────────────────────┘    │
│         │                                                │
│  ┌──────▼──────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Tier Router │→ │ vLLM Tier 0 │  │ Frontier Tier 2 │ │
│  └─────────────┘  │ vLLM Tier 1 │  └─────────────────┘ │
│                   └─────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### 1. Triage Agent

**Purpose:** Classify new findings as signal vs. noise before a flag is opened.

| Field | Value |
|-------|-------|
| Trigger | `FindingCreated` event (per change batch) |
| Model | Tier 0 (Haiku-class) |
| Budget | 8,000 in / 500 out tokens |
| Timeout | 30 seconds |

**Input Schema:**
```json
{
  "change_id": "uuid",
  "findings": [{
    "scanner": "sca",
    "rule_id": "cve-2024-1234",
    "severity": "high",
    "file_path": "package.json",
    "metadata": {}
  }],
  "repo_context": {
    "criticality_tier": "critical",
    "recent_suppressions": []
  }
}
```

**Output Schema:**
```json
{
  "classifications": [{
    "finding_id": "uuid",
    "signal": true,
    "noise_reason": null,
    "advisory_priority": "high",
    "confidence": 0.92
  }]
}
```

**Note:** `advisory_priority` is suggestion only. Final severity from severity-engine rules.

---

### 2. Correlation Agent

**Purpose:** Link related findings across repos into a single flag.

| Field | Value |
|-------|-------|
| Trigger | Scheduled (every 15 min) + on-demand |
| Model | Tier 0 |
| Budget | 16,000 in / 1,000 out |
| Timeout | 120 seconds |

**Input:** Batch of unlinked findings with shared fingerprints (e.g. same CVE across 12 services)

**Output:**
```json
{
  "correlations": [{
    "root_cause": "lodash@4.17.20 vulnerable across 12 repos",
    "finding_ids": ["f1", "f2", "..."],
    "suggested_flag_title": "CVE-2024-1234 — lodash (12 repos)",
    "merge_into_flag_id": null
  }]
}
```

---

### 3. Explainer Agent

**Purpose:** Generate human-readable flag summary and remediation steps.

| Field | Value |
|-------|-------|
| Trigger | Flag opened or severity escalated |
| Model | Tier 1 (Sonnet-class) |
| Budget | 12,000 in / 2,000 out |
| Timeout | 60 seconds |

**Output:**
```json
{
  "summary": "lodash 4.17.20 has a known prototype pollution vulnerability (CVE-2024-1234)...",
  "remediation_steps": [
    { "step": 1, "action": "Upgrade lodash to >=4.17.21", "automated": true, "risk": "low" },
    { "step": 2, "action": "Run npm audit fix", "automated": true, "risk": "low" }
  ],
  "citations": [
    { "type": "file", "path": "package.json", "line": 42, "commit": "abc123" },
    { "type": "cve", "id": "CVE-2024-1234", "url": "https://nvd.nist.gov/..." }
  ],
  "business_impact": "Payment service processes card data — high exposure if exploited."
}
```

---

### 4. Remediation Agent

**Purpose:** Generate draft PR with automated fix.

| Field | Value |
|-------|-------|
| Trigger | User clicks "Create fix PR" (permission-gated) |
| Model | Tier 1 |
| Budget | 16,000 in / 4,000 out |
| Timeout | 180 seconds |

**Supported fix types (MVP → V1):**

| Fix Type | Automation Level |
|----------|-----------------|
| Dependency bump (SCA) | Full — package.json + lockfile |
| IaC config correction | Full — Terraform/K8s manifest |
| Secret rotation guide | Partial — PR with rotation instructions + placeholder |
| SAST fix | Advisory only (V1) — suggested patch in PR description |
| License violation | Partial — dependency replacement suggestion |

**Output:**
```json
{
  "branch_name": "reposentinel/fix/cve-2024-1234-abc123",
  "commit_message": "fix(deps): upgrade lodash to 4.17.21 [CVE-2024-1234]",
  "pr_title": "fix: resolve CVE-2024-1234 in lodash",
  "pr_body": "## Auto-generated by RepoSentinel AI\n\n...",
  "files": [
    { "path": "package.json", "content": "...", "operation": "modify" },
    { "path": "package-lock.json", "content": "...", "operation": "modify" }
  ],
  "draft": true,
  "confidence": 0.95
}
```

**Safety gates:**
- PR is always `draft: true`
- Never merges automatically
- Files outside allowlist (package.json, *.lock, *.tf, *.yaml) require human review flag

---

### 5. Knowledge-Curator Agent

**Purpose:** Maintain knowledge base from merged PRs, resolved flags, and incidents.

| Field | Value |
|-------|-------|
| Trigger | Batched post-merge (hourly) |
| Model | Tier 1 |
| Budget | 20,000 in / 3,000 out |
| Timeout | 300 seconds |

**Output:**
```json
{
  "knowledge_units": [{
    "source_type": "pr",
    "source_ref": "pr:42",
    "title": "Auth retry logic rationale",
    "content": "The team chose 3 retries based on Stripe webhook SLA requirements...",
    "tags": ["auth", "payment-service", "reliability"],
    "supersedes_unit_id": null
  }]
}
```

---

### 6. Query Agent

**Purpose:** Answer user questions with citations from knowledge base and findings.

| Field | Value |
|-------|-------|
| Trigger | User query via API or MCP |
| Model | Tier 0 → escalate to Tier 2 if confidence < 0.6 |
| Budget | 8,000 in / 2,000 out (Tier 0); 32,000 in / 4,000 out (Tier 2) |
| Timeout | 45s (Tier 0) / 120s (Tier 2) |

**Modes:**
- `default` — all users
- `onboarding` — simplified language, more context, common "getting started" topics prioritized

**Output:**
```json
{
  "answer": "Payment-service retries 3 times because...",
  "confidence": 0.87,
  "citations": [{ "type": "code", "path": "src/http/client.ts", "lines": "45-52" }],
  "escalated": false,
  "low_confidence_disclaimer": null
}
```

If `confidence < 0.6`:
```json
{
  "answer": "I found partial information but cannot answer with high confidence...",
  "confidence": 0.42,
  "escalated": true,
  "low_confidence_disclaimer": "Retrieval covered only 2 of 5 payment-service modules."
}
```

---

## Tier Routing Logic

```python
def route_model(agent_type: str, context: dict) -> int:
    if agent_type == "query" and context.get("confidence_after_tier0", 1.0) < 0.6:
        return 2  # frontier
    if context.get("severity") == "critical" and context.get("ambiguous", False):
        return 2
    if agent_type in ("triage", "correlation"):
        return 0
    if agent_type in ("explainer", "remediation", "knowledge_curator"):
        return 1
    return 0
```

---

## Prompt Architecture

### Stable Context (Cached)

```
- System instructions (agent role, output schema)
- Organization scanner config summary
- Rule catalog excerpt (relevant rules only)
- Repo conventions (from knowledge base, if exists)
```

### Variable Context (Per-Invocation)

```
- Specific findings / diff hunks
- Retrieved knowledge chunks (top-k)
- User query (Query Agent only)
```

### Caching Strategy

| Block | Cache TTL | Savings |
|-------|-----------|---------|
| System prompt per agent | 24 hours | ~70% input tokens |
| Rule catalog per scanner | 1 hour | ~50% on triage |
| Repo conventions | Until repo config changes | ~30% on explain |

---

## Agent Run State Machine

```
QUEUED
  → RUNNING (checkpoint: input_validated)
  → RUNNING (checkpoint: llm_response_received)
  → RUNNING (checkpoint: output_validated)
  → COMPLETED

Failure paths:
  → BUDGET_EXCEEDED (no partial write)
  → TIMEOUT (retryable once)
  → FAILED (schema validation error — logged, alert ops)
  → ESCALATED_TO_HUMAN (Tier 2 also low confidence)
```

---

## Human-in-the-Loop Checkpoints

| Checkpoint | Agent | Human Action |
|------------|-------|-------------|
| Remediation PR review | Remediation | Merge or close draft PR |
| Critical flag triage | Triage + human | Security Lead confirms severity |
| Low-confidence query | Query | User sees disclaimer, can escalate |
| Compliance export | System | Compliance Officer reviews before send |

---

## Monitoring & Observability

Per agent run, emit metrics:

```
agent.run.duration_ms{agent=triage, tier=0}
agent.run.tokens_in{agent=triage}
agent.run.tokens_out{agent=triage}
agent.run.status{agent=triage, status=completed}
agent.run.cost_usd{agent=triage}
agent.output.confidence{agent=query}
```

Alerts:
- `agent.run.budget_exceeded` rate > 5% per hour
- `agent.run.timeout` rate > 2% per hour
- `agent.output.schema_validation_failed` — any occurrence → page ops
