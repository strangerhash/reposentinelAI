# MCP Servers & AI Agent Governance

Model Context Protocol integration for RepoSentinel AI — enabling Cursor, VS Code, and custom AI agents to interact with security posture and knowledge base safely.

---

## Overview

RepoSentinel AI operates in two MCP-related roles:

1. **MCP Server (outbound)** — RepoSentinel exposes tools that external AI agents (Cursor, VS Code Copilot, custom agents) can call
2. **MCP Governance (inbound)** — RepoSentinel monitors and governs MCP servers and AI agents operating on connected repositories

---

## RepoSentinel MCP Server

### Deployment Options

| Mode | Transport | Use Case |
|------|-----------|----------|
| Local stdio | `stdio` | Cursor IDE, local dev |
| Remote SSE | `sse` over HTTPS | Team-shared MCP endpoint |
| Self-hosted | stdio or SSE in customer VPC | Regulated environments |

### Cursor / VS Code Configuration

```json
{
  "mcpServers": {
    "reposentinel": {
      "command": "npx",
      "args": ["-y", "@reposentinel/mcp-server"],
      "env": {
        "REPOSENTINEL_API_KEY": "rsl_live_...",
        "REPOSENTINEL_API_URL": "https://api.reposentinel.ai/v1"
      }
    }
  }
}
```

### Remote SSE Configuration

```json
{
  "mcpServers": {
    "reposentinel": {
      "url": "https://mcp.reposentinel.ai/sse",
      "headers": {
        "Authorization": "Bearer eyJ..."
      }
    }
  }
}
```

---

## Exposed MCP Tools

### Security & Flags

#### `list_flags`
List open security flags for connected repositories.

```json
{
  "name": "list_flags",
  "description": "List security flags. Filter by severity, status, or repository.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "severity": { "type": "array", "items": { "enum": ["critical","high","medium","low"] } },
      "status": { "type": "array", "items": { "enum": ["open","assigned","in_remediation"] } },
      "repository": { "type": "string", "description": "org/repo name" },
      "limit": { "type": "integer", "default": 20 }
    }
  }
}
```

#### `get_flag_detail`
Get full flag with findings, explanation, and remediation steps.

#### `get_posture_score`
Get current posture score for org, team, or repository.

```json
{
  "name": "get_posture_score",
  "inputSchema": {
    "properties": {
      "scope": { "enum": ["org", "team", "repo"] },
      "scope_id": { "type": "string" }
    }
  }
}
```

### Knowledge Base

#### `query_knowledge`
Ask the knowledge base a question with citations.

```json
{
  "name": "query_knowledge",
  "inputSchema": {
    "properties": {
      "question": { "type": "string" },
      "mode": { "enum": ["default", "onboarding"], "default": "default" },
      "repository": { "type": "string" }
    },
    "required": ["question"]
  }
}
```

#### `search_architecture`
Query the architecture graph — dependencies, service relationships.

```json
{
  "name": "search_architecture",
  "inputSchema": {
    "properties": {
      "service": { "type": "string" },
      "query_type": { "enum": ["dependencies", "dependents", "drift"] }
    }
  }
}
```

### Remediation (Permission-Gated)

#### `create_fix_pr`
Create a draft remediation PR for an eligible flag. Requires `write:remediation` scope.

```json
{
  "name": "create_fix_pr",
  "inputSchema": {
    "properties": {
      "flag_id": { "type": "string" }
    },
    "required": ["flag_id"]
  }
}
```

**Safety:** Always creates draft PR. Never auto-merges.

### Compliance (Read-Only by Default)

#### `get_compliance_status`
Get control framework status (SOC 2, ISO 27001, PCI-DSS).

#### `list_control_gaps`
List controls at risk with linked flags.

---

## MCP Resources

Resources provide read-only context without tool calls.

| URI Pattern | Content |
|-------------|---------|
| `reposentinel://posture/org` | Current org posture score + trend |
| `reposentinel://posture/repo/{repo_id}` | Repo-level posture |
| `reposentinel://flags/critical` | Critical open flags summary |
| `reposentinel://architecture/{repo_id}` | Service dependency graph (JSON) |
| `reposentinel://compliance/{framework}` | Framework control status |

---

## MCP Prompts (Templates)

Pre-built prompts for common workflows:

| Prompt ID | Description |
|-----------|-------------|
| `security-review` | Review current repo flags before merge |
| `onboarding-tour` | New-hire codebase orientation |
| `incident-context` | Gather KB context for an incident |
| `dependency-audit` | SCA findings summary with fix recommendations |

---

## API Key Scopes for MCP

| Scope | Tools Allowed |
|-------|--------------|
| `read:flags` | list_flags, get_flag_detail |
| `read:posture` | get_posture_score |
| `read:knowledge` | query_knowledge, search_architecture |
| `read:compliance` | get_compliance_status, list_control_gaps |
| `write:remediation` | create_fix_pr |
| `admin:mcp` | Register/manage MCP servers |

