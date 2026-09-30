import json
from pathlib import Path
from typing import Any, Dict, Optional
from fagent.schemas.project import ProjectInfo
from fagent.schemas.graph import ProjectGraph


FAGENT_DIR_NAME = ".fagent"
CONFIG_FILE = "config.json"
PROJECT_FILE = "project.json"
GRAPH_FILE = "graph.json"
FINDINGS_FILE = "findings.json"
DECISIONS_FILE = "decisions.json"
DESIGN_SYSTEM_FILE = "design-system.json"


AUDIT_FILE = "audit.json"


class StateManager:
    """Manages reading and writing project-specific .fagent/ metadata."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.fagent_dir = self.project_root / FAGENT_DIR_NAME

    def is_initialized(self) -> bool:
        return self.fagent_dir.exists() and (self.fagent_dir / CONFIG_FILE).exists()

    def init_fagent(self, config_override: Optional[Dict[str, Any]] = None) -> Path:
        """Create .fagent directory and baseline configuration files."""
        self.fagent_dir.mkdir(parents=True, exist_ok=True)
        (self.fagent_dir / "history").mkdir(parents=True, exist_ok=True)

        config_data = {
            "version": "0.1.0",
            "auto_fix_safe": True,
            "max_iterations": 5,
            "require_approval_for_high_risk": True,
            "ignored_paths": [
                "node_modules",
                "dist",
                "build",
                ".git",
                ".fagent"
            ],
            **(config_override or {})
        }

        self._save_json(self.fagent_dir / CONFIG_FILE, config_data)
        
        # Initialize empty collections if they don't exist yet
        for filename in [DECISIONS_FILE, FINDINGS_FILE]:
            target = self.fagent_dir / filename
            if not target.exists():
                self._save_json(target, [])

        return self.fagent_dir

    def save_project_info(self, project_info: ProjectInfo) -> Path:
        target = self.fagent_dir / PROJECT_FILE
        self._save_json(target, project_info.model_dump(mode="json"))
        return target

    def save_graph(self, graph: ProjectGraph) -> Path:
        target = self.fagent_dir / GRAPH_FILE
        self._save_json(target, graph.model_dump(mode="json"))
        return target

    def save_findings(self, findings: list) -> Path:
        target = self.fagent_dir / FINDINGS_FILE
        data = [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in findings]
        self._save_json(target, data)
        return target

    def save_audit_report(self, report) -> Path:
        target = self.fagent_dir / AUDIT_FILE
        data = report.model_dump(mode="json") if hasattr(report, "model_dump") else report
        self._save_json(target, data)
        return target

    def load_project_info(self) -> Optional[ProjectInfo]:
        target = self.fagent_dir / PROJECT_FILE
        if not target.exists():
            return None
        data = self._read_json(target)
        return ProjectInfo.model_validate(data)

    def load_graph(self) -> Optional[ProjectGraph]:
        target = self.fagent_dir / GRAPH_FILE
        if not target.exists():
            return None
        data = self._read_json(target)
        return ProjectGraph.model_validate(data)

    def load_findings(self) -> list:
        target = self.fagent_dir / FINDINGS_FILE
        if not target.exists():
            return []
        return self._read_json(target)

    def load_audit_report(self) -> Optional[dict]:
        target = self.fagent_dir / AUDIT_FILE
        if not target.exists():
            return None
        return self._read_json(target)

    def _save_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


    def _read_json(self, path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

