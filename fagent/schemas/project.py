from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Framework(str, Enum):
    REACT = "React"
    NEXTJS = "Next.js"
    VUE = "Vue"
    NUXT = "Nuxt"
    SVELTE = "Svelte"
    ANGULAR = "Angular"
    UNKNOWN = "Unknown"


class Language(str, Enum):
    TYPESCRIPT = "TypeScript"
    JAVASCRIPT = "JavaScript"


class PackageManager(str, Enum):
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    BUN = "bun"
    UNKNOWN = "unknown"


class StylingSystem(str, Enum):
    TAILWIND = "Tailwind CSS"
    CSS_MODULES = "CSS Modules"
    STYLED_COMPONENTS = "styled-components"
    EMOTION = "@emotion"
    SCSS = "SCSS/Sass"
    VANILLA_CSS = "Vanilla CSS"
    UNKNOWN = "Unknown"


class ProjectInfo(BaseModel):
    name: str = Field(description="Name of the project")
    root_path: str = Field(description="Absolute path to the project root")
    framework: Framework = Field(default=Framework.UNKNOWN, description="Frontend framework detected")
    framework_version: Optional[str] = Field(default=None, description="Version of the framework")
    bundler: Optional[str] = Field(default=None, description="Build tool / bundler (e.g. Vite, Webpack, Turbopack)")
    language: Language = Field(default=Language.JAVASCRIPT, description="Primary language")
    package_manager: PackageManager = Field(default=PackageManager.UNKNOWN, description="Package manager used")
    src_dir: Optional[str] = Field(default=None, description="Relative path to source directory")
    public_dir: Optional[str] = Field(default=None, description="Relative path to public directory")
    entry_points: List[str] = Field(default_factory=list, description="Application entry points")
    styling_systems: List[StylingSystem] = Field(default_factory=list, description="Detected styling systems")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Runtime dependencies")
    dev_dependencies: Dict[str, str] = Field(default_factory=dict, description="Development dependencies")
    total_files: int = Field(default=0, description="Total source files in project")