Keys are scoped per-organization with optional repo-level restrictions.

---

## AI Agent & MCP Governance Module

### Problem (2026 Context)

Companies wire AI coding agents (Cursor, Copilot, Devin, custom) and MCP servers into pipelines. Almost nobody has visibility into:
- What files AI agents modified
- What MCP tools were invoked and with what permissions
- Whether agent-authored changes introduced security regressions

### RepoSentinel Governance Capabilities

#### 1. AI Agent Activity Tracking

Monitor commits and PRs tagged or detected as AI-agent-authored:

```json
{
  "id": "activity_xyz",
  "agent_name": "cursor",
  "repository": "acme/payment-service",
  "change_id": "change_abc",
  "files_touched": ["src/auth.ts", "src/config.ts"],
  "mcp_tools_invoked": ["reposentinel.query_knowledge", "filesystem.write"],
  "risk_level": "medium",
  "flags_introduced": 0,
  "detected_at": "2026-07-07T10:00:00Z"
}
```

**Detection methods:**
- Commit message patterns (`Co-authored-by: Cursor`, `Generated by Copilot`)
- GitHub Copilot attribution API
- Cursor hook integration (opt-in)
- MCP server audit logs (RepoSentinel MCP server logs all tool calls)

#### 2. MCP Server Registry

Organizations register MCP servers used by their teams:

```yaml
mcp_server:
  name: cursor-workspace
  type: external
  endpoint: local | https://custom-mcp.company.com
  tools_exposed:
    - filesystem.read
    - filesystem.write
    - reposentinel.query_knowledge
  permissions_reviewed: true
  last_audit: 2026-07-01
  risk_classification: medium
```

#### 3. MCP Permission Analysis

RepoSentinel analyzes registered MCP servers for risky permission combinations:

| Risk Pattern | Severity | Example |
|-------------|----------|---------|
| Write + no scope limit | High | `filesystem.write` on entire repo |
| Secret access + network | Critical | MCP tool can read `.env` and call external APIs |
| Unreviewed external MCP | Medium | Custom MCP server not in org registry |
| Agent bypasses scanners | High | Direct commit without PR / scan gate |

#### 4. AI Bill of Materials (AI-BOM)

Per-repository manifest of AI agents and MCP servers in use:

```json
{
  "repository": "acme/payment-service",
  "ai_bom_version": "1.0",
  "agents": [
    { "name": "cursor", "version": "1.2", "users_count": 12, "last_active": "2026-07-07" },
    { "name": "github-copilot", "version": "enterprise", "users_count": 8 }
  ],
  "mcp_servers": [
    { "name": "reposentinel", "tools": ["query_knowledge", "list_flags"], "risk": "low" },
    { "name": "custom-db-mcp", "tools": ["sql.execute"], "risk": "high" }
  ],
  "generated_at": "2026-07-07T02:00:00Z"
}
```

#### 5. Policy Enforcement

```yaml
policies:
  - name: require-scan-before-merge
    condition: ai_agent_authored == true
    action: block_merge_until_scan_passes

  - name: restrict-high-risk-mcp
    condition: mcp_server.risk == "high" AND environment == "production"
    action: alert_security_lead

  - name: log-all-mcp-invocations
    condition: always
    action: audit_log
```

---

## MCP Server Implementation

### Package Structure

```
packages/mcp-server/
├── src/
│   ├── index.ts          # stdio/SSE entry point
│   ├── server.ts         # MCP server setup
│   ├── tools/
│   │   ├── flags.ts
│   │   ├── posture.ts
│   │   ├── knowledge.ts
│   │   ├── architecture.ts
│   │   ├── remediation.ts
│   │   └── compliance.ts
│   ├── resources/
│   │   └── index.ts
│   ├── prompts/
│   │   └── index.ts
│   └── client.ts         # RepoSentinel API client
├── package.json
└── README.md
```

### NPM Package

```
@reposentinel/mcp-server
```

Published to npm for `npx @reposentinel/mcp-server` one-line Cursor setup.

---

## Security Considerations for MCP

| Risk | Mitigation |
|------|-----------|
| API key leakage in IDE config | Short-lived tokens, key rotation, scope limits |
| Over-privileged MCP tools | Default read-only; write scopes require admin approval |
| Prompt injection via KB | Retrieval boundaries; no raw repo in agent context |
| MCP server impersonation | Org registry + certificate pinning for remote SSE |
| Audit gap | Every MCP tool call logged to `ai_agent_activity` |

---

## Integration with Cursor Hooks

Optional Cursor hook (`.cursor/hooks.json`) to report agent activity:

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [{
      "command": "npx @reposentinel/cursor-hook report-edit",
      "env": { "REPOSENTINEL_API_KEY": "${REPOSENTINEL_API_KEY}" }
    }]
  }
}
```

This feeds the AI Agent Governance module with real-time file touch data.
