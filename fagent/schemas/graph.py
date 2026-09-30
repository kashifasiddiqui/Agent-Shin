from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from fagent.schemas.project import ProjectInfo


class AssetType(str, Enum):
    IMAGE = "image"
    SVG = "svg"
    FONT = "font"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"


class AssetNode(BaseModel):
    file_path: str = Field(description="Relative path to the asset")
    asset_type: AssetType = Field(description="Classification of asset")
    size_bytes: int = Field(default=0, description="Size in bytes")
    is_referenced: bool = Field(default=False, description="Whether the asset is imported or referenced in code")
    referenced_by: List[str] = Field(default_factory=list, description="Files referencing this asset")


class ComponentNode(BaseModel):
    name: str = Field(description="Component name")
    file_path: str = Field(description="Relative file path to component")
    is_page: bool = Field(default=False, description="Whether this component acts as a page/route view")
    is_layout: bool = Field(default=False, description="Whether this component acts as a shared layout")
    imported_components: List[str] = Field(default_factory=list, description="Components imported by this component")
    used_in: List[str] = Field(default_factory=list, description="Components or files that import this component")
    props: List[str] = Field(default_factory=list, description="Props recognized on this component")
    hooks: List[str] = Field(default_factory=list, description="React hooks used in this component")
    lines_of_code: int = Field(default=0, description="Lines of code in component file")


class RouteNode(BaseModel):
    path: str = Field(description="URL route path, e.g. '/', '/about'")
    component_name: Optional[str] = Field(default=None, description="Component handling this route")
    file_path: Optional[str] = Field(default=None, description="File defining or handling this route")
    layout: Optional[str] = Field(default=None, description="Layout wrapping this route")


class ProjectGraph(BaseModel):
    project: ProjectInfo = Field(description="Core project information")
    components: Dict[str, ComponentNode] = Field(default_factory=dict, description="Components keyed by name or relative path")
    routes: List[RouteNode] = Field(default_factory=list, description="Application routes")
    assets: List[AssetNode] = Field(default_factory=list, description="Project static assets")
    entry_routes: List[str] = Field(default_factory=list, description="Top-level entry route paths")
    generated_at: str = Field(description="ISO 8601 timestamp of graph generation")
