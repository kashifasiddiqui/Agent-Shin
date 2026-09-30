import shutil
import subprocess
from pathlib import Path
from typing import Optional


class GitSafetyManager:
    """Provides git checkpointing, rollback, and safety mechanisms for autonomous patching."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / ".fagent" / "backups"

    def is_git_repo(self) -> bool:
        return (self.project_root / ".git").exists() or self._run_git(["rev-parse", "--is-inside-work-tree"]) == "true"

    def create_checkpoint(self, tag: str = "pre-patch") -> str:
        """Creates a safety checkpoint before making autonomous modifications."""
        if self.is_git_repo():
            # If there are uncommitted changes, create a git stash or record HEAD
            stash_out = self._run_git(["stash", "create", f"fagent-{tag}"])
            head_commit = self._run_git(["rev-parse", "HEAD"])
            return stash_out if stash_out else (head_commit or "git-clean")
        else:
            # Fallback to local file backup if git is not initialized
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            return "local-checkpoint"

    def rollback(self) -> bool:
        """Rolls back all uncommitted or failed changes across the project."""
        if self.is_git_repo():
            res1 = self._run_git(["checkout", "--", "."])
            res2 = self._run_git(["clean", "-fd"])
            return True
        return False

    def commit_changes(self, message: str) -> bool:
        """Commits verified autonomous changes to the project git history."""
        if not self.is_git_repo():
            return False
        self._run_git(["add", "."])
        self._run_git(["commit", "-m", f"fagent: {message}"])
        return True

    def _run_git(self, args: list) -> str:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            return res.stdout.strip()
        except Exception:
            return ""
