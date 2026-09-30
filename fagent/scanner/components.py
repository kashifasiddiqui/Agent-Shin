import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from fagent.schemas.graph import ComponentNode


IMPORT_PATTERN = re.compile(
    r"""import\s+(?:(?:\*\s+as\s+(\w+)|(\w+)|(?:\{([^}]+)\}))\s+from\s+)?['"]([^'"]+)['"]""",
    re.MULTILINE
)
HOOK_PATTERN = re.compile(r"""\b(use[A-Z]\w*)\b""")
PROPS_PATTERN = re.compile(
    r"""(?:function\s+\w+\s*\(\s*\{([^}]+)\}|const\s+\w+\s*=\s*\(\s*\{([^}]+)\})"""
)
COMPONENT_DEF_PATTERN = re.compile(
    r"""(?:export\s+(?:default\s+)?(?:function|class|const)\s+([A-Z]\w*)|(?:function|class|const)\s+([A-Z]\w*)\s*(?:=|:|\())"""
)


class ComponentScanner:
    """Discovers and parses frontend components, their dependencies, and usage."""

    COMPONENT_EXTENSIONS = {".jsx", ".tsx", ".vue", ".svelte"}
    IGNORE_DIRS = {"node_modules", "dist", "build", ".next", ".git", ".fagent", "coverage"}

    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()

    def discover_component_files(self, search_dir: Path) -> List[Path]:
        files: List[Path] = []
        if not search_dir.exists():
            return files

        for path in search_dir.rglob("*"):
            if path.is_file() and path.suffix in self.COMPONENT_EXTENSIONS:
                if not any(ignored in path.parts for ignored in self.IGNORE_DIRS):
                    # Filter out test files
                    if not (path.name.endswith(".test.tsx") or path.name.endswith(".spec.tsx") or
                            path.name.endswith(".test.jsx") or path.name.endswith(".spec.jsx")):
                        files.append(path)
        return files

    def parse_component(self, file_path: Path) -> Optional[Tuple[ComponentNode, List[str]]]:
        """Parses a component file and returns the ComponentNode along with raw import targets."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

        # Exclude entry point scripts that only mount to DOM without defining a component
        if file_path.name in {"main.tsx", "main.jsx", "index.tsx", "index.jsx"}:
            if "ReactDOM" in content or "createRoot" in content:
                # If it doesn't define its own component, it's just an entry script
                comp_match = COMPONENT_DEF_PATTERN.search(content)
                if not comp_match:
                    return None

        rel_path = file_path.relative_to(self.root_path).as_posix()
        name = file_path.stem
        if name.lower() == "index":
            name = file_path.parent.name

        lines = content.splitlines()
        loc = len([line for line in lines if line.strip() and not line.strip().startswith("//")])

        # Detect page or layout heuristics
        parts_lower = [p.lower() for p in file_path.parts]
        is_page = (
            "pages" in parts_lower
            or "routes" in parts_lower
            or "views" in parts_lower
            or name.lower().endswith("page")
            or name.lower().endswith("view")
        )
        is_layout = "layout" in parts_lower or name.lower().endswith("layout")

        # Extract imported component names / modules
        imported_components: List[str] = []
        raw_import_paths: List[str] = []

        for match in IMPORT_PATTERN.finditer(content):
            default_import = match.group(2)
            named_imports = match.group(3)
            import_path = match.group(4)

            raw_import_paths.append(import_path)

            if default_import and default_import[0].isupper():
                imported_components.append(default_import)
            if named_imports:
                for item in named_imports.split(","):
                    item_name = item.strip().split(" as ")[0].strip()
                    if item_name and item_name[0].isupper():
                        imported_components.append(item_name)

        # Extract hooks
        hooks_found: Set[str] = set()
        for match in HOOK_PATTERN.finditer(content):
            hooks_found.add(match.group(1))

        # Extract props heuristically
        props: List[str] = []
        for match in PROPS_PATTERN.finditer(content):
            props_group = match.group(1) or match.group(2)
            if props_group:
                for p in props_group.split(","):
                    p_clean = p.split(":")[0].split("=")[0].strip()
                    if p_clean and p_clean.isidentifier():
                        props.append(p_clean)

        node = ComponentNode(
            name=name,
            file_path=rel_path,
            is_page=is_page,
            is_layout=is_layout,
            imported_components=sorted(list(set(imported_components))),
            used_in=[],
            props=sorted(list(set(props))),
            hooks=sorted(list(hooks_found)),
            lines_of_code=loc,
        )

        return node, raw_import_paths

    def scan_all(self, search_dir: Path) -> Dict[str, ComponentNode]:
        component_files = self.discover_component_files(search_dir)
        nodes: Dict[str, ComponentNode] = {}

        for file_path in component_files:
            result = self.parse_component(file_path)
            if result:
                node, _ = result
                nodes[node.name] = node

        # Calculate used_in relationships
        for caller_name, caller_node in nodes.items():
            for imported in caller_node.imported_components:
                if imported in nodes and caller_name not in nodes[imported].used_in:
                    nodes[imported].used_in.append(caller_name)

        return nodes
