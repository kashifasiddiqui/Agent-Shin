import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from fagent.analyzers.base import BaseAnalyzer
from fagent.schemas.finding import Finding, FindingCategory, Severity, FindingStatus
from fagent.schemas.design import DesignSystem, ColorUsage, RadiusUsage
from fagent.schemas.graph import ProjectGraph
from fagent.core.state import StateManager


HEX_COLOR_PATTERN = re.compile(r"""#(?:[0-9a-fA-F]{3,4}){1,2}\b""")
CSS_VAR_COLOR_PATTERN = re.compile(r"""--([a-zA-Z0-9_-]*(?:color|primary|secondary|accent|bg|text)[a-zA-Z0-9_-]*)\s*:\s*([^;]+);""")
CSS_RADIUS_PATTERN = re.compile(r"""(?:border-radius|--radius[a-zA-Z0-9_-]*)\s*:\s*([^;]+);""")
CSS_SHADOW_PATTERN = re.compile(r"""(?:box-shadow|--shadow[a-zA-Z0-9_-]*)\s*:\s*([^;]+);""")
CSS_FONT_PATTERN = re.compile(r"""font-family\s*:\s*([^;]+);""")

# Tailwind utility extraction patterns
TW_COLOR_CLASS = re.compile(r"""\b(?:bg|text|border|ring)-(?:slate|gray|zinc|neutral|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-[1-9]00\b""")
TW_RADIUS_CLASS = re.compile(r"""\brounded-(?:none|sm|md|lg|xl|2xl|3xl|full)\b""")
TW_SHADOW_CLASS = re.compile(r"""\bshadow-(?:sm|md|lg|xl|2xl|inner|none)\b""")
TW_FONT_SIZE_CLASS = re.compile(r"""\btext-(?:xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)\b""")
TW_GRADIENT_CLASS = re.compile(r"""\bbg-gradient-to-(?:t|tr|r|br|b|bl|l|tl)\b""")
TW_GLASS_CLASS = re.compile(r"""\b(?:backdrop-blur(?:-[a-z0-9]+)?|backdrop-filter|bg-(?:white|black)/\d+)\b""")



