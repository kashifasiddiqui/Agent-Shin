import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from fagent.analyzers.base import BaseAnalyzer
from fagent.schemas.finding import Finding, FindingCategory, Severity, FindingStatus
from fagent.schemas.graph import ProjectGraph


IMPORT_STATEMENT_PATTERN = re.compile(
    r"""import\s+(?:(\w+)\s*,\s*)?(?:(?:\*\s+as\s+(\w+))|(?:\{([^}]+)\})|(\w+))\s+from\s+['"]([^'"]+)['"]""",
    re.MULTILINE
)
MAP_JSX_PATTERN = re.compile(
    r"""\.(?:map)\s*\(\s*(?:\([^)]*\)|\w+)\s*=>\s*(?:\(\s*)?(<[A-Z\w]+)(?P<attrs>[^>]*?)(?:/>|>)""",
    re.DOTALL
)
TARGET_BLANK_PATTERN = re.compile(
    r"""<a\s+([^>]*target=['"]_blank['"][^>]*)>""",
    re.IGNORECASE | re.MULTILINE
)
DANGEROUS_HTML_PATTERN = re.compile(
    r"""\bdangerouslySetInnerHTML\b""",
    re.MULTILINE
)


class CodeAnalyzer(BaseAnalyzer):
    """Deterministic static code analysis for React and TypeScript/JavaScript."""

    @property
    def category_name(self) -> str:
        return "code"

    def analyze(self, project_root: Path, graph: ProjectGraph) -> List[Finding]:
        findings: List[Finding] = []
        counter = 1

        src_dir = project_root / (graph.project.src_dir or "src")
        if not src_dir.exists():
            src_dir = project_root

        code_extensions = {".jsx", ".tsx", ".js", ".ts"}
        for file_path in src_dir.rglob("*"):
            if not file_path.is_file() or file_path.suffix not in code_extensions:
                continue
            if any(ignored in file_path.parts for ignored in ["node_modules", "dist", "build", ".fagent", ".git"]):
                continue

            rel_path = file_path.relative_to(project_root).as_posix()
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            lines = content.splitlines()

            # 1. Unused Imports Check
            unused_imports = self._check_unused_imports(content)
            for name, line_num in unused_imports:
                findings.append(
                    Finding(
                        id=f"CODE-{counter:04d}",
                        category=FindingCategory.CODE,
                        severity=Severity.LOW,
                        message=f"Unused import '{name}' detected",
                        file=rel_path,
                        line=line_num,
                        evidence={"identifier": name, "rule": "no-unused-imports"},
                        fixable=True,
                        status=FindingStatus.DETECTED,
                    )
                )
                counter += 1

            # 2. Missing Key in .map() JSX
            for match in MAP_JSX_PATTERN.finditer(content):
                tag = match.group(1)
                attrs = match.group("attrs") or ""
                if "key=" not in attrs and "key = " not in attrs:
                    line_num = content[:match.start()].count("\n") + 1
                    findings.append(
                        Finding(
                            id=f"CODE-{counter:04d}",
                            category=FindingCategory.CODE,
                            severity=Severity.HIGH,
                            message=f"Missing 'key' prop on mapped JSX element {tag}",
                            file=rel_path,
                            line=line_num,
                            evidence={"tag": tag, "rule": "react-jsx-key"},
                            fixable=True,
                            status=FindingStatus.DETECTED,
                        )
                    )
                    counter += 1

            # 3. Unsafe target="_blank" without rel="noopener noreferrer"
            for line_idx, line in enumerate(lines, start=1):
                blank_match = TARGET_BLANK_PATTERN.search(line)
                if blank_match:
                    attrs = blank_match.group(1).lower()
                    if "rel=" not in attrs or ("noopener" not in attrs and "noreferrer" not in attrs):
                        findings.append(
                            Finding(
                                id=f"CODE-{counter:04d}",
                                category=FindingCategory.CODE,
                                severity=Severity.MEDIUM,
                                message="Unsafe target='_blank' link without rel='noopener noreferrer'",
                                file=rel_path,
                                line=line_idx,
                                evidence={"snippet": line.strip(), "rule": "react-jsx-no-target-blank"},
                                fixable=True,
                                status=FindingStatus.DETECTED,
                            )
                        )
                        counter += 1

            # 4. Dangerous HTML usage
            for line_idx, line in enumerate(lines, start=1):
                if DANGEROUS_HTML_PATTERN.search(line):
                    findings.append(
                        Finding(
                            id=f"CODE-{counter:04d}",
                            category=FindingCategory.CODE,
                            severity=Severity.HIGH,
                            message="Use of dangerouslySetInnerHTML detected; risk of XSS vulnerability",
                            file=rel_path,
                            line=line_idx,
                            evidence={"snippet": line.strip(), "rule": "no-danger"},
                            fixable=False,
                            status=FindingStatus.DETECTED,
                        )
                    )
                    counter += 1

        # 5. Component Level Smells from Project Graph
        for comp_name, comp_node in graph.components.items():
            if comp_node.lines_of_code > 250:
                findings.append(
                    Finding(
                        id=f"CODE-{counter:04d}",
                        category=FindingCategory.CODE,
                        severity=Severity.MEDIUM,
                        message=f"Component '{comp_name}' is overly large ({comp_node.lines_of_code} LOC). Consider modular decomposition.",
                        file=comp_node.file_path,
                        component=comp_name,
                        evidence={"loc": comp_node.lines_of_code, "threshold": 250, "rule": "max-component-lines"},
                        fixable=False,
                        status=FindingStatus.DETECTED,
                    )
                )
                counter += 1

            if len(comp_node.hooks) > 5:
                findings.append(
                    Finding(
                        id=f"CODE-{counter:04d}",
                        category=FindingCategory.CODE,
                        severity=Severity.LOW,
                        message=f"Component '{comp_name}' uses {len(comp_node.hooks)} distinct hooks. Consider a custom hook or reducer.",
                        file=comp_node.file_path,
                        component=comp_name,
                        evidence={"hooks": comp_node.hooks, "count": len(comp_node.hooks), "rule": "excessive-hooks"},
                        fixable=False,
                        status=FindingStatus.DETECTED,
                    )
                )
                counter += 1

        return findings

    def _check_unused_imports(self, content: str) -> List[Tuple[str, int]]:
        """Identifies imported symbols that are never referenced elsewhere in the file."""
        unused: List[Tuple[str, int]] = []
        
        imported_identifiers: List[Tuple[str, int]] = []
        import_end_pos = 0

        for match in IMPORT_STATEMENT_PATTERN.finditer(content):
            import_end_pos = max(import_end_pos, match.end())
            line_num = content[:match.start()].count("\n") + 1
            default_prefix = match.group(1)
            star_imp = match.group(2)
            named_imps = match.group(3)
            default_imp = match.group(4)

            for item in [default_prefix, star_imp, default_imp]:
                if item and item not in {"React"}:
                    imported_identifiers.append((item, line_num))

            if named_imps:
                for item in named_imps.split(","):
                    clean = item.strip().split(" as ")[-1].strip()
                    if clean and clean.isidentifier() and clean not in {"React"}:
                        imported_identifiers.append((clean, line_num))

        # Check usages in body text after imports
        body_text = content[import_end_pos:]
        for ident, line_num in imported_identifiers:
            usage_pattern = re.compile(rf"\b{re.escape(ident)}\b")
            if not usage_pattern.search(body_text):
                unused.append((ident, line_num))

        return unused
