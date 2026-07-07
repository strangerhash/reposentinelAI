# Design System

Silicon Valley clean aesthetic for RepoSentinel AI — tokens, components, and screen specifications.

---

## Design Philosophy

RepoSentinel should feel like **Linear × Vercel × Datadog** — not a legacy security console.

| Principle | Implementation |
|-----------|---------------|
| Clarity over density | One primary action per screen; progressive disclosure |
| Data with narrative | Every chart answers a specific question |
| Trust through traceability | Scores and AI outputs link to source |
| Calm by default | Neutral palette; severity color for risk only |
| Speed as feature | Sub-200ms navigation; skeleton loaders |

---

## Design Tokens

### Color Palette

```css
:root {
  /* Backgrounds */
  --bg-primary: #FAFAFA;
  --bg-secondary: #FFFFFF;
  --bg-tertiary: #F4F4F5;
  --bg-elevated: #FFFFFF;

  /* Text */
  --text-primary: #18181B;
  --text-secondary: #71717A;
  --text-tertiary: #A1A1AA;
  --text-inverse: #FAFAFA;

  /* Accent */
  --accent-primary: #3B82F6;
  --accent-hover: #2563EB;
  --accent-subtle: #EFF6FF;

  /* Severity (semantic only) */
  --severity-critical: #EF4444;
  --severity-high: #F97316;
  --severity-medium: #F59E0B;
  --severity-low: #3B82F6;
  --severity-info: #71717A;

  /* Status */
  --status-success: #10B981;
  --status-warning: #F59E0B;
  --status-error: #EF4444;

  /* Borders */
  --border-default: #E4E4E7;
  --border-subtle: #F4F4F5;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.10);
}

[data-theme="dark"] {
  --bg-primary: #0F1117;
  --bg-secondary: #181B25;
  --bg-tertiary: #1F2433;
  --bg-elevated: #1F2433;
  --text-primary: #F4F4F5;
  --text-secondary: #A1A1AA;
  --text-tertiary: #71717A;
  --border-default: #27272A;
  --accent-subtle: #1E3A5F;
}
```

### Typography

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Scale */
--text-xs: 0.75rem;    /* 12px — labels, badges */
--text-sm: 0.875rem;   /* 14px — body, table cells */
--text-base: 1rem;     /* 16px — default */
--text-lg: 1.125rem;   /* 18px — section headers */
--text-xl: 1.25rem;    /* 20px — card titles */
--text-2xl: 1.5rem;    /* 24px — page titles */
--text-3xl: 1.875rem;  /* 30px — hero metrics */
--text-4xl: 2.25rem;   /* 36px — posture score */
```

### Spacing & Layout

```css
--space-1: 0.25rem;
--space-2: 0.5rem;
--space-3: 0.75rem;
--space-4: 1rem;
--space-6: 1.5rem;
--space-8: 2rem;
--space-12: 3rem;

--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-full: 9999px;

--max-width-content: 1280px;
--sidebar-width: 240px;
--sidebar-collapsed: 64px;
```

### Motion

```css
--transition-fast: 150ms ease-out;
--transition-base: 200ms ease-out;
--transition-slow: 300ms ease-out;
```

---

## Component Library

**Base:** shadcn/ui + Tailwind CSS on Next.js 15

### Core Components

| Component | Usage |
|-----------|-------|
| `PostureScoreRing` | Hero metric — animated SVG ring 0–100 |
| `SeverityBadge` | critical/high/medium/low pills |
| `FlagCard` | Risk register row with SLA timer |
| `CitationCard` | Inline file/PR/commit reference |
| `TrendChart` | 90-day posture line (Tremor) |
| `ServiceGraph` | Architecture map (React Flow) |
| `ChatMessage` | Knowledge copilot with citations |
| `EmptyState` | Illustrated + CTA for zero-data screens |
| `TenantSwitcher` | MSP multi-client dropdown |
| `TokenBudgetBar` | Cost dashboard progress bar |

### Button Hierarchy

```
Primary:   bg-accent-primary text-white — one per screen section
Secondary: border border-default — supporting actions
Ghost:     text-secondary — tertiary actions
Danger:    bg-severity-critical — destructive only
```

---

## Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│ Top Bar: Logo | Tenant Switcher | Search | Notifications | Avatar │
├────────┬─────────────────────────────────────────────────────┤
│        │                                                      │
│ Side   │  Page Header: Title + Primary Action                │
│ bar    │  ─────────────────────────────────────────────────  │
│        │                                                      │
│ Posture│  Content Area (max-width: 1280px, centered)         │
│ Flags  │                                                      │
│ Arch   │                                                      │
│ Know   │                                                      │
│ Compl  │                                                      │
│ Settings│                                                     │
│        │                                                      │
└────────┴─────────────────────────────────────────────────────┘
```

