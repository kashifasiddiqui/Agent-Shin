from pathlib import Path
from fagent.core.memory import ProjectMemory
from fagent.core.orchestrator import HealingLoop
from fagent.schemas.finding import Finding, FindingCategory, Severity


def test_project_memory_lifecycle(tmp_path):
    mem = ProjectMemory(tmp_path)
    assert mem.get_decisions() == []

    entry = mem.record_decision(
        decision="Card components use 12px radius",
        file_path="src/components/Card.tsx",
        finding_id="DESIGN-0001",
        reason="Approved design specification",
    )
    assert entry["id"] == "DEC-0001"
    assert len(mem.get_decisions()) == 1

    finding = Finding(
        id="DESIGN-0001",
        category=FindingCategory.DESIGN,
        severity=Severity.MEDIUM,
        message="Inconsistent border radius",
        file="src/components/Card.tsx",
    )
    assert mem.is_known_exception(finding) is True

    unrelated_finding = Finding(
        id="CODE-0099",
        category=FindingCategory.CODE,
        severity=Severity.HIGH,
        message="Different issue",
        file="src/Other.tsx",
    )
    assert mem.is_known_exception(unrelated_finding) is False


def test_autonomous_healing_loop(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True)

    # File with fixable unused import
    code_file = src_dir / "Button.tsx"
    code_file.write_text("import React, { useState, useEffect } from 'react';\nexport const Button = () => <button>Click</button>;\n", encoding="utf-8")

    loop = HealingLoop(tmp_path, max_iterations=3, allow_review=False)
    result = loop.run()

    assert result["iterations_run"] >= 1
    assert result["total_applied_fixes"] >= 1
    assert result["final_score"] >= 95

    # File was autonomously healed
    content = code_file.read_text(encoding="utf-8")
    assert "useEffect" not in content
