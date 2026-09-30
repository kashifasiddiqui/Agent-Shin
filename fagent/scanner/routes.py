import re
from pathlib import Path
from typing import Dict, List, Optional
from fagent.schemas.graph import RouteNode, ComponentNode

# React Router JSX matchers
JSX_PATH_THEN_ELEM = re.compile(r"""<Route\s+[^>]*?path=['"]([^'"]+)['"][^>]*?element=\{<(\w+)""")
JSX_ELEM_THEN_PATH = re.compile(r"""<Route\s+[^>]*?element=\{<(\w+)[^>]*?>\}[^>]*?path=['"]([^'"]+)['"]""")
JSX_PATH_THEN_COMP = re.compile(r"""<Route\s+[^>]*?path=['"]([^'"]+)['"][^>]*?Component=\{?(\w+)\}?""")
JSX_PATH_ONLY = re.compile(r"""<Route\s+[^>]*?path=['"]([^'"]+)['"]""")

ROUTE_OBJ_PATTERN = re.compile(
    r"""path:\s*['"]([^'"]+)['"]\s*,\s*(?:element:\s*<(\w+)[^>]*>|Component:\s*(\w+))"""
)


class RouteScanner:
    """Discovers application routes from React Router, Next.js, and file-based structures."""

    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()

    def scan_routes(
        self, search_dir: Path, components: Dict[str, ComponentNode], is_nextjs: bool = False
    ) -> List[RouteNode]:
        routes: List[RouteNode] = []
        seen_paths = set()

        # 1. Scan React Router (JSX and object routes) across source files
        for ext in ["*.jsx", "*.tsx", "*.js", "*.ts"]:
            for code_file in search_dir.rglob(ext):
                if any(ignored in code_file.parts for ignored in ["node_modules", "dist", ".fagent", ".git", ".next"]):
                    continue
                try:
                    content = code_file.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

                if "<Route" in content:
                    # Match path then element
                    for match in JSX_PATH_THEN_ELEM.finditer(content):
                        path, comp_name = match.group(1), match.group(2)
                        if path not in seen_paths:
                            seen_paths.add(path)
                            comp_file = components[comp_name].file_path if comp_name in components else None
                            routes.append(
                                RouteNode(
                                    path=path,
                                    component_name=comp_name,
                                    file_path=comp_file or code_file.relative_to(self.root_path).as_posix()
                                )
                            )

                    # Match element then path
                    for match in JSX_ELEM_THEN_PATH.finditer(content):
                        comp_name, path = match.group(1), match.group(2)
                        if path not in seen_paths:
                            seen_paths.add(path)
                            comp_file = components[comp_name].file_path if comp_name in components else None
                            routes.append(
                                RouteNode(
                                    path=path,
                                    component_name=comp_name,
                                    file_path=comp_file or code_file.relative_to(self.root_path).as_posix()
                                )
                            )

                    # Match path then Component attribute
                    for match in JSX_PATH_THEN_COMP.finditer(content):
                        path, comp_name = match.group(1), match.group(2)
                        if path not in seen_paths:
                            seen_paths.add(path)
                            comp_file = components[comp_name].file_path if comp_name in components else None
                            routes.append(
                                RouteNode(
                                    path=path,
                                    component_name=comp_name,
                                    file_path=comp_file or code_file.relative_to(self.root_path).as_posix()
                                )
                            )

                    # Match fallback path only
                    for match in JSX_PATH_ONLY.finditer(content):
                        path = match.group(1)
                        if path not in seen_paths:
                            seen_paths.add(path)
                            routes.append(
                                RouteNode(
                                    path=path,
                                    component_name=None,
                                    file_path=code_file.relative_to(self.root_path).as_posix()
                                )
                            )

                if "path:" in content:
                    for match in ROUTE_OBJ_PATTERN.finditer(content):
                        path = match.group(1)
                        comp_name = match.group(2) or match.group(3)
                        if path not in seen_paths:
                            seen_paths.add(path)
                            comp_file = components.get(comp_name).file_path if comp_name and comp_name in components else None
                            routes.append(
                                RouteNode(
                                    path=path,
                                    component_name=comp_name,
                                    file_path=comp_file or code_file.relative_to(self.root_path).as_posix()
                                )
                            )

        # 2. If Next.js or file-based routing or no routes found yet, scan app/ and pages/
        app_dir = search_dir / "app"
        if app_dir.exists():
            for page_file in app_dir.rglob("page.*"):
                rel_to_app = page_file.parent.relative_to(app_dir).as_posix()
                route_path = "/" if rel_to_app == "." else f"/{rel_to_app}"
                route_path = re.sub(r"\[(\w+)\]", r":\1", route_path)
                if route_path not in seen_paths:
                    seen_paths.add(route_path)
                    routes.append(
                        RouteNode(
                            path=route_path,
                            file_path=page_file.relative_to(self.root_path).as_posix(),
                            component_name=page_file.parent.name if page_file.parent != app_dir else "RootPage"
                        )
                    )

        # Only check pages/ for file routes if Next.js is enabled or no router was detected
        if is_nextjs or not routes:
            pages_dir = search_dir / "pages"
            if pages_dir.exists():
                for page_file in pages_dir.rglob("*"):
                    if page_file.is_file() and page_file.suffix in {".jsx", ".tsx", ".js", ".ts"}:
                        if page_file.stem.startswith("_") or page_file.name.endswith(".test.tsx"):
                            continue
                        rel_to_pages = page_file.relative_to(pages_dir).with_suffix("").as_posix()
                        route_path = "/" if rel_to_pages == "index" else f"/{rel_to_pages}"
                        route_path = route_path.replace("/index", "")
                        route_path = re.sub(r"\[(\w+)\]", r":\1", route_path)
                        if route_path not in seen_paths:
                            seen_paths.add(route_path)
                            routes.append(
                                RouteNode(
                                    path=route_path,
                                    file_path=page_file.relative_to(self.root_path).as_posix(),
                                    component_name=page_file.stem
                                )
                            )

        # 3. Default fallback if no routes found
        if not routes:
            routes.append(
                RouteNode(
                    path="/",
                    component_name="App" if "App" in components else None,
                    file_path=components.get("App").file_path if "App" in components else None
                )
            )

        return sorted(routes, key=lambda r: r.path)
