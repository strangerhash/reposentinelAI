import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str
    slug: str


class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan_tier: str

    model_config = {"from_attributes": True}


class RepositoryCreate(BaseModel):
    platform: str
    external_id: str
    name: str
    full_name: str
    url: str
    default_branch: str = "main"
    criticality_tier: str = "medium"


class RepositoryOut(BaseModel):
    id: uuid.UUID
    platform: str
    full_name: str
    url: str
    criticality_tier: str
    is_active: bool
    last_scan_at: datetime | None
    open_flags: int = 0

    model_config = {"from_attributes": True}


class EngagementCreate(BaseModel):
    name: str
    target_org: str | None = None
    repo_ids: list[uuid.UUID] = Field(default_factory=list)
    expires_at: datetime | None = None
    white_label: dict | None = None


class EngagementOut(BaseModel):
    id: uuid.UUID
    name: str
    target_org: str | None
    status: str
    repo_ids: list
    report_summary: dict | None
    white_label: dict | None
    expires_at: datetime | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class FlagOut(BaseModel):
    id: uuid.UUID
    title: str
    severity: str
    status: str
    repository_id: uuid.UUID
    engagement_id: uuid.UUID | None
    explanation: str | None
    remediation_steps: list | None
    created_at: datetime
    repository_full_name: str | None = None

    model_config = {"from_attributes": True}


class FlagUpdate(BaseModel):
    status: str | None = None


class PostureOut(BaseModel):
    score: int
    trend_90d: int
    critical_open: int
    high_open: int
    total_open: int
    repos_scanned: int


class EngagementReportOut(BaseModel):
    engagement_id: uuid.UUID
    engagement_name: str
    target_org: str | None
    generated_at: datetime
    posture_score: int
    summary: dict
    flags_by_severity: dict
    top_risks: list[dict]
    repositories: list[dict]
