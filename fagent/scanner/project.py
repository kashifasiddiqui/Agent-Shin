from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional
from fagent.schemas.project import ProjectInfo, Framework, Language, PackageManager, StylingSystem
from fagent.schemas.graph import ProjectGraph
from fagent.scanner.framework import FrameworkDetector
from fagent.scanner.components import ComponentScanner
from fagent.scanner.routes import RouteScanner
from fagent.scanner.assets import AssetScanner


class ProjectScanner:
    """Master deterministic scanner that inspects a frontend project and builds the project graph."""

    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        self.component_scanner = ComponentScanner(self.root_path)
        self.route_scanner = RouteScanner(self.root_path)
        self.asset_scanner = AssetScanner(self.root_path)

    def scan(self) -> ProjectGraph:
        package_json_path = self.root_path / "package.json"
        package_json = {}
        if package_json_path.exists():
            try:
                package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
            except Exception:
                package_json = {}

        project_name = package_json.get("name", self.root_path.name)
        
        # Detect directories
        src_dir_path = self.root_path / "src" if (self.root_path / "src").exists() else self.root_path
        public_dir_path = self.root_path / "public" if (self.root_path / "public").exists() else None

        # Framework and tooling detection
        framework, framework_version, bundler = FrameworkDetector.detect_framework_and_bundler(package_json)
        package_manager = FrameworkDetector.detect_package_manager(self.root_path)
        language = FrameworkDetector.detect_language(self.root_path, src_dir_path)
        styling_systems = FrameworkDetector.detect_styling_systems(package_json, self.root_path)

        # Detect entry points
        entry_points = []
        for candidate in [
            "src/main.tsx", "src/main.jsx", "src/main.ts", "src/main.js",
            "src/index.tsx", "src/index.jsx", "src/index.ts", "src/index.js",
            "src/App.tsx", "src/App.jsx",
            "index.html"
        ]:
            if (self.root_path / candidate).exists():
                entry_points.append(candidate)

        # Discover all code files for stats and reference checks
        all_code_files: List[Path] = []
        for ext in ["*.js", "*.jsx", "*.ts", "*.tsx", "*.vue", "*.svelte", "*.css", "*.scss", "*.html"]:
            for f in self.root_path.rglob(ext):
                if not any(ignored in f.parts for ignored in ["node_modules", "dist", "build", ".fagent", ".git", ".next"]):
                    all_code_files.append(f)

        # Scan components
        components = self.component_scanner.scan_all(src_dir_path)

        # Scan routes
        routes = self.route_scanner.scan_routes(src_dir_path, components)

        # Scan assets
        asset_dirs = []
        if public_dir_path:
            asset_dirs.append(public_dir_path)
        if (src_dir_path / "assets").exists():
            asset_dirs.append(src_dir_path / "assets")
        elif (self.root_path / "assets").exists():
            asset_dirs.append(self.root_path / "assets")

        assets = self.asset_scanner.scan_assets(asset_dirs, all_code_files)

        project_info = ProjectInfo(
            name=project_name,
            root_path=self.root_path.as_posix(),
            framework=framework,
            framework_version=framework_version,
            bundler=bundler,
            language=language,
            package_manager=package_manager,
            src_dir=src_dir_path.relative_to(self.root_path).as_posix() if src_dir_path != self.root_path else ".",
            public_dir=public_dir_path.relative_to(self.root_path).as_posix() if public_dir_path else None,
            entry_points=entry_points,
            styling_systems=styling_systems,
            dependencies=package_json.get("dependencies", {}),
            dev_dependencies=package_json.get("devDependencies", {}),
            total_files=len(all_code_files),
        )

        return ProjectGraph(
            project=project_info,
            components=components,
            routes=routes,
            assets=assets,
            entry_routes=[r.path for r in routes],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
