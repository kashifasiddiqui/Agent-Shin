from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from fagent.analyzers.base import BaseAnalyzer
from fagent.analyzers.code import CodeAnalyzer
from fagent.analyzers.assets import AssetAnalyzer
from fagent.analyzers.design import DesignAnalyzer
from fagent.core.state import StateManager
from fagent.schemas.finding import (
    AuditReport,
    CategoryScore,
    Finding,
    FindingCategory,
    Severity,
)
from fagent.schemas.graph import ProjectGraph


class AuditEngine:
    """Orchestrates all analyzers and calculates project health metrics."""

    SEVERITY_PENALTIES = {
        Severity.CRITICAL: 20,
        Severity.HIGH: 10,
        Severity.MEDIUM: 5,
        Severity.LOW: 2,
        Severity.INFO: 0,
    }

    def __init__(self, project_root: Path, analyzers: Optional[List[BaseAnalyzer]] = None):
        self.project_root = Path(project_root).resolve()
        self.analyzers: List[BaseAnalyzer] = analyzers or [
            CodeAnalyzer(),
            AssetAnalyzer(),
            DesignAnalyzer(),
        ]


    def run_audit(self, graph: ProjectGraph) -> AuditReport:
        all_findings: List[Finding] = []

        # Run registered analyzers
        for analyzer in self.analyzers:
            findings = analyzer.analyze(self.project_root, graph)
            all_findings.extend(findings)

        # Group findings by category and calculate scores
        category_map: Dict[FindingCategory, List[Finding]] = {cat: [] for cat in FindingCategory}
        for f in all_findings:
            category_map[f.category].append(f)

        category_scores: Dict[str, CategoryScore] = {}
        weighted_scores: List[int] = []

        for cat, findings in category_map.items():
            penalty = 0
            crit = 0
            high = 0
            med = 0
            low = 0

            for f in findings:
                penalty += self.SEVERITY_PENALTIES.get(f.severity, 0)
                if f.severity == Severity.CRITICAL:
                    crit += 1
                elif f.severity == Severity.HIGH:
                    high += 1
                elif f.severity == Severity.MEDIUM:
                    med += 1
                elif f.severity == Severity.LOW:
                    low += 1

            cat_score = max(0, 100 - penalty)
            # Only include categories in report that have analyzers active or findings
            if cat in [FindingCategory.CODE, FindingCategory.ASSET, FindingCategory.PERFORMANCE] or findings:
                category_scores[cat.value] = CategoryScore(
                    category=cat,
                    score=cat_score,
                    total_findings=len(findings),
                    critical_count=crit,
                    high_count=high,
                    medium_count=med,
                    low_count=low,
                )
                weighted_scores.append(cat_score)

        overall = round(sum(weighted_scores) / len(weighted_scores)) if weighted_scores else 100
        fixable_count = sum(1 for f in all_findings if f.fixable)

        report = AuditReport(
            overall_score=overall,
            category_scores=category_scores,
            findings=all_findings,
            total_findings=len(all_findings),
            fixable_findings=fixable_count,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        return report
