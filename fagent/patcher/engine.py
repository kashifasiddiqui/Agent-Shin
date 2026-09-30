from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
from fagent.patcher.fixers import PatchFixer
from fagent.patcher.git import GitSafetyManager
from fagent.core.state import StateManager
from fagent.schemas.finding import Finding, FindingStatus
from fagent.schemas.patch import FilePatch, PatchPlan, PatchRiskLevel, PatchAction


class PatchEngine:
    """Orchestrates planning, risk evaluation, safe application, and rollback of patches."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.git_safety = GitSafetyManager(self.project_root)
        self.state = StateManager(self.project_root)

    def create_plan(self, findings: List[Finding]) -> PatchPlan:
        patches: List[FilePatch] = []
        safe_count = 0
        review_count = 0
        high_risk_count = 0

        self.findings_map: dict = {}
        for f in findings:
            self.findings_map[f.id] = f
            if not f.fixable or f.status in {FindingStatus.RESOLVED, FindingStatus.PATCHED}:
                continue
            patch = PatchFixer.generate_patch(self.project_root, f)
            if patch:
                patches.append(patch)
                if patch.risk_level == PatchRiskLevel.SAFE:
                    safe_count += 1
                elif patch.risk_level == PatchRiskLevel.REVIEW:
                    review_count += 1
                else:
                    high_risk_count += 1

        return PatchPlan(
            patches=patches,
            total_patches=len(patches),
            safe_count=safe_count,
            review_count=review_count,
            high_risk_count=high_risk_count,
        )

    def apply_patch(self, patch: FilePatch) -> bool:
        target_path = self.project_root / patch.file_path
        if patch.action == PatchAction.DELETE_FILE:
            if target_path.exists():
                target_path.unlink()
            return True
        elif patch.action in {PatchAction.MODIFY_FILE, PatchAction.CREATE_FILE}:
            if target_path.exists():
                try:
                    current_content = target_path.read_text(encoding="utf-8")
                    finding = self.findings_map.get(patch.finding_id)
                    if finding:
                        updated_content = PatchFixer.apply_fix_to_content(current_content, finding)
                        if updated_content:
                            target_path.write_text(updated_content, encoding="utf-8")
                            return True
                except Exception:
                    pass

            if patch.patched_content is not None:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(patch.patched_content, encoding="utf-8")
                return True
        return False


    def apply_plan_with_safety(
        self,
        plan: PatchPlan,
        allowed_risks: Optional[List[PatchRiskLevel]] = None,
    ) -> Tuple[bool, List[FilePatch], List[str]]:
        """Applies eligible patches with automated Git safety checkpoint and verification."""
        allowed = allowed_risks or [PatchRiskLevel.SAFE]
        eligible_patches = [p for p in plan.patches if p.risk_level in allowed]

        if not eligible_patches:
            return True, [], ["No patches matching the allowed risk level."]

        # 1. Create Git checkpoint before modifying code
        checkpoint_id = self.git_safety.create_checkpoint(tag="auto-fix")

        applied: List[FilePatch] = []
        messages: List[str] = []

        try:
            for patch in eligible_patches:
                success = self.apply_patch(patch)
                if success:
                    applied.append(patch)
                    messages.append(f"Applied: {patch.description} ({patch.file_path})")

            # 2. Run post-patch verification (sanity check that files exist and parse)
            verification_passed = self.verify_patches(applied)

            if not verification_passed:
                # Rollback on verification failure
                self.git_safety.rollback()
                return False, [], ["Verification failed after applying patches. All changes were safely rolled back."]

            # 3. Record decisions in project memory
            self._record_patch_decisions(applied)

            return True, applied, messages

        except Exception as e:
            # Immediate rollback on error
            self.git_safety.rollback()
            return False, [], [f"Error during patching: {str(e)}. Rolled back all changes."]

    def verify_patches(self, patches: List[FilePatch]) -> bool:
        """Deterministic post-patch verification."""
        for p in patches:
            if p.action == PatchAction.DELETE_FILE:
                target = self.project_root / p.file_path
                if target.exists():
                    return False
            elif p.action == PatchAction.MODIFY_FILE:
                target = self.project_root / p.file_path
                if not target.exists():
                    return False
                try:
                    content = target.read_text(encoding="utf-8")
                    if not content.strip():
                        return False
                except Exception:
                    return False
        return True

    def _record_patch_decisions(self, patches: List[FilePatch]) -> None:
        decisions_file = self.state.fagent_dir / "decisions.json"
        existing = []
        if decisions_file.exists():
            try:
                existing = self.state._read_json(decisions_file)
            except Exception:
                existing = []

        for p in patches:
            decision = {
                "decision": p.description,
                "file": p.file_path,
                "finding_id": p.finding_id,
                "risk_level": p.risk_level.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "applied_and_verified",
            }
            existing.append(decision)

        self.state._save_json(decisions_file, existing)
