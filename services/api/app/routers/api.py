import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Engagement, Flag, Repository
from app.schemas import (
    EngagementCreate,
    EngagementOut,
    EngagementReportOut,
    FlagOut,
    FlagUpdate,
    OrganizationCreate,
    OrganizationOut,
    PostureOut,
    RepositoryCreate,
    RepositoryOut,
)
from app.services.core import (
    build_engagement_report,
    compute_posture,
    get_or_create_demo_org,
    list_flags,
    run_engagement_scan,
)

router = APIRouter(prefix="/v1", tags=["api"])


@router.get("/health")
async def health():
    return {"status": "ok", "product": "EstateGuard"}


@router.post("/orgs", response_model=OrganizationOut)
async def create_org(payload: OrganizationCreate, db: AsyncSession = Depends(get_db)):
    org = await get_or_create_demo_org(db) if payload.slug == "demo" else None
    if not org:
        from app.models import Organization

        org = Organization(name=payload.name, slug=payload.slug)
        db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.get("/orgs/{slug}", response_model=OrganizationOut)
async def get_org(slug: str, db: AsyncSession = Depends(get_db)):
    from app.models import Organization

    result = await db.execute(select(Organization).where(Organization.slug == slug))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/repos", response_model=list[RepositoryOut])
async def list_repos(tenant: str = "demo", db: AsyncSession = Depends(get_db)):
    org = await get_or_create_demo_org(db)
    result = await db.execute(select(Repository).where(Repository.tenant_id == org.id))
    repos = result.scalars().all()
    out = []
    for repo in repos:
        flags = await db.execute(
            select(Flag).where(Flag.repository_id == repo.id, Flag.status.notin_(["resolved", "verified", "dismissed"]))
        )
        out.append(
            RepositoryOut(
                id=repo.id,
                platform=repo.platform,
                full_name=repo.full_name,
                url=repo.url,
                criticality_tier=repo.criticality_tier,
                is_active=repo.is_active,
                last_scan_at=repo.last_scan_at,
                open_flags=len(flags.scalars().all()),
            )
        )
    return out


@router.post("/repos", response_model=RepositoryOut)
async def create_repo(payload: RepositoryCreate, tenant: str = "demo", db: AsyncSession = Depends(get_db)):
    org = await get_or_create_demo_org(db)
    repo = Repository(
        tenant_id=org.id,
        platform=payload.platform,
        external_id=payload.external_id,
        name=payload.name,
        full_name=payload.full_name,
        url=payload.url,
        default_branch=payload.default_branch,
        criticality_tier=payload.criticality_tier,
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)
    return RepositoryOut(
        id=repo.id,
        platform=repo.platform,
        full_name=repo.full_name,
        url=repo.url,
        criticality_tier=repo.criticality_tier,
        is_active=repo.is_active,
        last_scan_at=repo.last_scan_at,
        open_flags=0,
    )


@router.get("/flags", response_model=list[FlagOut])
async def get_flags(tenant: str = "demo", engagement_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)):
    org = await get_or_create_demo_org(db)
    flags = await list_flags(db, org.id, engagement_id)
    out = []
    for flag in flags:
        repo = await db.get(Repository, flag.repository_id)
        out.append(
            FlagOut(
                id=flag.id,
                title=flag.title,
                severity=flag.severity,
                status=flag.status,
                repository_id=flag.repository_id,
                engagement_id=flag.engagement_id,
                explanation=flag.explanation,
                remediation_steps=flag.remediation_steps,
                created_at=flag.created_at,
                repository_full_name=repo.full_name if repo else None,
            )
        )
    return out


@router.patch("/flags/{flag_id}", response_model=FlagOut)
async def update_flag(flag_id: uuid.UUID, payload: FlagUpdate, db: AsyncSession = Depends(get_db)):
    flag = await db.get(Flag, flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    if payload.status:
        flag.status = payload.status
    await db.commit()
    await db.refresh(flag)
    repo = await db.get(Repository, flag.repository_id)
    return FlagOut(
        id=flag.id,
        title=flag.title,
        severity=flag.severity,
        status=flag.status,
        repository_id=flag.repository_id,
        engagement_id=flag.engagement_id,
        explanation=flag.explanation,
        remediation_steps=flag.remediation_steps,
        created_at=flag.created_at,
        repository_full_name=repo.full_name if repo else None,
    )


@router.get("/posture", response_model=PostureOut)
async def get_posture(tenant: str = "demo", db: AsyncSession = Depends(get_db)):
    org = await get_or_create_demo_org(db)
    return await compute_posture(db, org.id)


@router.get("/engagements", response_model=list[EngagementOut])
async def list_engagements(tenant: str = "demo", db: AsyncSession = Depends(get_db)):
    org = await get_or_create_demo_org(db)
    result = await db.execute(
        select(Engagement).where(Engagement.tenant_id == org.id).order_by(Engagement.created_at.desc())
    )
    return result.scalars().all()


@router.post("/engagements", response_model=EngagementOut)
async def create_engagement(payload: EngagementCreate, tenant: str = "demo", db: AsyncSession = Depends(get_db)):
    org = await get_or_create_demo_org(db)
    engagement = Engagement(
        tenant_id=org.id,
        name=payload.name,
        target_org=payload.target_org,
        repo_ids=payload.repo_ids,
        expires_at=payload.expires_at,
        white_label=payload.white_label,
        status="draft",
    )
    db.add(engagement)
    await db.commit()
    await db.refresh(engagement)
    return engagement


@router.post("/engagements/{engagement_id}/scan", response_model=EngagementOut)
async def scan_engagement(engagement_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    engagement = await db.get(Engagement, engagement_id)
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    engagement = await run_engagement_scan(db, engagement)
    await db.commit()
    await db.refresh(engagement)
    return engagement


@router.get("/engagements/{engagement_id}/report", response_model=EngagementReportOut)
async def engagement_report(engagement_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    engagement = await db.get(Engagement, engagement_id)
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return await build_engagement_report(db, engagement)
