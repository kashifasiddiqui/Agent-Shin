from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PatchRiskLevel(str, Enum):
    SAFE = "safe"
    REVIEW = "review"
    HIGH_RISK = "high_risk"


class PatchAction(str, Enum):
    MODIFY_FILE = "modify"
    DELETE_FILE = "delete"
    CREATE_FILE = "create"


class FilePatch(BaseModel):
    finding_id: str = Field(description="Associated finding ID")
    file_path: str = Field(description="Relative path to target file")
    risk_level: PatchRiskLevel = Field(description="Assigned safety risk level")
    action: PatchAction = Field(default=PatchAction.MODIFY_FILE, description="Type of filesystem action")
    description: str = Field(description="Human-readable summary of the proposed patch")
    diff: str = Field(description="Unified diff preview of the modification")
    original_content: Optional[str] = Field(default=None, description="Original content before patch")
    patched_content: Optional[str] = Field(default=None, description="New content after patch")


class PatchPlan(BaseModel):
    patches: List[FilePatch] = Field(default_factory=list, description="Planned patches")
    total_patches: int = Field(default=0)
    safe_count: int = Field(default=0)
    review_count: int = Field(default=0)
    high_risk_count: int = Field(default=0)
