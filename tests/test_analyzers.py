from pathlib import Path
from typer.testing import CliRunner
from fagent.cli import app
from fagent.scanner.project import ProjectScanner
from fagent.core.audit import AuditEngine
from fagent.schemas.finding import FindingCategory, Severity

runner = CliRunner()


def test_audit_engine_detection():
    sample_root = Path(__file__).parent.parent / "examples" / "sample-react-app"
    scanner = ProjectScanner(sample_root)
    graph = scanner.scan()

    engine = AuditEngine(sample_root)
    report = engine.run_audit(graph)

    assert report.total_findings >= 3
    assert report.overall_score < 100

    finding_messages = [f.message for f in report.findings]
    assert any("useEffect" in m for m in finding_messages)
    assert any("target='_blank'" in m for m in finding_messages)
    assert any("key" in m for m in finding_messages)

    # Check category scores
    assert "code" in report.category_scores
    assert report.category_scores["code"].score < 100
    assert report.category_scores["code"].high_count >= 1


def test_cli_audit_command():
    sample_root = Path(__file__).parent.parent / "examples" / "sample-react-app"
    result = runner.invoke(app, ["audit", str(sample_root)])
    assert result.exit_code == 0
    assert "Frontend Quality Audit" in result.stdout
    assert "Overall Quality Score" in result.stdout
    assert "Detected Findings" in result.stdout
    assert "CODE-" in result.stdout
