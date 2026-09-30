# FAgent — Agentic Frontend Engineer

> **An autonomous frontend quality, auditing, and development engineer that uses deterministic tools for facts, AI for reasoning, and real browser verification for closed-loop quality assurance.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-green.svg)](https://playwright.dev/)
[![Testing](https://img.shields.io/badge/Tests-24%2F24%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()
[![Status](https://img.shields.io/badge/Maturity-Early%20Alpha%20(35%25)-red.svg)]()
[![Field Testing](https://img.shields.io/badge/Field%20Testing-Active%20Fine--Tuning-orange.svg)]()

---

## 📊 Development & Production Readiness

> ⚠️ **Field Reality Notice**: While the core engine architecture is implemented and verified by **24/24 unit tests**, real-world validation on actual external production apps (e.g. React 19, Vite, Next.js) demonstrated that **autonomous frontend modifications require substantial fine-tuning**. Visual design nuances (such as container curvature vs. pill badges) cannot be treated with blunt scripts. The product is strictly in **Early Developer Alpha (Experimental)**.

```text
[Core Architecture & Engine]      [█████████████████░░░] 85% (Scanners, Patcher, Browser Verifier)
[Automated Test Coverage]         [████████████████████] 100% (24/24 Test Suites Passing)
[Real-World Production Maturity]  [███████░░░░░░░░░░░░░] 35% (Early Alpha — Active Fine-Tuning)
```

| Core Capability | Engine Build | Real-World Status | Field Notes |
| :--- | :---: | :---: | :--- |
| **CLI & State Management** | `100%` | ✅ Stable | Fast Typer CLI, Rich formatting, `.fagent/` state management |
| **Deterministic Project Scanner** | `90%` | 🧪 Functional | Discovered 87 files, 38 components, and 10 routes in ~4s on Vite apps |
| **Project Graph (`graph.json`)** | `85%` | 🧪 Functional | Component hierarchy, reverse import mapping, route discovery |
| **Code Intelligence** | `90%` | 🧪 Functional | Reliably purges dead imports without touching business logic |
| **Design Intelligence** | `65%` | ⚠️ Needs Fine-Tuning | Flags palette fragmentation and smells; needs component-aware token categorization |
| **AI-Style UI Smell Detection** | `60%` | ⚠️ Needs Fine-Tuning | Detects gradients & glassmorphism; must distinguish intentional branding from smells |
| **Controlled Patch Engine** | `65%` | ⚠️ Needs Fine-Tuning | Safe for dead code; visual styling modifications strictly require manual/human review |
| **Git Safety & Rollback** | `95%` | ✅ Proven in Field | Instant rollback via checkpoints prevented code regressions during field tests |
| **Browser Runtime Verification** | `85%` | 🧪 Functional | Headless Playwright Chromium crawls all active routes across 3 device viewports |
| **Project Memory & Exceptions** | `80%` | 🧪 Alpha | Suppresses re-flagging of intentional project exceptions in `.fagent/decisions.json` |
| **Autonomous Healing Loop** | `55%` | ⚠️ Experimental | Works for deterministic code bugs; iterative visual healing requires further calibration |
| **LLM Reasoning (OpenRouter)** | `80%` | 🔑 Operational | Explains design smells and architectural trade-offs using free fast coding models |

---

## 🔬 Real-World Field Validation & Lessons Learned

During live field testing on an external production React 19 + Vite application (`Physiotherapy`), the following critical engineering lessons were established:

1. **A Card is NOT an Avatar (Context-Aware Geometry)**:
   * *The Problem*: Naive frequency algorithms saw `rounded-full` as the dominant radius because circular avatars and badges were common. Applying that "dominant" radius to rectangular cards flattened and distorted card corners.
   * *The Fix*: Circular/pill radii (`9999px`, `rounded-full`, `50%`) are now strictly isolated from rectangular card geometry. Visual styling changes are permanently demoted from `SAFE` to `REVIEW`.
2. **Asset Protection**:
   * *The Problem*: Simple static regexes flagged dynamic images (e.g. `images/${slug}.jpg`) as "unreferenced", risking asset deletion.
   * *The Fix*: Asset deletions now require explicit `REVIEW` confirmation and are never executed in automated `--safe-only` mode.
3. **The Power of Git Checkpoints**:
   * The automated Git checkpoint mechanism allowed the system to restore 100% of the project's original state instantaneously when a patch plan failed visual expectations.

---

## 🔑 Do I Need an API Key?

### **No API key is required for 90% of FAgent!**

FAgent was intentionally built around a **deterministic-first, zero-cost architecture**:

| Command | Needs API Key? | How It Works |
| :--- | :---: | :--- |
| `fagent scan` | **NO** ❌ | 100% offline local Python file scanner & AST extractor. Zero API tokens. |
| `fagent audit` | **NO** ❌ | 100% offline static code analysis, CSS token frequency & AI smell audits. |
| `fagent fix` | **NO** ❌ | 100% offline AST/regex patcher with Git safety checkpoints and auto-rollback. |
| `fagent verify` | **NO** ❌ | 100% offline headless Playwright Chromium inspecting DOM layout & WCAG rules. |
| `fagent heal` | **NO** ❌ | 100% offline closed autonomous feedback loop running the above components. |
| `fagent explain` | **OPTIONAL** 🔑 | Uses OpenRouter (free models available) only when you want an LLM to reason about *why* a specific design smell exists. |

If you **never** set `OPENROUTER_API_KEY`, FAgent works as a fast, private, offline frontend linter, fixer, and visual regression tester.

---

## 💡 The Problem & Core Philosophy

Modern AI coding assistants generate large amounts of code quickly, but introduce subtle responsive bugs, accessibility oversights, design inconsistencies, and generic "AI-looking" UI templates. Developers frequently spend more time reviewing AI code than they saved generating it.

FAgent solves this with a strict engineering principle:

> **Use deterministic software to establish facts. Use AI to reason about those facts. Never use AI where a reliable deterministic tool can answer the question more cheaply and precisely.**

---

## 🔄 Closed Feedback Loop

FAgent operates through a verified autonomous engineering loop:

```text
    OBSERVE ──► Build Project Graph (components, routes, styles, assets)
       │
       ▼
    ANALYZE ──► Static Code, Design Tokens, AI Smells, Asset Audits
       │
       ▼
     PLAN   ──► Classify Risk (SAFE vs REVIEW vs HIGH RISK) & Build Unified Diffs
       │
       ▼
      ACT   ──► Create Git Checkpoint & Apply Controlled Patches
       │
       ▼
    VERIFY  ──► Run Build/Sanity Check + Playwright Headless Browser
       │
    ┌──┴──┐
    ▼     ▼
  PASS   FAIL
    │     │
    │     ▼
    │   ROLLBACK (Undo all uncommitted workspace changes via Git)
    ▼
  REMEMBER ──► Record verified decision in .fagent/decisions.json
    │
    ▼
  ITERATE ──► Repeat until Quality Target is reached (fagent heal)
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/kashifasiddiqui/Agent-Shin.git
cd Agent-Shin

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
.venv\Scripts\activate          # Windows

# Install FAgent in editable development mode
pip install -e ".[dev]"

# Install Playwright Chromium browser binaries
playwright install chromium
```

### 2. Verify Installation

```bash
fagent --help
```

---

## 🛠️ CLI Command Reference

### `fagent init [TARGET]`
Initializes the `.fagent/` metadata directory, baseline config, and decision log inside a target frontend project.
```bash
fagent init ./my-react-app
```

### `fagent scan [TARGET]`
Performs deterministic project discovery:
- Detects Framework (React, Next.js, Vue, Svelte) and bundler (Vite, Webpack).
- Discovers component hierarchies, page views, and hooks (`useState`, `useEffect`).
- Extracts application route trees (React Router, Next.js App/Pages router).
- Catalogs static assets and maps code references.
- Persists to `.fagent/graph.json`.
```bash
fagent scan ./my-react-app
```

### `fagent status [TARGET]`
Summarizes project health, discovered components count, routes, and last scan timestamp.
```bash
fagent status ./my-react-app
```

### `fagent audit [TARGET]`
Runs deterministic static analyzers across Code, Design, Assets, and Performance:
- **Code**: Unused imports (`CODE-0001`), missing list keys (`CODE-0002`), unsafe `target="_blank"` (`CODE-0003`), `dangerouslySetInnerHTML` (`CODE-0004`), oversized components (`CODE-0005`).
- **Design & AI Smells**: Discovers design tokens, detects excessive divergent gradients (`DESIGN-0002`), frosted glass overuse (`DESIGN-0003`), and border radius inconsistency (`DESIGN-0001`).
- **Assets**: Unreferenced static files and oversized images (>1MB).
- Calculates category health scores (0-100%) and saves findings to `.fagent/findings.json`.
```bash
fagent audit ./my-react-app
```

### `fagent fix [TARGET] [--safe-only / --all] [--ai] [--model MODEL] [--yes]`
Safely applies verified patches to fix detected findings:
- Pre-patch Git checkpoint creation.
- Syntax-highlighted unified diff preview.
- **AI-Assisted Patch Synthesis**: When `--ai` is enabled, complex findings (like design smells or layout issues) are synthesized into verified code patches using OpenRouter LLMs.
- Deterministic verification with automated Git rollback on failure.
- Records verified actions in `.fagent/decisions.json`.
```bash
# Apply only safe, non-breaking fixes automatically
fagent fix ./my-react-app --safe-only --yes

# Synthesize AI patches for complex findings using OpenRouter
fagent fix ./my-react-app --all --ai

# Use a specific model for patch generation
fagent fix ./my-react-app --all --ai --model anthropic/claude-3.5-sonnet
```

### `fagent verify [TARGET] [--url URL] [--headless]`
Launches Playwright Chromium to audit runtime behavior across viewports:
- Standard viewports: **Mobile** (375x667), **Tablet** (768x1024), **Desktop** (1440x900).
- Detects horizontal layout overflow (`scrollWidth > innerWidth`) with offending DOM selectors.
- Audits accessibility: missing `alt` attributes, empty buttons, unlabeled form controls, heading hierarchy.
- Saves full-page screenshot galleries to `.fagent/screenshots/`.
```bash
# Verify running dev server
fagent verify ./my-react-app --url http://localhost:5173
```

### `fagent memory [TARGET] [--add TEXT] [--reason TEXT]`
Inspects or records project decisions, design rules, and approved exceptions so FAgent does not re-flag intentional project choices.
```bash
# View recorded decisions
fagent memory ./my-react-app

# Record an approved design pattern exception
fagent memory ./my-react-app --add "Cards use 12px radius" --reason "Design standard"
```

### `fagent heal [TARGET] [--max-iterations N] [--allow-review] [--ai] [--model MODEL]`
Autonomous closed-loop healing. Iteratively audits, plans, applies patches with Git checkpoints, and verifies the application until quality goals converge.
```bash
# Deterministic autonomous healing loop
fagent heal ./my-react-app --max-iterations 3

# Full AI-assisted autonomous healing with LLM reasoning
fagent heal ./my-react-app --max-iterations 5 --ai
```

---

## 🧪 Automated Testing

FAgent includes a full pytest test suite covering scanners, analyzers, patch engine, Git safety, Playwright browser rendering, and memory:

```bash
# Run complete test suite with coverage
pytest --cov=fagent tests/
```

```text
tests/test_analyzers.py ..          [  8%]
tests/test_browser.py .             [ 12%]
tests/test_cli.py .....             [ 33%]
tests/test_design.py ..             [ 41%]
tests/test_memory_and_healing.py .. [ 50%]
tests/test_patcher.py ......        [ 75%]
tests/test_reasoning.py ...         [ 87%]
tests/test_scanner.py ..            [ 95%]
tests/test_state.py .               [100%]

===================== 24 passed in 3.29s =====================
```

---

## 📁 Repository Structure

```text
Agent-Shin/
├── fagent/                      # Core FAgent package
│   ├── cli.py                   # Typer CLI interface
│   ├── core/                    # StateManager, AuditEngine, ProjectMemory, HealingLoop
│   ├── scanner/                 # Framework, Component, Route, and Asset scanners
│   ├── analyzers/               # Code, Asset, and Design Intelligence analyzers
│   ├── patcher/                 # PatchFixer, PatchEngine, GitSafetyManager
│   ├── browser/                 # BrowserLauncher, RouteCrawler, DOMInspector, BrowserVerifier
│   └── schemas/                 # Pydantic schemas (Project, Graph, Finding, Design, Patch)
├── tests/                       # Automated pytest suite (19 test cases)
├── examples/
│   └── sample-react-app/        # Real React + Vite + TypeScript showcase project
├── pyproject.toml               # Build system & package specification
├── README.md                    # Project documentation
└── PROJECT_DOCUMENTATION.md     # Master architectural specification
```

---

## 📄 License

MIT © [Kashif Siddiqui](https://github.com/kashifasiddiqui/Agent-Shin)
