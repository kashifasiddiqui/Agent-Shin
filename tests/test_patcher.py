from pathlib import Path
from fagent.patcher.fixers import PatchFixer
from fagent.patcher.engine import PatchEngine
from fagent.schemas.finding import Finding, FindingCategory, Severity
from fagent.schemas.patch import PatchRiskLevel, PatchAction


def test_fix_unused_import():
    content = "import React, { useState, useEffect } from 'react';\n\nexport const Foo = () => null;\n"
    finding = Finding(
        id="CODE-0001",
        category=FindingCategory.CODE,
        severity=Severity.LOW,
        message="Unused import 'useEffect'",
        file="Foo.tsx",
        evidence={"identifier": "useEffect", "rule": "no-unused-imports"},
        fixable=True,
    )
    patched = PatchFixer._fix_unused_import(content, "useEffect")
    assert "useEffect" not in patched
    assert "useState" in patched
    assert "React" in patched


def test_fix_target_blank():
    content = '<a href="https://example.com" target="_blank">Link</a>'
    finding = Finding(
        id="CODE-0002",
        category=FindingCategory.CODE,
        severity=Severity.MEDIUM,
        message="Unsafe target blank",
        file="Foo.tsx",
        evidence={"rule": "react-jsx-no-target-blank"},
        fixable=True,
    )
    patched = PatchFixer._fix_target_blank(content)
    assert 'rel="noopener noreferrer"' in patched


def test_fix_missing_key():
    content = "<ul>{items.map((item) => ( <li>{item.name}</li> ))}</ul>"
    finding = Finding(
        id="CODE-0003",
        category=FindingCategory.CODE,
        severity=Severity.HIGH,
        message="Missing key",
        file="Foo.tsx",
        evidence={"rule": "react-jsx-key"},
        fixable=True,
    )
    patched = PatchFixer._fix_missing_key(content, "<li>")
    assert "key={" in patched


def test_patch_engine_lifecycle(tmp_path):
    test_file = tmp_path / "Card.tsx"
    test_file.write_text("import React, { useState, useEffect } from 'react';\nexport const Card = () => <a target=\"_blank\">Link</a>;\n", encoding="utf-8")

    findings = [
        Finding(
            id="CODE-0001",
            category=FindingCategory.CODE,
            severity=Severity.LOW,
            message="Unused import 'useEffect'",
            file="Card.tsx",
            evidence={"identifier": "useEffect", "rule": "no-unused-imports"},
            fixable=True,
        ),
        Finding(
            id="CODE-0002",
            category=FindingCategory.CODE,
            severity=Severity.MEDIUM,
            message="Unsafe target blank",
            file="Card.tsx",
            evidence={"rule": "react-jsx-no-target-blank"},
            fixable=True,
        ),
    ]

    engine = PatchEngine(tmp_path)
    plan = engine.create_plan(findings)

    assert plan.total_patches == 2
    assert plan.safe_count == 2

    # Test applying safe patches
    success, applied, msgs = engine.apply_plan_with_safety(plan, allowed_risks=[PatchRiskLevel.SAFE])
    assert success is True
    assert len(applied) == 2

    content_after = test_file.read_text(encoding="utf-8")
    assert "useEffect" not in content_after
    assert 'rel="noopener noreferrer"' in content_after


def test_fix_border_radius_harmonization():
    content = '<div className="rounded-3xl p-4 bg-white">Card</div>'
    patched = PatchFixer._fix_border_radius(content, "rounded-3xl", "rounded-lg")
    assert "rounded-lg" in patched
    assert "rounded-3xl" not in patched


def test_fix_missing_alt():
    content = '<img src="/hero.png" className="w-full" />'
    patched = PatchFixer._fix_missing_alt(content)
    assert 'alt=""' in patched
    assert 'src="/hero.png"' in patched

