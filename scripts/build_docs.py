#!/usr/bin/env python3
"""Combine all RepoSentinel AI docs into a single professional HTML file."""

import re
from datetime import datetime
from pathlib import Path

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension

DOCS_DIR = Path(__file__).parent.parent / "docs"
OUTPUT = Path(__file__).parent.parent / "RepoSentinel_AI_Complete_Documentation.html"

DOC_FILES = [
    ("01-product-overview.md", "Product Overview", "product"),
    ("02-landing-page.md", "Landing Page", "landing"),
    ("03-roles-and-permissions.md", "Roles & Permissions", "roles"),
    ("04-system-architecture.md", "System Architecture", "architecture"),
    ("05-system-design.md", "System Design", "design"),
    ("06-data-model.md", "Data Model", "data"),
    ("07-api-design.md", "API Design", "api"),
    ("08-agent-framework.md", "Agent Framework", "agents"),
    ("09-mcp-servers.md", "MCP Servers", "mcp"),
    ("10-security-architecture.md", "Security Architecture", "security"),
    ("11-design-system.md", "Design System", "ui"),
    ("12-deployment-guide.md", "Deployment Guide", "deploy"),
    ("13-roadmap-and-pricing.md", "Roadmap & Pricing", "roadmap"),
    ("14-integrations.md", "Integrations", "integrations"),
    ("15-competitive-analysis.md", "Competitive Analysis", "competitive"),
    ("16-rebrand-estateguard.md", "Rebrand: EstateGuard", "rebrand"),
]

md = markdown.Markdown(
    extensions=[
        TableExtension(),
        FencedCodeExtension(),
        TocExtension(permalink=True, toc_depth="2-3"),
        "nl2br",
    ]
)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def convert_md(content: str, section_id: str) -> str:
  md.reset()
  html = md.convert(content)
  html = re.sub(r'<h(\d) id="([^"]+)"', rf'<h\1 id="{section_id}-\2"', html)
  html = re.sub(r'<a class="headerlink" href="#([^"]+)"', rf'<a class="headerlink" href="#{section_id}-\1"', html)
  return html


def build_nav() -> str:
    items = []
    for filename, title, sid in DOC_FILES:
        items.append(f'<a href="#{sid}" class="nav-link" data-section="{sid}">{title}</a>')
    return "\n".join(items)


def build_sections() -> str:
    sections = []
    for filename, title, sid in DOC_FILES:
        path = DOCS_DIR / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        body = convert_md(content, sid)
        sections.append(f"""
<section id="{sid}" class="doc-section">
  <div class="section-header">
  <span class="section-label">Documentation</span>
  <h1 class="section-title">{title}</h1>
  </div>
  <div class="section-body prose">
  {body}
  </div>
</section>
""")
    return "\n".join(sections)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RepoSentinel AI — Complete Product Documentation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #FAFAFA;
  --bg-elevated: #FFFFFF;
  --bg-sidebar: #FFFFFF;
  --text: #18181B;
  --text-secondary: #71717A;
  --text-tertiary: #A1A1AA;
  --accent: #3B82F6;
  --accent-hover: #2563EB;
  --accent-subtle: #EFF6FF;
  --border: #E4E4E7;
  --border-subtle: #F4F4F5;
  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --sidebar-w: 280px;
  --topbar-h: 56px;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.08);
  --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono: 'JetBrains Mono', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; scroll-padding-top: calc(var(--topbar-h) + 24px); }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

/* Top Bar */
.topbar {
  position: fixed; top: 0; left: 0; right: 0; height: var(--topbar-h);
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; z-index: 100;
}
.topbar-brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 16px; }
.topbar-brand .logo {
  width: 28px; height: 28px; background: var(--accent); border-radius: 6px;
  display: flex; align-items: center; justify-content: center; color: white; font-size: 14px;
}
.topbar-meta { font-size: 13px; color: var(--text-secondary); }
.topbar-actions { display: flex; gap: 8px; }
.btn {
  padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
  border: 1px solid var(--border); background: var(--bg-elevated); cursor: pointer;
  text-decoration: none; color: var(--text); transition: all 150ms ease;
}
.btn:hover { border-color: var(--accent); color: var(--accent); }
.btn-primary { background: var(--accent); color: white; border-color: var(--accent); }
.btn-primary:hover { background: var(--accent-hover); color: white; }