### Sidebar Navigation

```
📊 Posture          — Executive dashboard
🚩 Flags            — Risk register (badge: open count)
🏗 Architecture     — Service graph
💬 Knowledge        — Copilot search
📋 Compliance       — Control mapping (Business+)
🔍 Engagements      — M&A mode (Business+)
🤖 AI Governance    — Agent/MCP tracking (V2)
⚙️ Settings         — Org, integrations, billing
📈 Cost & Ops        — Token spend (Admin only)
```

---

## Key Screen Specifications

### 1. Executive Posture Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  Posture Score                                           │
│  ┌──────────┐  ┌─────────────────────────────────────┐  │
│  │    87    │  │ 90-day trend: +12 pts              │  │
│  │  /100    │  │ [═══════════════░░░] chart          │  │
│  │  ▲ +3    │  │ Better than 72% of fintech peers    │  │
│  └──────────┘  └─────────────────────────────────────┘  │
│                                                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐         │
│  │ Critical: 1│ │ High: 5    │ │ Auto-fixed │         │
│  │ open       │ │ open       │ │ 42 / 30d   │         │
│  └────────────┘ └────────────┘ └────────────┘         │
│                                                          │
│  Top Risk Drivers                                        │
│  1. CVE-2024-1234 — lodash (12 repos)     [Create fix PR]│
│  2. Exposed secret in config/dev.yaml      [View flag]   │
│  3. Architecture drift — auth → billing    [View graph]  │
└─────────────────────────────────────────────────────────┘
```

### 2. Risk Register

- Data table with sortable columns: Severity, Title, Repo, Assignee, SLA, Status
- Bulk actions: Assign, Dismiss, Export
- Filters: severity, status, repo, team, compliance control
- Row click → Flag Detail slide-over panel

### 3. Flag Detail (Split View)

```
┌──────────────────────┬──────────────────────────────────┐
│ FINDINGS (left)      │ EXPLANATION (right)               │
│                      │                                   │
│ scanner: sca         │ lodash 4.17.20 is vulnerable...  │
│ rule: cve-2024-1234  │                                   │
│ file: package.json:42│ Remediation Steps:                  │
│ [view in repo]       │ 1. Upgrade lodash to >=4.17.21    │
│                      │ 2. Run npm audit fix              │
│                      │                                   │
│                      │ [Create fix PR]  [Assign]  [Dismiss]│
├──────────────────────┴──────────────────────────────────┤
│ AUDIT TRAIL: assigned by Security Lead · 2h ago           │
└─────────────────────────────────────────────────────────┘
```

### 4. Knowledge Copilot

- Chat interface with message bubbles
- Inline `CitationCard` components (file icon + path + line range)
- Mode toggle: Default | Onboarding (simplified)
- Suggested questions chips for empty state

### 5. Landing Page

- Hero: headline + animated dashboard mockup
- 3-column problem section
- Product pillar cards with icons
- How it works (4 steps)
- Differentiator comparison table
- Persona-based solution tabs
- Pricing preview cards
- Final CTA with gradient background

---

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|-----------|-------|--------|
| Mobile | < 768px | Sidebar hidden (hamburger), single column |
| Tablet | 768–1024px | Collapsed sidebar (icons only) |
| Desktop | > 1024px | Full sidebar + content |
| Wide | > 1440px | Content centered, max 1280px |

---

## Accessibility

- WCAG 2.1 AA compliance target
- Color contrast: 4.5:1 minimum for text
- Severity never conveyed by color alone (icons + labels)
- Keyboard navigation for all interactive elements
- Screen reader labels on posture score ring and charts
- Focus indicators on all focusable elements

---

## White-Label Theming

MSP/consultancy tenants can override:

```json
{
  "logo_url": "https://consultancy.com/logo.svg",
  "accent_color": "#6366F1",
  "custom_domain": "security.clientportal.com",
  "hide_reposentinel_branding": true,
  "report_footer": "Prepared by Acme Security Consulting"
}
```

CSS variables injected at runtime from tenant `white_label` config.
