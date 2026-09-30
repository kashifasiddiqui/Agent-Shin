import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from fagent.schemas.project import Framework, Language, PackageManager, StylingSystem


class FrameworkDetector:
    """Detects framework, language, package manager, and styling tools from project files."""

    @staticmethod
    def detect_package_manager(root_path: Path) -> PackageManager:
        if (root_path / "bun.lockb").exists() or (root_path / "bun.lock").exists():
            return PackageManager.BUN
        if (root_path / "pnpm-lock.yaml").exists():
            return PackageManager.PNPM
        if (root_path / "yarn.lock").exists():
            return PackageManager.YARN
        if (root_path / "package-lock.json").exists():
            return PackageManager.NPM
        return PackageManager.NPM

    @staticmethod
    def detect_language(root_path: Path, src_dir: Optional[Path] = None) -> Language:
        if (root_path / "tsconfig.json").exists():
            return Language.TYPESCRIPT
        
        target_dir = src_dir if src_dir and src_dir.exists() else root_path
        ts_files = list(target_dir.glob("**/*.ts")) + list(target_dir.glob("**/*.tsx"))
        # filter out node_modules
        ts_files = [f for f in ts_files if "node_modules" not in f.parts and ".fagent" not in f.parts]
        if ts_files:
            return Language.TYPESCRIPT
        return Language.JAVASCRIPT

    @staticmethod
    def detect_framework_and_bundler(package_json: Dict) -> Tuple[Framework, Optional[str], Optional[str]]:
        deps = package_json.get("dependencies", {})
        dev_deps = package_json.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}

        bundler = None
        if "vite" in all_deps:
            bundler = "Vite"
        elif "webpack" in all_deps:
            bundler = "Webpack"
        elif "turbo" in all_deps:
            bundler = "Turborepo/Turbopack"

        if "next" in all_deps:
            version = all_deps.get("next")
            return Framework.NEXTJS, version, bundler or "Next.js Bundler"
        elif "react" in all_deps:
            version = all_deps.get("react")
            return Framework.REACT, version, bundler or "React Scripts / Custom"
        elif "vue" in all_deps:
            version = all_deps.get("vue")
            return Framework.VUE, version, bundler
        elif "nuxt" in all_deps:
            version = all_deps.get("nuxt")
            return Framework.NUXT, version, bundler
        elif "svelte" in all_deps or "@sveltejs/kit" in all_deps:
            version = all_deps.get("svelte") or all_deps.get("@sveltejs/kit")
            return Framework.SVELTE, version, bundler
        elif "@angular/core" in all_deps:
            version = all_deps.get("@angular/core")
            return Framework.ANGULAR, version, bundler

        return Framework.UNKNOWN, None, bundler

    @staticmethod
    def detect_styling_systems(package_json: Dict, root_path: Path) -> List[StylingSystem]:
        systems = []
        deps = package_json.get("dependencies", {})
        dev_deps = package_json.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}

        if (
            "tailwindcss" in all_deps 
            or (root_path / "tailwind.config.js").exists() 
            or (root_path / "tailwind.config.ts").exists()
        ):
            systems.append(StylingSystem.TAILWIND)

        if "styled-components" in all_deps:
            systems.append(StylingSystem.STYLED_COMPONENTS)

        if "@emotion/react" in all_deps or "@emotion/styled" in all_deps:
            systems.append(StylingSystem.EMOTION)

        if "sass" in all_deps or "node-sass" in all_deps:
            systems.append(StylingSystem.SCSS)

        # Check for CSS modules
        src_path = root_path / "src" if (root_path / "src").exists() else root_path
        css_modules = list(src_path.glob("**/*.module.css")) + list(src_path.glob("**/*.module.scss"))
        if css_modules:
            systems.append(StylingSystem.CSS_MODULES)

        if not systems:
            systems.append(StylingSystem.VANILLA_CSS)

        return systems
