"""Pydantic schemas for FAgent."""

from fagent.schemas.project import ProjectInfo, Framework, Language, PackageManager, StylingSystem
from fagent.schemas.graph import ProjectGraph, ComponentNode, RouteNode, AssetNode
from fagent.schemas.finding import Finding, FindingCategory, Severity, FindingStatus, CategoryScore, AuditReport
from fagent.schemas.design import DesignSystem, ColorUsage, RadiusUsage
from fagent.schemas.patch import FilePatch, PatchPlan, PatchRiskLevel, PatchAction

__all__ = [
    "ProjectInfo",
    "Framework",
    "Language",
    "PackageManager",
    "StylingSystem",
    "ProjectGraph",
    "ComponentNode",
    "RouteNode",
    "AssetNode",
    "Finding",
    "FindingCategory",
    "Severity",
    "FindingStatus",
    "CategoryScore",
    "AuditReport",
    "DesignSystem",
    "ColorUsage",
    "RadiusUsage",
    "FilePatch",
    "PatchPlan",
    "PatchRiskLevel",
    "PatchAction",
]