/* Sidebar */
.sidebar {
  position: fixed; top: var(--topbar-h); left: 0; bottom: 0; width: var(--sidebar-w);
  background: var(--bg-sidebar); border-right: 1px solid var(--border);
  overflow-y: auto; padding: 20px 0; z-index: 50;
}
.sidebar-label {
  padding: 0 20px; font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text-tertiary); margin-bottom: 8px;
}
.nav-link {
  display: block; padding: 7px 20px; font-size: 13.5px; color: var(--text-secondary);
  text-decoration: none; border-left: 2px solid transparent; transition: all 150ms;
}
.nav-link:hover { color: var(--text); background: var(--border-subtle); }
.nav-link.active { color: var(--accent); border-left-color: var(--accent); background: var(--accent-subtle); font-weight: 500; }

/* Main */
.main { margin-left: var(--sidebar-w); margin-top: var(--topbar-h); }

/* Hero */
.hero {
  background: linear-gradient(135deg, #0F1117 0%, #1a1f2e 50%, #0F1117 100%);
  color: white; padding: 80px 48px 64px; position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; top: -50%; right: -20%; width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-content { max-width: 720px; position: relative; }
.hero-badge {
  display: inline-block; padding: 4px 12px; background: rgba(59,130,246,0.2);
  border: 1px solid rgba(59,130,246,0.3); border-radius: 20px;
  font-size: 12px; font-weight: 500; color: #93C5FD; margin-bottom: 20px;
}
.hero h1 { font-size: 42px; font-weight: 700; line-height: 1.15; margin-bottom: 16px; letter-spacing: -0.02em; }
.hero p { font-size: 18px; color: #A1A1AA; line-height: 1.6; margin-bottom: 32px; max-width: 560px; }
.hero-stats { display: flex; gap: 32px; margin-top: 40px; }
.hero-stat { }
.hero-stat-value { font-size: 28px; font-weight: 700; color: white; }
.hero-stat-label { font-size: 13px; color: #71717A; margin-top: 2px; }

/* Doc index cards */
.doc-index { padding: 48px; max-width: 1200px; }
.doc-index h2 { font-size: 24px; font-weight: 700; margin-bottom: 8px; }
.doc-index > p { color: var(--text-secondary); margin-bottom: 32px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.doc-card {
  background: var(--bg-elevated); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px; text-decoration: none; color: var(--text); transition: all 200ms ease;
  box-shadow: var(--shadow);
}
.doc-card:hover { border-color: var(--accent); box-shadow: var(--shadow-lg); transform: translateY(-1px); }
.doc-card-icon { font-size: 24px; margin-bottom: 12px; }
.doc-card h3 { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
.doc-card p { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }

/* Sections */
.doc-section { padding: 48px; max-width: 900px; border-bottom: 1px solid var(--border); }
.section-header { margin-bottom: 32px; }
.section-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); }
.section-title { font-size: 32px; font-weight: 700; margin-top: 4px; letter-spacing: -0.02em; }

/* Prose */
.prose h2 { font-size: 22px; font-weight: 700; margin: 40px 0 16px; padding-top: 16px; border-top: 1px solid var(--border-subtle); letter-spacing: -0.01em; }
.prose h2:first-child { border-top: none; margin-top: 0; padding-top: 0; }
.prose h3 { font-size: 17px; font-weight: 600; margin: 28px 0 12px; }
.prose h4 { font-size: 15px; font-weight: 600; margin: 20px 0 8px; }
.prose p { margin-bottom: 14px; color: var(--text); }
.prose ul, .prose ol { margin: 0 0 16px 24px; }
.prose li { margin-bottom: 6px; }
.prose strong { font-weight: 600; }
.prose a { color: var(--accent); text-decoration: none; }
.prose a:hover { text-decoration: underline; }
.prose blockquote {
  border-left: 3px solid var(--accent); padding: 12px 20px; margin: 16px 0;
  background: var(--accent-subtle); border-radius: 0 var(--radius) var(--radius) 0;
  color: var(--text-secondary); font-style: italic;
}
.prose code {
  font-family: var(--mono); font-size: 13px; background: var(--border-subtle);
  padding: 2px 6px; border-radius: 4px; color: #BE185D;
}
.prose pre {
  background: #0F1117; color: #E4E4E7; padding: 20px; border-radius: var(--radius);
  overflow-x: auto; margin: 16px 0; font-size: 13px; line-height: 1.5;
  box-shadow: var(--shadow);
}
.prose pre code { background: none; padding: 0; color: inherit; font-size: 13px; }
.prose table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13.5px; }
.prose th {
  background: var(--border-subtle); font-weight: 600; text-align: left;
  padding: 10px 14px; border: 1px solid var(--border);
}
.prose td { padding: 10px 14px; border: 1px solid var(--border); vertical-align: top; }
.prose tr:hover td { background: #FAFAFA; }
.prose hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }
.headerlink { color: var(--text-tertiary); text-decoration: none; margin-left: 6px; font-size: 14px; opacity: 0; transition: opacity 150ms; }
h2:hover .headerlink, h3:hover .headerlink { opacity: 1; }

/* Footer */
.footer {
  padding: 32px 48px; text-align: center; color: var(--text-tertiary); font-size: 13px;
  border-top: 1px solid var(--border);
}

/* Mobile */
.menu-toggle { display: none; background: none; border: none; font-size: 20px; cursor: pointer; }
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); transition: transform 200ms; }
  .sidebar.open { transform: translateX(0); }
  .main { margin-left: 0; }
  .menu-toggle { display: block; }
  .hero { padding: 48px 24px; }
  .hero h1 { font-size: 28px; }
  .doc-section, .doc-index { padding: 32px 24px; }
  .hero-stats { flex-direction: column; gap: 16px; }
}
@media print {
  .sidebar, .topbar { display: none; }
  .main { margin: 0; }
  .doc-section { page-break-inside: avoid; }
}
</style>
</head>
<body>

