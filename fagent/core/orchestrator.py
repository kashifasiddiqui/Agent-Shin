from typing import Any, Dict, List, Optional
from pathlib import Path
from fagent.scanner.project import ProjectScanner
from fagent.core.audit import AuditEngine
from fagent.core.state import StateManager
from fagent.core.memory import ProjectMemory
from fagent.schemas.patch import PatchRiskLevel


class HealingLoop:
    """Autonomous closed loop: Observe -> Analyze -> Plan -> Patch -> Verify -> Learn -> Iterate."""

    def __init__(
        self,
        project_root: Path,
        max_iterations: int = 5,
        allow_review: bool = False,
        use_ai: bool = False,
        model: Optional[str] = None
    ):
        from fagent.patcher.engine import PatchEngine

        self.project_root = Path(project_root).resolve()
        self.max_iterations = max_iterations
        self.allow_review = allow_review
        self.use_ai = use_ai
        self.model = model
        self.state = StateManager(self.project_root)
        self.memory = ProjectMemory(self.project_root)
        self.patcher = PatchEngine(self.project_root)

    def run(self) -> Dict[str, Any]:
        history: List[Dict[str, Any]] = []
        total_applied = 0

        allowed_risks = [PatchRiskLevel.SAFE, PatchRiskLevel.REVIEW] if (self.allow_review or self.use_ai) else [PatchRiskLevel.SAFE]

        for iteration in range(1, self.max_iterations + 1):
            # 1. Observe (Scan)
            scanner = ProjectScanner(self.project_root)
            graph = scanner.scan()
            self.state.save_graph(graph)

            # 2. Analyze (Audit)
            audit_engine = AuditEngine(self.project_root)
            report = audit_engine.run_audit(graph)
            self.state.save_findings(report.findings)
            self.state.save_audit_report(report)

            # Filter out known exceptions
            active_findings = [f for f in report.findings if not self.memory.is_known_exception(f)]

            # 3. Plan (supports deterministic + AI synthesis)
            plan = self.patcher.create_plan(active_findings, use_ai=self.use_ai, model=self.model)
            eligible_patches = [p for p in plan.patches if p.risk_level in allowed_risks]

            iteration_record = {
                "iteration": iteration,
                "score_before": report.overall_score,
                "total_findings": len(active_findings),
                "fixable_count": len(eligible_patches),
                "applied_count": 0,
                "status": "in_progress",
            }

            # Stop Condition: No eligible fixable findings remain or score is 100%
            if not eligible_patches or report.overall_score == 100:
                iteration_record["status"] = "converged"
                history.append(iteration_record)
                break

            # 4. Act + 5. Verify + 6. Learn
            success, applied, msgs = self.patcher.apply_plan_with_safety(plan, allowed_risks=allowed_risks)

            if success and applied:
                iteration_record["applied_count"] = len(applied)
                iteration_record["status"] = "success"
                iteration_record["messages"] = msgs
                total_applied += len(applied)
            else:
                iteration_record["status"] = "failed_or_no_change"
                iteration_record["messages"] = msgs
                history.append(iteration_record)
                break

            history.append(iteration_record)

        # Final Scan & Audit
        final_scanner = ProjectScanner(self.project_root)
        final_graph = final_scanner.scan()
        final_report = AuditEngine(self.project_root).run_audit(final_graph)

        return {
            "iterations_run": len(history),
            "total_applied_fixes": total_applied,
            "final_score": final_report.overall_score,
            "final_findings_count": len(final_report.findings),
            "history": history,
        }
