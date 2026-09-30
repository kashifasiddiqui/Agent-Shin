from pathlib import Path
from typer.testing import CliRunner
from fagent.cli import app
from fagent.scanner.project import ProjectScanner
from fagent.core.audit import AuditEngine
from fagent.schemas.finding import FindingCategory, Severity

runner = CliRunner()


def test_audit_engine_detection(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True)

    code_file = src_dir / "Component.tsx"
    code_file.write_text(
        "import React, { useState, useEffect } from 'react';\n"
        "export const Component = ({ items }: any) => (\n"
        "  <div>\n"
        "    <a href=\"https://github.com\" target=\"_blank\">Repo</a>\n"
        "    {items.map((i: any) => <span>{i}</span>)}\n"
        "  </div>\n"
        ");\n",
        encoding="utf-8"
    )

    scanner = ProjectScanner(tmp_path)
    graph = scanner.scan()

    engine = AuditEngine(tmp_path)
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


def test_cli_audit_command(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True)

    code_file = src_dir / "TestCard.tsx"
    code_file.write_text(
        "import React, { useEffect } from 'react';\n"
        "export const TestCard = () => <a target=\"_blank\">Link</a>;\n",
        encoding="utf-8"
    )

    result = runner.invoke(app, ["audit", str(tmp_path)])
    assert result.exit_code == 0
    assert "Frontend Quality Audit" in result.stdout
    assert "Overall Quality Score" in result.stdout
    assert "Detected Findings" in result.stdout
    assert "CODE-" in result.stdout
