# Data Model

PostgreSQL schema design for RepoSentinel AI. All tables include `tenant_id` for multi-tenant isolation with Row-Level Security.

---

## Entity Relationship Overview

```
organizations ──┬── users ── user_roles
                ├── repositories ── changes ── findings
                │                    └── scan_runs
                ├── flags ── flag_findings ── findings
                │     └── flag_events (audit)
                ├── knowledge_units ── embeddings
                ├── posture_snapshots
                ├── compliance_controls ── control_mappings
                ├── engagements (M&A)
                ├── mcp_servers ── mcp_permissions
                ├── agent_runs
                └── integrations
```

---

## Core Tables

### organizations

```sql
CREATE TABLE organizations (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  slug          TEXT UNIQUE NOT NULL,
  plan_tier     TEXT NOT NULL DEFAULT 'free',  -- free|team|business|enterprise
  settings      JSONB DEFAULT '{}',
  white_label   JSONB DEFAULT NULL,  -- { logo_url, accent_color, custom_domain }
  parent_msp_id UUID REFERENCES organizations(id),  -- for MSP client tenants
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);
```

### users

```sql
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL REFERENCES organizations(id),
  email         TEXT NOT NULL,
  name          TEXT,
  avatar_url    TEXT,
  auth_provider TEXT,  -- sso|github|gitlab|magic_link
  external_id   TEXT,
  last_login_at TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT now(),
  UNIQUE(tenant_id, email)
);
```

### user_roles

```sql
CREATE TABLE user_roles (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  UUID NOT NULL REFERENCES organizations(id),
  user_id    UUID NOT NULL REFERENCES users(id),
  role       TEXT NOT NULL,  -- owner|admin|security_lead|compliance|eng_manager|developer|auditor
  team_id    UUID REFERENCES teams(id),  -- NULL = org-wide
  granted_by UUID REFERENCES users(id),
  expires_at TIMESTAMPTZ,  -- for auditor time-limited access
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### repositories

```sql
CREATE TABLE repositories (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         UUID NOT NULL REFERENCES organizations(id),
  platform          TEXT NOT NULL,  -- github|gitlab|bitbucket
  external_id       TEXT NOT NULL,
  name              TEXT NOT NULL,
  full_name         TEXT NOT NULL,  -- org/repo
  url               TEXT NOT NULL,
  default_branch    TEXT DEFAULT 'main',
  criticality_tier  TEXT DEFAULT 'medium',  -- critical|high|medium|low
  team_id           UUID REFERENCES teams(id),
  scanner_config    JSONB DEFAULT '{}',
  last_scan_at      TIMESTAMPTZ,
  is_active         BOOLEAN DEFAULT true,
  created_at        TIMESTAMPTZ DEFAULT now(),
  UNIQUE(tenant_id, platform, external_id)
);
```

### changes

```sql
CREATE TABLE changes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL,
  repository_id UUID NOT NULL REFERENCES repositories(id),
  event_type    TEXT NOT NULL,
  sha           TEXT NOT NULL,
  ref           TEXT,
  author_email  TEXT,
  is_pr         BOOLEAN DEFAULT false,
  pr_number     INT,
  files_changed TEXT[],
  diff_s3_key   TEXT,  -- short-lived, 24h TTL
  occurred_at   TIMESTAMPTZ NOT NULL,
  received_at   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_changes_repo_time ON changes(repository_id, occurred_at DESC);
