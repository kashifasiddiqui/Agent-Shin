from pathlib import Path
from fagent.analyzers.design import DesignExtractor, DesignAnalyzer
from fagent.scanner.project import ProjectScanner
from fagent.schemas.finding import FindingCategory, Severity


def test_design_extractor(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True)

    # Sample CSS with variables and tokens
    css_content = """
    :root {
        --primary-color: #3b82f6;
        --secondary-color: #64748b;
        --radius-card: 12px;
        --shadow-elevation: 0 4px 6px rgba(0,0,0,0.1);
        font-family: 'Inter', sans-serif;
    }
    """
    (src_dir / "styles.css").write_text(css_content, encoding="utf-8")

    # Sample JSX with Tailwind classes
    jsx_content = """
    export function Hero() {
        return (
            <div className="bg-blue-600 text-gray-900 rounded-xl shadow-md text-2xl">
                <span className="rounded-lg text-sm">Badge</span>
            </div>
        );
    }
    """
    (src_dir / "Hero.tsx").write_text(jsx_content, encoding="utf-8")

    extractor = DesignExtractor(tmp_path)
    system = extractor.extract(src_dir)

    assert "#3b82f6" in system.all_colors
    assert "bg-blue-600" in system.all_colors
    assert "text-gray-900" in system.all_colors
    assert "rounded-xl" in system.radii
    assert "12px" in system.radii
    assert "shadow-md" in system.shadows or "0 4px 6px rgba(0,0,0,0.1)" in system.shadows
    assert "text-2xl" in system.font_sizes
    assert any("Inter" in f for f in system.font_families)


def test_ai_style_ui_smell_detection(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True)

    # Intentionally trigger AI smell: multiple divergent gradients and glassmorphism
    component_with_smells = """
    export function AICard() {
        return (
            <div>
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 backdrop-blur-md rounded-sm" />
                <div className="bg-gradient-to-b from-cyan-400 to-blue-600 backdrop-blur-lg rounded-3xl" />
                <div className="bg-gradient-to-tr from-amber-400 to-red-500 backdrop-blur-sm rounded-full" />
                <div className="bg-gradient-to-l from-emerald-400 to-teal-500 rounded-none" />
            </div>
        );
    }
    """
    (src_dir / "AICard.tsx").write_text(component_with_smells, encoding="utf-8")

    scanner = ProjectScanner(tmp_path)
    graph = scanner.scan()

    analyzer = DesignAnalyzer()
    findings = analyzer.analyze(tmp_path, graph)

    smell_messages = [f.message for f in findings]
    assert any("Excessive gradient" in m for m in smell_messages)
    assert any("Overuse of frosted glass" in m for m in smell_messages)
    assert any("Inconsistent border radii" in m for m in smell_messages)

    # Check that confidence and evidence are present
    gradient_finding = next(f for f in findings if "gradient" in f.message.lower())
    assert "confidence" in gradient_finding.evidence
    assert "smell" in gradient_finding.evidence
