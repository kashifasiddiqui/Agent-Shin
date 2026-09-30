from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from fagent.core.state import StateManager
from fagent.schemas.finding import Finding


class ProjectMemory:
    """Manages project-specific memory, approved decisions, and known design exceptions."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.state = StateManager(self.project_root)
        self.decisions_file = self.state.fagent_dir / "decisions.json"

    def get_decisions(self) -> List[Dict[str, Any]]:
        if not self.decisions_file.exists():
            return []
        try:
            return self.state._read_json(self.decisions_file)
        except Exception:
            return []

    def record_decision(
        self,
        decision: str,
        file_path: Optional[str] = None,
        finding_id: Optional[str] = None,
        reason: Optional[str] = None,
        source: str = "user-approved"
    ) -> Dict[str, Any]:
        """Records an intentional design choice, fix, or approved exception in project memory."""
        decisions = self.get_decisions()
        entry = {
            "id": f"DEC-{len(decisions) + 1:04d}",
            "decision": decision,
            "file": file_path,
            "finding_id": finding_id,
            "reason": reason or "Established project pattern",
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        decisions.append(entry)
        self.state.fagent_dir.mkdir(parents=True, exist_ok=True)
        self.state._save_json(self.decisions_file, decisions)
        return entry

    def is_known_exception(self, finding: Finding) -> bool:
        """Checks if finding matches a recorded exception."""
        decisions = self.get_decisions()
        for d in decisions:
            if d.get("finding_id") == finding.id:
                return True
            if d.get("file") == finding.file and finding.message in d.get("decision", ""):
                return True
        return False
