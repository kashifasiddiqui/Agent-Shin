from pathlib import Path
from fagent.reasoning.provider import LLMProvider, OpenRouterProvider
from fagent.reasoning.planner import LLMReasoningEngine
from fagent.schemas.finding import Finding, FindingCategory, Severity
from fagent.schemas.patch import PatchRiskLevel


class MockLLMProvider(LLMProvider):
    def __init__(self, response_text: str):
        self.response_text = response_text
        self.last_messages = []

    def generate(self, messages: list, temperature: float = 0.2) -> str:
        self.last_messages = messages
        return self.response_text


def test_openrouter_provider_config():
    p = OpenRouterProvider(api_key="sk-or-test", model="qwen/qwen-2.5-coder-32b-instruct:free")
    assert p.is_configured() is True
    assert p.model == "qwen/qwen-2.5-coder-32b-instruct:free"

    p_empty = OpenRouterProvider(api_key="")
    assert p_empty.is_configured() is False


def test_llm_reasoning_explain():
    mock_resp = "### Analysis\nInconsistent border radii harm visual hierarchy."
    mock_provider = MockLLMProvider(mock_resp)
    engine = LLMReasoningEngine(provider=mock_provider)

    finding = Finding(
        id="DESIGN-0001",
        category=FindingCategory.DESIGN,
        severity=Severity.MEDIUM,
        message="Inconsistent border radii",
        file="src/components/Card.tsx",
    )

    explanation = engine.explain_finding(finding)
    assert "Analysis" in explanation
    assert len(mock_provider.last_messages) == 2
    assert "DESIGN-0001" in mock_provider.last_messages[1]["content"]


def test_llm_reasoning_ai_patch(tmp_path):
    test_file = tmp_path / "Card.tsx"
    test_file.write_text("export const Card = () => <div className=\"rounded-sm\">Card</div>;\n", encoding="utf-8")

    mock_resp = "```tsx\nexport const Card = () => <div className=\"rounded-xl\">Card</div>;\n```"
    mock_provider = MockLLMProvider(mock_resp)
    engine = LLMReasoningEngine(provider=mock_provider)

    finding = Finding(
        id="DESIGN-0001",
        category=FindingCategory.DESIGN,
        severity=Severity.MEDIUM,
        message="Inconsistent border radii",
        file="Card.tsx",
    )

    patch = engine.generate_ai_patch(finding, tmp_path)
    assert patch is not None
    assert patch.finding_id == "DESIGN-0001"
    assert patch.risk_level == PatchRiskLevel.REVIEW
    assert "rounded-xl" in patch.patched_content
    assert "-export const Card = () => <div className=\"rounded-sm\">Card</div>;" in patch.diff
    assert "+export const Card = () => <div className=\"rounded-xl\">Card</div>;" in patch.diff