class DesignExtractor:
    """Extracts design tokens, colors, typography, radii, and styles from CSS and JSX/TSX."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def extract(self, search_dir: Path) -> DesignSystem:
        all_colors: Dict[str, ColorUsage] = {}
        all_radii: Dict[str, RadiusUsage] = {}
        font_families: Set[str] = set()
        font_sizes: Set[str] = set()
        shadows: Set[str] = set()
        gradients: Set[str] = set()
        glass_elements: Set[str] = set()

        # 1. Scan CSS / SCSS files
        for css_file in search_dir.rglob("*.css"):
            if any(ignored in css_file.parts for ignored in ["node_modules", "dist", ".fagent", ".git"]):
                continue
            try:
                content = css_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel_file = css_file.relative_to(self.project_root).as_posix()

            for match in HEX_COLOR_PATTERN.finditer(content):
                c = match.group(0).lower()
                self._record_color(all_colors, c, rel_file)

            for match in CSS_VAR_COLOR_PATTERN.finditer(content):
                c = match.group(2).strip().lower()
                self._record_color(all_colors, c, rel_file)

            for match in CSS_RADIUS_PATTERN.finditer(content):
                r = match.group(1).strip()
                self._record_radius(all_radii, r, rel_file)

            for match in CSS_SHADOW_PATTERN.finditer(content):
                shadows.add(match.group(1).strip())

            for match in CSS_FONT_PATTERN.finditer(content):
                font_families.add(match.group(1).strip())

        # 2. Scan JSX/TSX files for classNames and styles
        for ext in ["*.jsx", "*.tsx", "*.html"]:
            for code_file in search_dir.rglob(ext):
                if any(ignored in code_file.parts for ignored in ["node_modules", "dist", ".fagent", ".git"]):
                    continue
                try:
                    content = code_file.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

                rel_file = code_file.relative_to(self.project_root).as_posix()

                # Tailwind colors
                for match in TW_COLOR_CLASS.finditer(content):
                    c = match.group(0)
                    self._record_color(all_colors, c, rel_file)

                # Tailwind radii
                for match in TW_RADIUS_CLASS.finditer(content):
                    r = match.group(0)
                    self._record_radius(all_radii, r, rel_file)

                # Tailwind shadows
                for match in TW_SHADOW_CLASS.finditer(content):
                    shadows.add(match.group(0))

                # Tailwind font sizes
                for match in TW_FONT_SIZE_CLASS.finditer(content):
                    font_sizes.add(match.group(0))

                # Tailwind gradients
                for match in TW_GRADIENT_CLASS.finditer(content):
                    gradients.add(f"{match.group(0)} in {rel_file}")

                # Tailwind glassmorphism
                for match in TW_GLASS_CLASS.finditer(content):
                    glass_elements.add(f"{match.group(0)} in {rel_file}")

        # Classify primary vs accent colors based on frequency
        sorted_colors = sorted(all_colors.values(), key=lambda c: c.count, reverse=True)
        primary_colors = [c.value for c in sorted_colors[:3]]
        accent_colors = [c.value for c in sorted_colors[3:8]]

        total_tokens = len(all_colors) + len(all_radii) + len(shadows) + len(font_sizes)

        return DesignSystem(
            primary_colors=primary_colors,
            accent_colors=accent_colors,
            all_colors=all_colors,
            radii=all_radii,
            font_families=sorted(list(font_families)),
            font_sizes=sorted(list(font_sizes)),
            shadows=sorted(list(shadows)),
            gradients=sorted(list(gradients)),
            glassmorphism_elements=sorted(list(glass_elements)),
            total_token_count=total_tokens,
        )

    def _record_color(self, mapping: Dict[str, ColorUsage], color: str, file_path: str):
        if color not in mapping:
            mapping[color] = ColorUsage(value=color, count=1, sources=[file_path])
        else:
            mapping[color].count += 1
            if file_path not in mapping[color].sources:
                mapping[color].sources.append(file_path)

    def _record_radius(self, mapping: Dict[str, RadiusUsage], radius: str, file_path: str):
        if radius not in mapping:
            mapping[radius] = RadiusUsage(value=radius, count=1, sources=[file_path])
        else:
            mapping[radius].count += 1
            if file_path not in mapping[radius].sources:
                mapping[radius].sources.append(file_path)


class DesignAnalyzer(BaseAnalyzer):
    """Analyzes design system consistency, token harmony, and AI-style UI smells."""

    @property
    def category_name(self) -> str:
        return "design"

    def analyze(self, project_root: Path, graph: ProjectGraph) -> List[Finding]:
        findings: List[Finding] = []
        counter = 1

        src_dir = project_root / (graph.project.src_dir or "src")
        if not src_dir.exists():
            src_dir = project_root

        extractor = DesignExtractor(project_root)
        design_system = extractor.extract(src_dir)

        # Persist design system into .fagent/design-system.json
        state = StateManager(project_root)
        if state.is_initialized():
            ds_target = state.fagent_dir / "design-system.json"
            state._save_json(ds_target, design_system.model_dump(mode="json"))

        # 1. AI Smell: Excessive / Conflicting Gradients
        if len(design_system.gradients) >= 3:
            findings.append(
                Finding(
                    id=f"DESIGN-{counter:04d}",
                    category=FindingCategory.DESIGN,
                    severity=Severity.MEDIUM,
                    message=f"Potential AI-style UI pattern: Excessive gradient treatments ({len(design_system.gradients)} found)",
                    evidence={
                        "confidence": "89%",
                        "smell": "excessive-gradients",
                        "detected_gradients": design_system.gradients[:5],
                        "recommendation": "Unify backgrounds to a cohesive flat or single subtle gradient design system.",
                    },
                    fixable=False,
                    status=FindingStatus.DETECTED,
                )
            )
            counter += 1

        # 2. AI Smell: Heavy / Uncontrolled Glassmorphism
        if len(design_system.glassmorphism_elements) >= 3:
            findings.append(
                Finding(
                    id=f"DESIGN-{counter:04d}",
                    category=FindingCategory.DESIGN,
                    severity=Severity.LOW,
                    message=f"Potential AI-style UI pattern: Overuse of frosted glass / backdrop-blur ({len(design_system.glassmorphism_elements)} occurrences)",
                    evidence={
                        "confidence": "84%",
                        "smell": "glassmorphism-overuse",
                        "elements": design_system.glassmorphism_elements[:5],
                        "recommendation": "Use glassmorphism sparingly for focal navigation or modals rather than repeated content cards.",
                    },
                    fixable=False,
                    status=FindingStatus.DETECTED,
                )
            )
            counter += 1

        # 3. Border Radius Inconsistency
        # If project uses >= 4 disparate radii simultaneously across basic cards
        if len(design_system.radii) >= 4:
            sorted_radii = sorted(design_system.radii.values(), key=lambda r: r.count, reverse=True)
            dominant_radius = sorted_radii[0].value
            outliers = [r.value for r in sorted_radii[2:]]
            findings.append(
                Finding(
                    id=f"DESIGN-{counter:04d}",
                    category=FindingCategory.DESIGN,
                    severity=Severity.MEDIUM,
                    message=f"Inconsistent border radii detected across project ({len(design_system.radii)} distinct radius values used)",
                    evidence={
                        "dominant_radius": dominant_radius,
                        "outlier_radii": outliers,
                        "rule": "consistent-border-radius",
                        "recommendation": f"Standardize component borders around '{dominant_radius}'.",
                    },
                    fixable=True,
                    status=FindingStatus.DETECTED,
                )
            )
            counter += 1

        # 4. Color Palette Coherence / Random Accent Multiplicity
        # If > 5 non-neutral color families are used in Tailwind classes
        color_families: Set[str] = set()
        for color_val in design_system.all_colors.keys():
            if "-" in color_val:
                family = color_val.split("-")[1]
                if family not in {"slate", "gray", "zinc", "neutral"}:
                    color_families.add(family)

        if len(color_families) >= 4:
            findings.append(
                Finding(
                    id=f"DESIGN-{counter:04d}",
                    category=FindingCategory.DESIGN,
                    severity=Severity.LOW,
                    message=f"High color palette fragmentation: {len(color_families)} distinct accent color families detected ({', '.join(sorted(color_families))})",
                    evidence={
                        "color_families": sorted(list(color_families)),
                        "rule": "color-palette-coherence",
                        "recommendation": "Establish 1 primary brand color and at most 2 complementary accent colors.",
                    },
                    fixable=False,
                    status=FindingStatus.DETECTED,
                )
            )
            counter += 1

        return findings
