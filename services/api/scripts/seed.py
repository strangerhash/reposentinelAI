"""Seed demo data for EstateGuard development."""

import asyncio
import uuid

from sqlalchemy import select

from app.database import SessionLocal, engine, Base
from app.models import Engagement, Organization, Repository


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        result = await db.execute(select(Organization).where(Organization.slug == "demo"))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(name="Xenqube Demo Consultancy", slug="demo", plan_tier="business")
            db.add(org)
            await db.flush()

        repos = [
            Repository(
                tenant_id=org.id,
                platform="github",
                external_id="1001",
                name="payment-service",
                full_name="targetco/payment-service",
                url="https://github.com/targetco/payment-service",
                criticality_tier="critical",
            ),
            Repository(
                tenant_id=org.id,
                platform="gitlab",
                external_id="2001",
                name="auth-gateway",
                full_name="targetco/auth-gateway",
                url="https://gitlab.com/targetco/auth-gateway",
                criticality_tier="high",
            ),
            Repository(
                tenant_id=org.id,
                platform="github",
                external_id="1002",
                name="web-app",
                full_name="targetco/web-app",
                url="https://github.com/targetco/web-app",
                criticality_tier="medium",
            ),
        ]

        repo_ids = []
        for repo in repos:
            existing = await db.execute(
                select(Repository).where(
                    Repository.tenant_id == org.id,
                    Repository.platform == repo.platform,
                    Repository.external_id == repo.external_id,
                )
            )
            if existing.scalar_one_or_none():
                continue
            db.add(repo)
            await db.flush()
            repo_ids.append(repo.id)

        if repo_ids:
            engagement = Engagement(
                tenant_id=org.id,
                name="TargetCo Acquisition — Phase 1",
                target_org="TargetCo Inc.",
                status="draft",
                repo_ids=repo_ids,
                white_label={"report_title": "TargetCo Security Assessment"},
            )
            db.add(engagement)

        await db.commit()
        print("Seeded demo org, repos, and draft engagement.")


if __name__ == "__main__":
    asyncio.run(seed())