<header class="topbar">
  <div class="topbar-brand">
    <button class="menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>
    <div class="logo">R</div>
    <span>RepoSentinel AI</span>
  </div>
  <div class="topbar-meta">Complete Documentation · v0.2 · __DATE__</div>
  <div class="topbar-actions">
    <a href="#landing" class="btn">Landing Page</a>
    <a href="#competitive" class="btn">Competitive Analysis</a>
  </div>
</header>

<nav class="sidebar">
  <div class="sidebar-label">Contents</div>
  __NAV__
</nav>

<main class="main">

<section class="hero" id="top">
  <div class="hero-content">
    <div class="hero-badge">Product Documentation v0.2</div>
    <h1>RepoSentinel AI</h1>
    <p>The governed AI control plane above GitHub, GitLab, and Bitbucket. Security posture, living architecture, and institutional knowledge — without the token bill.</p>
    <div class="hero-stats">
      <div class="hero-stat"><div class="hero-stat-value">16</div><div class="hero-stat-label">Documents</div></div>
      <div class="hero-stat"><div class="hero-stat-value">6</div><div class="hero-stat-label">AI Agents</div></div>
      <div class="hero-stat"><div class="hero-stat-value">3</div><div class="hero-stat-label">VCS Platforms</div></div>
      <div class="hero-stat"><div class="hero-stat-value">10</div><div class="hero-stat-label">MCP Tools</div></div>
    </div>
  </div>
</section>

