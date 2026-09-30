import json
from pathlib import Path
from fagent.scanner.project import ProjectScanner
from fagent.scanner.framework import FrameworkDetector
from fagent.schemas.project import Framework, Language, PackageManager, StylingSystem


def test_framework_detector(tmp_path):
    pkg_json = {
        "name": "my-test-app",
        "dependencies": {
            "react": "^18.2.0",
            "tailwindcss": "^3.0.0"
        },
        "devDependencies": {
            "vite": "^4.0.0"
        }
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg_json), encoding="utf-8")
    (tmp_path / "yarn.lock").write_text("", encoding="utf-8")
    (tmp_path / "tsconfig.json").write_text("{}", encoding="utf-8")

    framework, version, bundler = FrameworkDetector.detect_framework_and_bundler(pkg_json)
    assert framework == Framework.REACT
    assert version == "^18.2.0"
    assert bundler == "Vite"

    pkg_manager = FrameworkDetector.detect_package_manager(tmp_path)
    assert pkg_manager == PackageManager.YARN

    lang = FrameworkDetector.detect_language(tmp_path)
    assert lang == Language.TYPESCRIPT

    styles = FrameworkDetector.detect_styling_systems(pkg_json, tmp_path)
    assert StylingSystem.TAILWIND in styles


def test_sample_react_app_scan():
    sample_root = Path(__file__).parent.parent / "examples" / "sample-react-app"
    scanner = ProjectScanner(sample_root)
    graph = scanner.scan()

    assert graph.project.name == "sample-react-app"
    assert graph.project.framework == Framework.REACT
    assert graph.project.bundler == "Vite"
    assert graph.project.language == Language.TYPESCRIPT
    assert graph.project.package_manager == PackageManager.NPM
    assert StylingSystem.TAILWIND in graph.project.styling_systems

    # Components
    assert "Button" in graph.components
    assert "Header" in graph.components
    assert "ProjectCard" in graph.components
    assert "HomePage" in graph.components
    assert "ProjectsPage" in graph.components

    # Component relationships
    assert "Header" in graph.components["Button"].used_in
    assert "HomePage" in graph.components["Header"].used_in
    assert "useState" in graph.components["Header"].hooks

    # Routes
    route_paths = [r.path for r in graph.routes]
    assert "/" in route_paths
    assert "/projects" in route_paths

    # Assets
    asset_paths = [a.file_path for a in graph.assets]
    assert any("logo.svg" in p for p in asset_paths)
    assert any("favicon.svg" in p for p in asset_paths)
