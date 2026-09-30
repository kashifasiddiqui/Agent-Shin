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