<section class="doc-index" id="index">
  <h2>Documentation Index</h2>
    <p>Complete product, architecture, and engineering documentation. Product codename: <strong>EstateGuard</strong>.</p>
  <div class="card-grid">
    <a href="#product" class="doc-card"><div class="doc-card-icon">📋</div><h3>Product Overview</h3><p>Vision, positioning, problem statement, and success metrics.</p></a>
    <a href="#landing" class="doc-card"><div class="doc-card-icon">🌐</div><h3>Landing Page</h3><p>Marketing site copy, structure, and design tokens.</p></a>
    <a href="#roles" class="doc-card"><div class="doc-card-icon">👥</div><h3>Roles & Permissions</h3><p>RBAC model, permission matrix, and audit requirements.</p></a>
    <a href="#architecture" class="doc-card"><div class="doc-card-icon">🏗</div><h3>System Architecture</h3><p>Four-layer architecture, enforcement boundary, deployment topologies.</p></a>
    <a href="#design" class="doc-card"><div class="doc-card-icon">⚙️</div><h3>System Design</h3><p>Service map, data flows, state machines, scaling strategy.</p></a>
    <a href="#data" class="doc-card"><div class="doc-card-icon">🗄</div><h3>Data Model</h3><p>PostgreSQL schema, RLS, indexing, and retention policies.</p></a>
    <a href="#api" class="doc-card"><div class="doc-card-icon">🔌</div><h3>API Design</h3><p>REST API specification for all platform endpoints.</p></a>
    <a href="#agents" class="doc-card"><div class="doc-card-icon">🤖</div><h3>Agent Framework</h3><p>Six governed agents, contracts, tier routing, budgets.</p></a>
    <a href="#mcp" class="doc-card"><div class="doc-card-icon">🔗</div><h3>MCP Servers</h3><p>MCP tools, resources, AI-agent governance, Cursor integration.</p></a>
    <a href="#security" class="doc-card"><div class="doc-card-icon">🔒</div><h3>Security Architecture</h3><p>Threat model, encryption, tenant isolation, compliance.</p></a>
    <a href="#ui" class="doc-card"><div class="doc-card-icon">🎨</div><h3>Design System</h3><p>Silicon Valley clean aesthetic, tokens, components, screens.</p></a>
    <a href="#deploy" class="doc-card"><div class="doc-card-icon">🚀</div><h3>Deployment Guide</h3><p>SaaS AWS, VPC self-hosted Helm, local dev, CI/CD.</p></a>
    <a href="#roadmap" class="doc-card"><div class="doc-card-icon">📅</div><h3>Roadmap & Pricing</h3><p>MVP → V1 → V2 phases, pricing tiers, GTM sequence.</p></a>
    <a href="#integrations" class="doc-card"><div class="doc-card-icon">🔧</div><h3>Integrations</h3><p>VCS, Slack, Jira, SSO, marketplaces, billing.</p></a>
    <a href="#competitive" class="doc-card"><div class="doc-card-icon">⚔️</div><h3>Competitive Analysis</h3><p>vs reposentinel.com, Cursor, Snyk. Positioning and wedge strategy.</p></a>
  </div>
</section>

__SECTIONS__

</main>

<footer class="footer">
  RepoSentinel AI · Xenqube / Tool Hub · Generated __DATE__ · Confidential — Internal Product Strategy
</footer>

<script>
const sections = document.querySelectorAll('.doc-section');
const navLinks = document.querySelectorAll('.nav-link');

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(l => l.classList.remove('active'));
      const link = document.querySelector(`.nav-link[data-section="${entry.target.id}"]`);
      if (link) link.classList.add('active');
    }
  });
}, { rootMargin: '-20% 0px -60% 0px' });

sections.forEach(s => observer.observe(s));

navLinks.forEach(link => {
  link.addEventListener('click', () => {
    document.querySelector('.sidebar').classList.remove('open');
  });
});
</script>
</body>
</html>"""


def main():
    date_str = datetime.now().strftime("%B %d, %Y")
    html = HTML_TEMPLATE.replace("__NAV__", build_nav())
    html = html.replace("__SECTIONS__", build_sections())
    html = html.replace("__DATE__", date_str)
    OUTPUT.write_text(html, encoding="utf-8")
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Generated: {OUTPUT}")
    print(f"Size: {size_kb:.0f} KB")
    print(f"Documents: {len(DOC_FILES)}")


if __name__ == "__main__":
    main()
