import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Engagement, EngagementStatus, Finding, Flag, FlagStatus, Organization, Repository
from app.scanners.engine import ScanFinding, scan_files
from app.schemas import EngagementReportOut, PostureOut


SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 10,
    "medium": 5,
    "low": 2,
    "info": 0,
}


async def get_or_create_demo_org(db: AsyncSession) -> Organization:
    result = await db.execute(select(Organization).where(Organization.slug == "demo"))
    org = result.scalar_one_or_none()
    if org:
        return org
    org = Organization(name="Demo Consultancy", slug="demo", plan_tier="business")
    db.add(org)
    await db.flush()
    return org


async def list_flags(db: AsyncSession, tenant_id: uuid.UUID, engagement_id: uuid.UUID | None = None) -> list[Flag]:
    query = select(Flag).where(Flag.tenant_id == tenant_id).order_by(Flag.created_at.desc())
    if engagement_id:
        query = query.where(Flag.engagement_id == engagement_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def compute_posture(db: AsyncSession, tenant_id: uuid.UUID) -> PostureOut:
    result = await db.execute(
        select(Flag.severity, func.count())
        .where(Flag.tenant_id == tenant_id, Flag.status.notin_(["resolved", "verified", "dismissed"]))
        .group_by(Flag.severity)
    )
    counts = dict(result.all())
    penalty = sum(SEVERITY_WEIGHTS.get(sev, 0) * count for sev, count in counts.items())
    score = max(0, min(100, 100 - penalty))

    repo_count = await db.execute(
        select(func.count()).select_from(Repository).where(Repository.tenant_id == tenant_id, Repository.is_active.is_(True))
    )
    return PostureOut(
        score=score,
        trend_90d=0,
        critical_open=counts.get("critical", 0),
        high_open=counts.get("high", 0),
        total_open=sum(counts.values()),
        repos_scanned=repo_count.scalar() or 0,
    )


async def persist_findings_and_flags(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    repository: Repository,
    findings: list[ScanFinding],
    engagement_id: uuid.UUID | None = None,
) -> list[Flag]:
    created_flags: list[Flag] = []
    for item in findings:
        existing = await db.execute(
            select(Finding).where(
                Finding.tenant_id == tenant_id,
                Finding.fingerprint == item.fingerprint,
                Finding.status == "open",
            )
        )
        if existing.scalar_one_or_none():
            continue

        finding = Finding(
            tenant_id=tenant_id,
            repository_id=repository.id,
            scanner=item.scanner,
            rule_id=item.rule_id,
            severity=item.severity,
            title=item.title,
            description=item.description,
            file_path=item.file_path,
            line_start=item.line_start,
            fingerprint=item.fingerprint,
            extra=item.metadata,
        )
        db.add(finding)
        await db.flush()

        if item.severity in ("critical", "high", "medium"):
            flag = Flag(
                tenant_id=tenant_id,
                repository_id=repository.id,
                engagement_id=engagement_id,
                title=item.title,
                severity=item.severity,
                status=FlagStatus.NEW.value,
                explanation=_explain_finding(item),
                remediation_steps=_remediation_steps(item),
            )
            db.add(flag)
            created_flags.append(flag)

    repository.last_scan_at = datetime.now(timezone.utc)
    return created_flags


def _explain_finding(item: ScanFinding) -> str:
    if item.scanner == "secrets":
        return (
            f"A potential secret was detected in `{item.file_path}` at line {item.line_start}. "
            "Rotate the credential immediately and remove it from git history."
        )
    return (
        f"Dependency risk identified in `{item.file_path}`: {item.title}. "
        "Review upgrade path and test before merging."
    )


def _remediation_steps(item: ScanFinding) -> list[dict]:
    if item.scanner == "sca" and item.metadata.get("package"):
        return [
            {
                "step": 1,
                "action": f"Upgrade {item.metadata['package']} to latest patched version",
                "automated": True,
            },
            {"step": 2, "action": "Run test suite and open PR", "automated": False},
        ]
    return [
        {"step": 1, "action": "Revoke and rotate exposed credential", "automated": False},
        {"step": 2, "action": "Remove secret from repository history", "automated": False},
    ]


async def run_engagement_scan(db: AsyncSession, engagement: Engagement, sample_files: dict[str, str] | None = None) -> Engagement:
    engagement.status = EngagementStatus.SCANNING.value
    await db.flush()

    if not engagement.repo_ids:
        repos_result = await db.execute(
            select(Repository).where(Repository.tenant_id == engagement.tenant_id, Repository.is_active.is_(True))
        )
        engagement.repo_ids = [r.id for r in repos_result.scalars().all()]

    for repo_id in engagement.repo_ids:
        repo = await db.get(Repository, repo_id)
        if not repo:
            continue
        files = sample_files or _demo_files_for_repo(repo.full_name)
        findings = scan_files(files)
        await persist_findings_and_flags(db, engagement.tenant_id, repo, findings, engagement.id)

    report = await build_engagement_report(db, engagement)
    engagement.report_summary = report.model_dump(mode="json")
    engagement.status = EngagementStatus.COMPLETED.value
    engagement.completed_at = datetime.now(timezone.utc)
    return engagement


def _demo_files_for_repo(full_name: str) -> dict[str, str]:
    return {
        "package.json": """
        {
          "name": "%s",
          "dependencies": {
            "lodash": "4.17.20",
            "axios": "1.6.0"
          }
        }
        """ % full_name.split("/")[-1],
        "src/config.ts": """
        export const config = {
          apiKey: "sk-demo1234567890abcdefghij",
          retries: 3,
        };
        """,
        ".env.example": "DATABASE_URL=postgres://user:password='supersecret123'@localhost/db",
    }


async def build_engagement_report(db: AsyncSession, engagement: Engagement) -> EngagementReportOut:
    flags = await list_flags(db, engagement.tenant_id, engagement.id)
    posture = await compute_posture(db, engagement.tenant_id)

    by_severity: dict[str, int] = {}
    for flag in flags:
        by_severity[flag.severity] = by_severity.get(flag.severity, 0) + 1

    repos_out = []
    for repo_id in engagement.repo_ids:
        repo = await db.get(Repository, repo_id)
        if repo:
            repo_flags = [f for f in flags if f.repository_id == repo.id]
            repos_out.append(
                {
                    "id": str(repo.id),
                    "full_name": repo.full_name,
                    "platform": repo.platform,
                    "open_flags": len(repo_flags),
                    "critical": sum(1 for f in repo_flags if f.severity == "critical"),
                }
            )

    top_risks = [
        {
            "flag_id": str(f.id),
            "title": f.title,
            "severity": f.severity,
            "repository_id": str(f.repository_id),
        }
        for f in sorted(flags, key=lambda x: ["critical", "high", "medium", "low"].index(x.severity))[:10]
    ]

    return EngagementReportOut(
        engagement_id=engagement.id,
        engagement_name=engagement.name,
        target_org=engagement.target_org,
        generated_at=datetime.now(timezone.utc),
        posture_score=posture.score,
        summary={
            "total_flags": len(flags),
            "repos_assessed": len(repos_out),
            "recommendation": _engagement_recommendation(posture.score, by_severity),
        },
        flags_by_severity=by_severity,
        top_risks=top_risks,
        repositories=repos_out,
    )


def _engagement_recommendation(score: int, by_severity: dict) -> str:
    if score < 50 or by_severity.get("critical", 0) > 0:
        return "HIGH RISK — Critical security debt identified. Recommend remediation before acquisition close."
    if score < 75:
        return "MODERATE RISK — Address high-severity findings within 90-day integration window."
    return "LOW RISK — Security posture acceptable with standard integration hygiene."
