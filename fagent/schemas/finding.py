from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class FindingCategory(str, Enum):
    CODE = "code"
    DESIGN = "design"
    RESPONSIVE = "responsive"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    ASSET = "asset"
    ARCHITECTURE = "architecture"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingStatus(str, Enum):
    DETECTED = "detected"
    VALIDATED = "validated"
    PRIORITIZED = "prioritized"
    PLANNED = "planned"
    PATCHED = "patched"
    VERIFIED = "verified"
    RESOLVED = "resolved"
    ROLLED_BACK = "rolled_back"


class Finding(BaseModel):
    id: str = Field(description="Unique identifier e.g. CODE-0001, UI-0042")
    category: FindingCategory = Field(description="Finding category")
    severity: Severity = Field(description="Severity level")
    message: str = Field(description="Short human-readable summary of the finding")
    file: Optional[str] = Field(default=None, description="Affected file path relative to project root")
    line: Optional[int] = Field(default=None, description="Affected line number if applicable")
    component: Optional[str] = Field(default=None, description="Affected component name if applicable")
    route: Optional[str] = Field(default=None, description="Affected route if applicable")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Concrete deterministic evidence backing this finding")
    fixable: bool = Field(default=False, description="Whether this finding is automatically fixable")
    status: FindingStatus = Field(default=FindingStatus.DETECTED, description="Current lifecycle state of the finding")


class CategoryScore(BaseModel):
    category: FindingCategory = Field(description="Finding category")
    score: int = Field(ge=0, le=100, description="Score from 0 to 100")
    total_findings: int = Field(default=0, description="Total findings in this category")
    critical_count: int = Field(default=0)
    high_count: int = Field(default=0)
    medium_count: int = Field(default=0)
    low_count: int = Field(default=0)


class AuditReport(BaseModel):
    overall_score: int = Field(ge=0, le=100, description="Overall project health score (0-100)")
    category_scores: Dict[str, CategoryScore] = Field(default_factory=dict)
    findings: list[Finding] = Field(default_factory=list)
    total_findings: int = Field(default=0)
    fixable_findings: int = Field(default=0)
    created_at: str = Field(description="ISO timestamp of audit completion")

