import difflib
import re
from pathlib import Path
from typing import Optional
from fagent.reasoning.provider import LLMProvider, OpenRouterProvider
from fagent.reasoning.prompts import (
    EXPLAIN_SYSTEM_PROMPT,
    EXPLAIN_USER_TEMPLATE,
    FIX_PLANNER_SYSTEM_PROMPT,
    FIX_PLANNER_USER_TEMPLATE,
)
from fagent.schemas.finding import Finding
from fagent.schemas.graph import ProjectGraph
from fagent.schemas.patch import FilePatch, PatchAction, PatchRiskLevel


class LLMReasoningEngine:
    """Orchestrates model-based reasoning for finding explanations and AI-driven patch planning."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or OpenRouterProvider()

    def explain_finding(self, finding: Finding, graph: Optional[ProjectGraph] = None) -> str:
        """Asks the model to analyze and explain the finding with senior frontend engineering rigor."""
        framework_str = graph.project.framework.value if graph else "React"
        styling_str = ", ".join(s.value for s in graph.project.styling_systems) if graph else "Tailwind CSS"

        user_prompt = EXPLAIN_USER_TEMPLATE.format(
            finding_id=finding.id,
            category=finding.category.value,
            severity=finding.severity.value,
            file_path=finding.file or "Unknown",
            line=str(finding.line or "N/A"),
            message=finding.message,
            evidence=str(finding.evidence),
            framework=framework_str,
            styling=styling_str,
        )

        messages = [
            {"role": "system", "content": EXPLAIN_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        return self.provider.generate(messages, temperature=0.2)

    def generate_ai_patch(
        self,
        finding: Finding,
        project_root: Path,
        design_tokens: Optional[str] = None
    ) -> Optional[FilePatch]:
        """Uses LLM reasoning to generate a patch for complex or ambiguous findings."""
        if not finding.file:
            return None

        file_path = project_root / finding.file
        if not file_path.exists():
            return None

        try:
            original_content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

        ext = file_path.suffix.lstrip(".") or "tsx"

        user_prompt = FIX_PLANNER_USER_TEMPLATE.format(
            finding_id=finding.id,
            message=finding.message,
            file_path=finding.file,
            evidence=str(finding.evidence),
            design_tokens=design_tokens or "Standard Tailwind / CSS Tokens",
            file_ext=ext,
            file_content=original_content,
        )

        messages = [
            {"role": "system", "content": FIX_PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        response = self.provider.generate(messages, temperature=0.1)
        patched_code = self._extract_code_block(response)

        if not patched_code or patched_code.strip() == original_content.strip():
            return None

        # Build unified diff
        old_lines = original_content.splitlines(keepends=True)
        new_lines = patched_code.splitlines(keepends=True)
        diff = "\n".join(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"a/{finding.file}",
                tofile=f"b/{finding.file}",
                lineterm="",
            )
        )

        return FilePatch(
            finding_id=finding.id,
            file_path=finding.file,
            risk_level=PatchRiskLevel.REVIEW,
            action=PatchAction.MODIFY_FILE,
            description=f"AI-Generated fix for {finding.id}: {finding.message}",
            diff=diff,
            original_content=original_content,
            patched_content=patched_code,
        )

    @staticmethod
    def _extract_code_block(text: str) -> Optional[str]:
        """Extracts code block from markdown ``` fences."""
        code_block_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", text)
        if code_block_match:
            return code_block_match.group(1).rstrip()
        return text.strip() if text else None
