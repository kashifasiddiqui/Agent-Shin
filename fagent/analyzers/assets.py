from pathlib import Path
from typing import List
from fagent.analyzers.base import BaseAnalyzer
from fagent.schemas.finding import Finding, FindingCategory, Severity, FindingStatus
from fagent.schemas.graph import ProjectGraph, AssetType


class AssetAnalyzer(BaseAnalyzer):
    """Deterministic analyzer for images, fonts, and static assets."""

    @property
    def category_name(self) -> str:
        return "asset"

    def analyze(self, project_root: Path, graph: ProjectGraph) -> List[Finding]:
        findings: List[Finding] = []
        counter = 1

        for asset in graph.assets:
            # 1. Check unreferenced assets
            if not asset.is_referenced:
                # Favicon / manifest / public root assets are commonly accessed directly via HTML or browser
                if not asset.file_path.endswith("favicon.ico") and not asset.file_path.endswith("favicon.svg"):
                    findings.append(
                        Finding(
                            id=f"ASSET-{counter:04d}",
                            category=FindingCategory.ASSET,
                            severity=Severity.LOW,
                            message=f"Static asset '{asset.file_path}' is never referenced in source code",
                            file=asset.file_path,
                            evidence={"size_bytes": asset.size_bytes, "rule": "unreferenced-asset"},
                            fixable=True,
                            status=FindingStatus.DETECTED,
                        )
                    )
                    counter += 1

            # 2. Check large unoptimized assets (>1MB)
            if asset.size_bytes > 1_000_000 and asset.asset_type == AssetType.IMAGE:
                mb_size = round(asset.size_bytes / (1024 * 1024), 2)
                findings.append(
                    Finding(
                        id=f"ASSET-{counter:04d}",
                        category=FindingCategory.PERFORMANCE,
                        severity=Severity.MEDIUM,
                        message=f"Large image asset '{asset.file_path}' ({mb_size} MB) may impact load time",
                        file=asset.file_path,
                        evidence={"size_bytes": asset.size_bytes, "threshold": 1_000_000, "rule": "large-image-asset"},
                        fixable=False,
                        status=FindingStatus.DETECTED,
                    )
                )
                counter += 1

        return findings