```

### findings

```sql
CREATE TABLE findings (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL,
  repository_id   UUID NOT NULL REFERENCES repositories(id),
  change_id       UUID REFERENCES changes(id),
  scanner         TEXT NOT NULL,  -- secrets|sast|sca|iac|license|drift
  rule_id         TEXT NOT NULL,
  severity        TEXT NOT NULL,  -- critical|high|medium|low|info
  severity_rule_v TEXT NOT NULL,  -- rule version for audit
  title           TEXT NOT NULL,
  description     TEXT,
  file_path       TEXT,
  line_start      INT,
  line_end        INT,
  fingerprint     TEXT NOT NULL,  -- dedup hash
  metadata        JSONB DEFAULT '{}',
  first_seen_at   TIMESTAMPTZ DEFAULT now(),
  last_seen_at    TIMESTAMPTZ DEFAULT now(),
  status          TEXT DEFAULT 'open'  -- open|suppressed|resolved
);
CREATE INDEX idx_findings_fingerprint ON findings(tenant_id, fingerprint);
CREATE INDEX idx_findings_severity ON findings(tenant_id, severity, status);
```

### flags

```sql
CREATE TABLE flags (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         UUID NOT NULL,
  repository_id     UUID NOT NULL REFERENCES repositories(id),
  title             TEXT NOT NULL,
  severity          TEXT NOT NULL,
  severity_rule_v   TEXT NOT NULL,
  status            TEXT NOT NULL DEFAULT 'new',
  assignee_id       UUID REFERENCES users(id),
  explanation       TEXT,  -- agent-generated
  remediation_steps JSONB,
  remediation_pr_url TEXT,
  sla_due_at        TIMESTAMPTZ,
  created_at        TIMESTAMPTZ DEFAULT now(),
  updated_at        TIMESTAMPTZ DEFAULT now(),
  resolved_at       TIMESTAMPTZ
);
```

### flag_events (audit trail)

```sql
CREATE TABLE flag_events (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  UUID NOT NULL,
  flag_id    UUID NOT NULL REFERENCES flags(id),
  actor_type TEXT NOT NULL,  -- user|agent|system|api_key
  actor_id   TEXT NOT NULL,
  action     TEXT NOT NULL,
  from_status TEXT,
  to_status   TEXT,
  metadata   JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### knowledge_units

```sql
CREATE TABLE knowledge_units (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL,
  repository_id UUID REFERENCES repositories(id),
  source_type   TEXT NOT NULL,  -- code|pr|incident|adr|flag_resolution
  source_ref    TEXT,  -- commit sha, pr number, etc.
  title         TEXT,
  content       TEXT NOT NULL,
  chunk_index   INT DEFAULT 0,
  metadata      JSONB DEFAULT '{}',
  version       INT DEFAULT 1,
  is_stale      BOOLEAN DEFAULT false,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE embeddings (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  embedding         vector(1536),  -- pgvector
  model             TEXT NOT NULL,
  created_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_embeddings_vector ON embeddings
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### posture_snapshots

```sql
CREATE TABLE posture_snapshots (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL,
  scope_type    TEXT NOT NULL,  -- org|team|repo
  scope_id      UUID NOT NULL,
  score         INT NOT NULL CHECK (score >= 0 AND score <= 100),
  trend_90d     INT,  -- point change over 90 days
  peer_percentile INT,
  breakdown     JSONB,  -- { critical: 2, high: 5, auto_fixed: 12 }
  computed_at   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_posture_scope ON posture_snapshots(tenant_id, scope_type, scope_id, computed_at DESC);
```

### compliance_controls

```sql
CREATE TABLE compliance_frameworks (
  id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,  -- SOC2|ISO27001|PCI_DSS
  version TEXT NOT NULL
);

CREATE TABLE compliance_controls (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  framework_id UUID NOT NULL REFERENCES compliance_frameworks(id),
  control_id   TEXT NOT NULL,  -- e.g. CC6.1
  title        TEXT NOT NULL,
  description  TEXT
);

CREATE TABLE control_mappings (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  control_id   UUID NOT NULL REFERENCES compliance_controls(id),
  scanner      TEXT NOT NULL,
  rule_id      TEXT NOT NULL,
  mapping_type TEXT NOT NULL  -- direct|partial|compensating
);
```

### engagements (M&A Due Diligence)

```sql
CREATE TABLE engagements (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL REFERENCES organizations(id),
  name          TEXT NOT NULL,
  target_org    TEXT,
  status        TEXT DEFAULT 'active',  -- active|completed|expired
  repo_ids      UUID[],
  report_s3_key TEXT,
  white_label   JSONB,
  expires_at    TIMESTAMPTZ NOT NULL,
  created_by    UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT now()
);
```

### agent_runs

```sql
CREATE TABLE agent_runs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL,
  agent_type    TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'queued',
  input_ref     JSONB,  -- { flag_id, change_id, etc. }
  output        JSONB,
  model_tier    INT,
  tokens_in     INT DEFAULT 0,
  tokens_out    INT DEFAULT 0,
  budget_limit  INT,
  error         TEXT,
  started_at    TIMESTAMPTZ,
  completed_at  TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT now()
);
```

### mcp_servers

```sql
CREATE TABLE mcp_servers (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL,
  name          TEXT NOT NULL,
  server_type   TEXT NOT NULL,  -- reposentinel|external
  endpoint      TEXT,
  permissions   JSONB NOT NULL,  -- scoped tool list
  status        TEXT DEFAULT 'active',
  last_seen_at  TIMESTAMPTZ,
  created_by    UUID REFERENCES users(id),
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ai_agent_activity (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL,
  repository_id UUID REFERENCES repositories(id),
  agent_name    TEXT NOT NULL,  -- cursor|copilot|custom
  mcp_server_id UUID REFERENCES mcp_servers(id),
  change_id     UUID REFERENCES changes(id),
  files_touched TEXT[],
  permissions_used JSONB,
  risk_level    TEXT,
  detected_at   TIMESTAMPTZ DEFAULT now()
);
```

---

## Row-Level Security

```sql
ALTER TABLE flags ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON flags
  USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- Set per-request: SET app.tenant_id = 'uuid';
```

---

## Indexing Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| findings | (tenant_id, fingerprint) | Dedup |
| findings | (tenant_id, severity, status) | Risk register filters |
| changes | (repository_id, occurred_at DESC) | Recent activity |
| posture_snapshots | (tenant_id, scope_type, scope_id, computed_at DESC) | Trend queries |
| embeddings | IVFFlat on vector | Similarity search |
| flag_events | (flag_id, created_at) | Audit trail |

---

## Data Retention

| Data Type | SaaS Retention | Enterprise |
|-----------|---------------|------------|
| Findings (resolved) | 1 year | Configurable |
| Flag events (audit) | 1 year | 7 years |
| Knowledge units | Indefinite (versioned) | Indefinite |
| Diff artifacts (S3) | 24 hours | 24 hours |
| Posture snapshots | 2 years | Indefinite |
| Agent run logs | 90 days | 1 year |
