import difflib
import re
from pathlib import Path
from typing import Optional
from fagent.schemas.finding import Finding, FindingCategory
from fagent.schemas.patch import FilePatch, PatchAction, PatchRiskLevel


class PatchFixer:
    """Generates unified diffs and replacement content for fixable findings."""

    @staticmethod
    def apply_fix_to_content(content: str, finding: Finding) -> Optional[str]:
        # 1. Unused import fix
        if "no-unused-imports" in finding.evidence.get("rule", "") or "Unused import" in finding.message:
            ident = finding.evidence.get("identifier")
            if ident:
                return PatchFixer._fix_unused_import(content, ident)

        # 2. Unsafe target="_blank" fix
        if "react-jsx-no-target-blank" in finding.evidence.get("rule", "") or "target='_blank'" in finding.message:
            return PatchFixer._fix_target_blank(content)

        # 3. Missing key fix
        if "react-jsx-key" in finding.evidence.get("rule", "") or "Missing 'key' prop" in finding.message:
            tag = finding.evidence.get("tag", "")
            return PatchFixer._fix_missing_key(content, tag)

        # 4. Consistent border radius fix
        if "consistent-border-radius" in finding.evidence.get("rule", ""):
            dominant = finding.evidence.get("dominant_radius")
            outlier = finding.evidence.get("outlier_radius")
            if dominant and outlier:
                return PatchFixer._fix_border_radius(content, outlier, dominant)

        # 5. Missing alt attribute fix
        if "missing-alt" in finding.evidence.get("rule", "") or "Missing alt" in finding.message:
            return PatchFixer._fix_missing_alt(content)

        return None

    @staticmethod
    def generate_patch(project_root: Path, finding: Finding) -> Optional[FilePatch]:
        if not finding.file:
            return None

        file_path = project_root / finding.file
        if not file_path.exists():
            return None

        try:
            original_content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

        # 1. Unused import fix (SAFE)
        if "no-unused-imports" in finding.evidence.get("rule", "") or "Unused import" in finding.message:
            ident = finding.evidence.get("identifier")
            if not ident:
                return None
            patched_content = PatchFixer.apply_fix_to_content(original_content, finding)
            if patched_content and patched_content != original_content:
                diff = PatchFixer._create_diff(finding.file, original_content, patched_content)
                return FilePatch(
                    finding_id=finding.id,
                    file_path=finding.file,
                    risk_level=PatchRiskLevel.SAFE,
                    action=PatchAction.MODIFY_FILE,
                    description=f"Remove unused import '{ident}'",
                    diff=diff,
                    original_content=original_content,
                    patched_content=patched_content,
                )

        # 2. Unsafe target="_blank" fix (SAFE)
        if "react-jsx-no-target-blank" in finding.evidence.get("rule", "") or "target='_blank'" in finding.message:
            patched_content = PatchFixer._fix_target_blank(original_content)
            if patched_content and patched_content != original_content:
                diff = PatchFixer._create_diff(finding.file, original_content, patched_content)
                return FilePatch(
                    finding_id=finding.id,
                    file_path=finding.file,
                    risk_level=PatchRiskLevel.SAFE,
                    action=PatchAction.MODIFY_FILE,
                    description="Add rel='noopener noreferrer' to external target='_blank' link",
                    diff=diff,
                    original_content=original_content,
                    patched_content=patched_content,
                )

        # 3. Missing key in .map() (REVIEW)
        if "react-jsx-key" in finding.evidence.get("rule", "") or "Missing 'key' prop" in finding.message:
            tag = finding.evidence.get("tag", "")
            patched_content = PatchFixer._fix_missing_key(original_content, tag)
            if patched_content and patched_content != original_content:
                diff = PatchFixer._create_diff(finding.file, original_content, patched_content)
                return FilePatch(
                    finding_id=finding.id,
                    file_path=finding.file,
                    risk_level=PatchRiskLevel.REVIEW,
                    action=PatchAction.MODIFY_FILE,
                    description=f"Add deterministic key prop to mapped JSX element {tag}",
                    diff=diff,
                    original_content=original_content,
                    patched_content=patched_content,
                )

        # 4. Consistent border radius harmonization (SAFE)
        if "consistent-border-radius" in finding.evidence.get("rule", ""):
            dominant = finding.evidence.get("dominant_radius")
            outlier = finding.evidence.get("outlier_radius")
            if dominant and outlier:
                patched_content = PatchFixer._fix_border_radius(original_content, outlier, dominant)
                if patched_content and patched_content != original_content:
                    diff = PatchFixer._create_diff(finding.file, original_content, patched_content)
                    return FilePatch(
                        finding_id=finding.id,
                        file_path=finding.file,
                        risk_level=PatchRiskLevel.SAFE,
                        action=PatchAction.MODIFY_FILE,
                        description=f"Harmonize outlier radius '{outlier}' to dominant '{dominant}'",
                        diff=diff,
                        original_content=original_content,
                        patched_content=patched_content,
                    )

        # 5. Missing image alt tag (SAFE)
        if "missing-alt" in finding.evidence.get("rule", "") or "Missing alt" in finding.message:
            patched_content = PatchFixer._fix_missing_alt(original_content)
            if patched_content and patched_content != original_content:
                diff = PatchFixer._create_diff(finding.file, original_content, patched_content)
                return FilePatch(
                    finding_id=finding.id,
                    file_path=finding.file,
                    risk_level=PatchRiskLevel.SAFE,
                    action=PatchAction.MODIFY_FILE,
                    description="Add decorative or placeholder alt attribute to image element",
                    diff=diff,
                    original_content=original_content,
                    patched_content=patched_content,
                )

        # 6. Unreferenced asset deletion (SAFE)
        if finding.category == FindingCategory.ASSET and "unreferenced-asset" in finding.evidence.get("rule", ""):
            diff = f"--- a/{finding.file}\n+++ /dev/null\n@@ -1 +0,0 @@\n-[deleted binary or unreferenced asset]\n"
            return FilePatch(
                finding_id=finding.id,
                file_path=finding.file,
                risk_level=PatchRiskLevel.SAFE,
                action=PatchAction.DELETE_FILE,
                description=f"Delete unreferenced asset '{finding.file}'",
                diff=diff,
                original_content=original_content,
                patched_content="",
            )

        return None

    @staticmethod
    def _fix_unused_import(content: str, identifier: str) -> str:
        lines = content.splitlines(keepends=True)
        new_lines = []

        for line in lines:
            if line.strip().startswith("import ") and identifier in line:
                # If named import inside { ... }
                if "{" in line and "}" in line:
                    before_brace = line[:line.find("{") + 1]
                    inside_brace = line[line.find("{") + 1:line.find("}")]
                    after_brace = line[line.find("}"):]

                    parts = [p.strip() for p in inside_brace.split(",") if p.strip()]
                    remaining = [p for p in parts if p != identifier and not p.endswith(f" as {identifier}")]

                    if remaining:
                        new_line = before_brace + " " + ", ".join(remaining) + " " + after_brace
                        new_lines.append(new_line)
                    else:
                        # No named imports remain. Check if there was a default import before brace
                        if "," in before_brace:
                            # e.g. import React, { useEffect } from 'react';
                            clean_before = before_brace.replace("{", "").replace(",", "").strip()
                            new_line = f"{clean_before} {after_brace.strip()}\n"
                            new_lines.append(new_line)
                        else:
                            # Entire import was just { identifier }, remove line entirely
                            continue
                else:
                    # Default import only, e.g. import Foo from './Foo';
                    continue
            else:
                new_lines.append(line)

        return "".join(new_lines)

    @staticmethod
    def _fix_target_blank(content: str) -> str:
        pattern = re.compile(r"""(<a\s+[^>]*?target=['"]_blank['"][^>]*?)(/?>)""", re.IGNORECASE)
        def repl(match):
            attrs = match.group(1)
            closing = match.group(2)
            if "rel=" not in attrs.lower():
                return f'{attrs} rel="noopener noreferrer"{closing}'
            return match.group(0)

        return pattern.sub(repl, content)

    @staticmethod
    def _fix_missing_key(content: str, tag: str) -> str:
        # Match .map((param, index) => <Tag or .map(param => <Tag
        map_pattern = re.compile(
            r"""(?P<prefix>\.(?:map)\s*\(\s*(?:\((?P<p1>\w+)(?:,\s*(?P<idx>\w+))?\)|(?P<p2>\w+))\s*=>\s*(?:\(\s*)?[\s\n]*)(?P<tag><[A-Z\w]+)(?P<attrs>[^>]*?)(?P<closing>/?>)""",
            re.MULTILINE
        )

        def repl(match):
            prefix = match.group("prefix")
            p_name = match.group("p1") or match.group("p2") or "item"
            idx_name = match.group("idx")
            tag_name = match.group("tag")
            attrs = match.group("attrs")
            closing = match.group("closing")

            if "key=" in attrs:
                return match.group(0)

            key_expr = f'{p_name}.id || {p_name}.title || {p_name}' if not idx_name else f'{p_name}.id || {idx_name}'
            return f'{prefix}{tag_name} key={{{key_expr}}}{attrs}{closing}'

        return map_pattern.sub(repl, content)

    @staticmethod
    def _fix_border_radius(content: str, outlier: str, dominant: str) -> str:
        # e.g. replacing 'rounded-3xl' or 'border-radius: 24px' with dominant
        pattern = re.compile(r"\b" + re.escape(outlier) + r"\b")
        return pattern.sub(dominant, content)

    @staticmethod
    def _fix_missing_alt(content: str) -> str:
        # Matches <img without alt attribute
        pattern = re.compile(r"""(<img\s+[^>]*?)(/?>)""", re.IGNORECASE)
        def repl(match):
            attrs = match.group(1)
            closing = match.group(2)
            if "alt=" not in attrs.lower():
                return f'{attrs} alt=""{closing}'
            return match.group(0)

        return pattern.sub(repl, content)

    @staticmethod
    def _create_diff(file_path: str, old: str, new: str) -> str:
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        return "\n".join(diff)
