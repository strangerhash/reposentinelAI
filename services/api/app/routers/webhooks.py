import hashlib
import hmac
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Change, Organization, Repository
from app.services.core import get_or_create_demo_org, persist_findings_and_flags
from app.scanners.engine import scan_files

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/github/{tenant_slug}")
async def github_webhook(
    tenant_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_github_event: str = Header(default="push"),
    x_hub_signature_256: str | None = Header(default=None),
):
    body = await request.body()
    payload = await request.json()

    org = await _get_org(db, tenant_slug)
    if x_github_event == "ping":
        return {"ok": True, "message": "pong"}

    repo_data = payload.get("repository", {})
    if not repo_data:
        raise HTTPException(status_code=400, detail="Missing repository")

    repo = await _upsert_repo(
        db,
        org,
        platform="github",
        external_id=str(repo_data.get("id")),
        name=repo_data.get("name", ""),
        full_name=repo_data.get("full_name", ""),
        url=repo_data.get("html_url", ""),
    )

    sha = payload.get("after") or payload.get("head_commit", {}).get("id", "unknown")
    change = Change(
        tenant_id=org.id,
        repository_id=repo.id,
        event_type=x_github_event,
        sha=sha,
        ref=payload.get("ref"),
        author_email=(payload.get("head_commit") or {}).get("author", {}).get("email"),
        is_pr=x_github_event == "pull_request",
    )
    db.add(change)
    await db.flush()

    # MVP: scan committed file list metadata; full diff fetch in V1
    files = _extract_github_files(payload)
    if files:
        findings = scan_files(files)
        await persist_findings_and_flags(db, org.id, repo, findings)

    await db.commit()
    return {"ok": True, "repository": repo.full_name, "event": x_github_event}


@router.post("/gitlab/{tenant_slug}")
async def gitlab_webhook(
    tenant_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_gitlab_event: str = Header(default="Push Hook"),
):
    payload = await request.json()
    org = await _get_org(db, tenant_slug)

    project = payload.get("project", {})
    repo = await _upsert_repo(
        db,
        org,
        platform="gitlab",
        external_id=str(project.get("id", "")),
        name=project.get("name", ""),
        full_name=project.get("path_with_namespace", ""),
        url=project.get("web_url", ""),
    )

    sha = payload.get("checkout_sha") or payload.get("after", "unknown")
    change = Change(
        tenant_id=org.id,
        repository_id=repo.id,
        event_type=x_gitlab_event,
        sha=sha,
        ref=(payload.get("ref") or "").replace("refs/heads/", ""),
        author_email=(payload.get("user_email") or payload.get("user_username")),
    )
    db.add(change)
    await db.flush()

    files = _extract_gitlab_files(payload)
    if files:
        findings = scan_files(files)
        await persist_findings_and_flags(db, org.id, repo, findings)

    await db.commit()
    return {"ok": True, "repository": repo.full_name, "event": x_gitlab_event}


async def _get_org(db: AsyncSession, slug: str) -> Organization:
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    org = result.scalar_one_or_none()
    if not org:
        org = await get_or_create_demo_org(db)
    return org


async def _upsert_repo(
    db: AsyncSession,
    org: Organization,
    platform: str,
    external_id: str,
    name: str,
    full_name: str,
    url: str,
) -> Repository:
    result = await db.execute(
        select(Repository).where(
            Repository.tenant_id == org.id,
            Repository.platform == platform,
            Repository.external_id == external_id,
        )
    )
    repo = result.scalar_one_or_none()
    if repo:
        return repo
    repo = Repository(
        tenant_id=org.id,
        platform=platform,
        external_id=external_id,
        name=name,
        full_name=full_name,
        url=url,
    )
    db.add(repo)
    await db.flush()
    return repo


def _extract_github_files(payload: dict) -> dict[str, str]:
    files: dict[str, str] = {}
    for commit in payload.get("commits", [])[:3]:
        for path in commit.get("modified", []) + commit.get("added", []):
            if path.endswith((".env", ".json", ".ts", ".js", ".yaml", ".yml")):
                files[path] = commit.get("message", "") + f"\n// file: {path}"
    return files


def _extract_gitlab_files(payload: dict) -> dict[str, str]:
    files: dict[str, str] = {}
    for commit in payload.get("commits", [])[:3]:
        for path in commit.get("modified", []) + commit.get("added", []):
            if path.endswith((".env", ".json", ".ts", ".js", ".yaml", ".yml")):
                files[path] = commit.get("message", "") + f"\n// file: {path}"
    return files


def verify_github_signature(secret: str, body: bytes, signature: str | None) -> bool:
    if not secret or not signature:
        return True
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
