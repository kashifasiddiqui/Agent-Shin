# FAgent — Agentic Frontend Engineer

## Master Project Documentation

**Project type:** Agentic AI Developer Tool  
**Initial interface:** CLI  
**Primary focus:** Frontend engineering  
**Initial target:** React / Vite / TypeScript projects  
**Architecture principle:** Local-first, evidence-driven, tool-using AI  
**Primary objective:** Make frontend development faster with AI without sacrificing code quality, visual quality, performance, responsiveness, accessibility, or maintainability.

---

# 1. Project Vision

## 1.1 The idea

The project is an **Agentic AI Frontend Engineer** designed to assist with rapid frontend development.

The goal is not simply to build another AI coding assistant that generates React code.

The goal is to build an agent that can:

- understand an entire frontend project
- remember project-specific decisions
- understand components regardless of how deeply they are nested
- find where UI elements are implemented
- review frontend code
- review the actual rendered interface
- detect visual and UX problems
- detect responsive problems
- detect accessibility problems
- detect performance issues
- detect inconsistent design patterns
- identify low-quality "AI-generated UI" patterns
- suggest improvements
- generate controlled patches
- verify those patches in a real browser
- roll back bad changes
- continue iterating until the project reaches a defined quality level

The long-term vision is:

> **An autonomous frontend engineer that uses AI to accelerate development while behaving like a rigorous human frontend engineer who continuously reviews, tests, optimizes, and improves the work.**

---

# 2. The Problem

Modern AI coding tools are extremely good at generating frontend code quickly.

However, rapid AI-generated development creates another problem:

```text
Fast generation
      ↓
Large amount of code
      ↓
Visual inconsistencies
      ↓
Responsive bugs
      ↓
Accessibility issues
      ↓
Unnecessary complexity
      ↓
Generic / AI-looking UI
      ↓
Developer manually reviews everything
```

The developer can end up spending almost as much time reviewing AI-generated code as they saved by generating it.

This project attempts to close that gap.

The agent should make this possible:

```text
AI-assisted development
        +
automated engineering review
        +
browser-based verification
        +
controlled autonomous fixes
```

---

# 3. Core Philosophy

The most important principle of the entire system is:

> **Use deterministic software to establish facts. Use AI to reason about those facts. Never use AI where a reliable deterministic tool can answer the question more cheaply and precisely.**

For example:

### Do not ask an LLM:

> "Find all files in this project."

Use the filesystem.

### Do not ask an LLM:

> "Does this TypeScript compile?"

Use TypeScript.

### Do not ask an LLM:

> "Does this page overflow horizontally?"

Inspect the browser and DOM.

### Do ask an LLM:

> "These three components use different visual patterns even though they represent the same UI concept. Determine whether they should be unified and propose the smallest safe change."

This separation makes the agent:

- cheaper
- faster
- more reliable
- easier to debug
- easier to test
- safer

---

# 4. What Makes FAgent Different

The project should not be positioned as:

> "AI that writes frontend."

Instead:

> **FAgent is an autonomous frontend quality and development engineer.**

It combines:

```text
Code Intelligence
+
Design Intelligence
+
Browser Intelligence
+
AI Reasoning
+
Controlled Code Modification
+
Verification
+
Project Memory
```

The distinctive feature is the **closed feedback loop**.

---

# 5. Core Agent Loop

The mature system should operate around:

```text
OBSERVE
   ↓
UNDERSTAND
   ↓
ANALYZE
   ↓
PLAN
   ↓
ACT
   ↓
TEST
   ↓
RENDER
   ↓
VERIFY
   ↓
LEARN
   ↓
OBSERVE AGAIN
```

More concretely:

```text
Project
   ↓
Scan
   ↓
Build project graph
   ↓
Analyze code/design/UI
   ↓
Generate findings
   ↓
Prioritize findings
   ↓
Reason about fixes
   ↓
Generate patch
   ↓
Apply controlled patch
   ↓
Run tests/build/lint
   ↓
Open browser
   ↓
Render affected pages
   ↓
Inspect screenshot + DOM
   ↓
Verify
   ↓
PASS → Keep
FAIL → Rollback / Re-plan
   ↓
Remember decision
   ↓
Continue
```

This loop is the heart of the product.

---

# 6. User Experience

The first version should be a CLI.

Example:

```bash
fagent init
fagent scan
fagent audit
fagent review
fagent fix
fagent verify
fagent heal
fagent status
```

Potential future commands:

```bash
fagent inspect component ProjectCard
fagent inspect route /projects
fagent explain UI-0042
fagent diff
fagent history
fagent memory
```

The CLI should remain useful even without an LLM.

---

# 7. Why CLI First

A CLI provides:

- simple development
- easy integration with Git
- easy integration with VS Code
- easy CI/CD integration
- low UI overhead
- fast iteration
- portability
- easy automation

The first product should not have a dashboard.

A GUI can be added later if it solves a real problem.

---

# 8. Project Separation

FAgent must be a standalone application.

Example:

```text
Projects/
│
├── frontend-agent/
│
├── bookstore-app/
├── portfolio-app/
├── hospital-app/
└── client-project/
```

`frontend-agent` contains the agent source code.

The other projects are targets that the agent can inspect and eventually modify.

This means FAgent is reusable across many projects.

---

# 9. Target Project State

When initialized:

```text
my-project/
│
├── src/
├── public/
├── package.json
│
└── .fagent/
    ├── config.json
    ├── project.json
    ├── graph.json
    ├── design-system.json
    ├── findings.json
    ├── decisions.json
    └── history/
```

The `.fagent/` directory contains project-specific agent state.

It should be possible to commit selected parts of this directory to Git, depending on the project's needs.

---

# 10. Initial Technology Stack

## Agent

```text
Python
Typer
Pydantic
pytest
Git
```

## Frontend analysis

```text
TypeScript
ESLint
AST / Tree-sitter
CSS parser / PostCSS-compatible tooling
```

## Browser

```text
Playwright
Chromium
```

## Accessibility

```text
axe-core
```

## Storage

```text
JSON
SQLite
```

## AI

Provider-agnostic LLM interface.

The exact model should be configurable rather than hard-coded into the architecture.

---

# 11. Why Python

Python is the initial backend language because it is strong for:

- AI integration
- orchestration
- automation
- filesystem operations
- subprocess management
- browser automation
- data processing
- rapid development

The target frontend remains JavaScript/TypeScript.

So the architecture becomes:

```text
Python Agent
     ↓
Frontend Project
     ↓
TypeScript / React / Vite / etc.
```

---

# 12. Initial Repository Structure

Start small.

```text
frontend-agent/
│
├── fagent/
│   ├── __init__.py
│   ├── cli.py
│   │
│   ├── scanner/
│   │   ├── __init__.py
│   │   └── project.py
│   │
│   └── schemas/
│       ├── __init__.py
│       └── project.py
│
├── tests/
│   └── test_scanner.py
│
├── examples/
│   └── sample-react-app/
│
├── docs/
│
├── pyproject.toml
├── README.md
├── PROJECT_DOCUMENTATION.md
└── .gitignore
```

Do not create every future directory immediately.

The architecture should grow with validated functionality.

---

# 13. Future Architecture

Eventually:

```text
frontend-agent/
│
├── fagent/
│   │
│   ├── cli/
│   │   └── commands/
│   │
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── state.py
│   │   └── events.py
│   │
│   ├── scanner/
│   │   ├── project.py
│   │   ├── framework.py
│   │   ├── components.py
│   │   ├── routes.py
│   │   ├── assets.py
│   │   └── dependencies.py
│   │
│   ├── analyzers/
│   │   ├── code.py
│   │   ├── design.py
│   │   ├── responsive.py
│   │   ├── accessibility.py
│   │   ├── performance.py
│   │   └── ai_smells.py
│   │
│   ├── browser/
│   │   ├── launcher.py
│   │   ├── crawler.py
│   │   ├── dom.py
│   │   └── screenshots.py
│   │
│   ├── reasoning/
│   │   ├── planner.py
│   │   ├── reasoner.py
│   │   └── prompts/
│   │
│   ├── patcher/
│   │   ├── planner.py
│   │   ├── apply.py
│   │   └── rollback.py
│   │
│   ├── verifier/
│   │   ├── tests.py
│   │   ├── build.py
│   │   └── visual.py
│   │
│   ├── memory/
│   │   ├── project.py
│   │   ├── decisions.py
│   │   └── history.py
│   │
│   └── schemas/
│       ├── project.py
│       ├── component.py
│       ├── finding.py
│       ├── patch.py
│       └── agent.py
│
├── tests/
├── examples/
├── docs/
├── pyproject.toml
├── README.md
└── .gitignore
```

---

# 14. Phase 1 — CLI Foundation

Commands:

```bash
fagent --help
fagent init
fagent scan
fagent status
```

Initially only `scan` needs meaningful behavior.

The CLI must remain thin.

Bad architecture:

```text
cli.py
└── all business logic
```

Good architecture:

```text
cli.py
   ↓
service
   ↓
scanner
   ↓
schemas
```

---

# 15. Phase 2 — Project Scanner

`fagent scan` should initially be deterministic.

It should discover:

## Project identity

- project root
- project name
- language
- framework
- framework version
- package manager

## Source

- source directories
- entry points
- components
- layouts
- pages

## Routing

- React Router routes
- Next.js routes
- recognizable routing structures

## Styling

- CSS
- SCSS
- Tailwind
- CSS Modules
- styled-components
- other recognizable systems

## Assets

- images
- SVGs
- fonts
- icons
- videos

## Dependencies

- runtime dependencies
- development dependencies

---

# 16. Project Graph

The project graph is one of the most important parts of the system.

The agent should not merely know that a file exists.

It should know relationships.

Example:

```text
Route: /projects
│
└── ProjectsPage
    │
    ├── Navbar
    │
    ├── ProjectGrid
    │   ├── ProjectCard
    │   ├── ProjectCard
    │   └── ProjectCard
    │
    └── Footer
```

The graph eventually represents:

```text
Project
 ├── Routes
 ├── Pages
 ├── Components
 ├── Layouts
 ├── Hooks
 ├── Styles
 ├── Assets
 ├── Dependencies
 └── Design Tokens
```

This is what allows the agent to answer questions such as:

> Where is the book card used on the `/books` page?

even if it is nested through multiple components.

---

# 17. Phase 3 — Code Intelligence

The system should use deterministic analysis before AI.

Potential findings:

```text
unused imports
dead code
missing keys
type errors
duplicated code
unnecessary complexity
bad component boundaries
unsafe patterns
```

Example finding:

```json
{
  "id": "CODE-0042",
  "category": "code",
  "severity": "medium",
  "file": "src/components/ProjectCard.tsx",
  "line": 42,
  "message": "Unused variable detected"
}
```

---

# 18. Phase 4 — Design Intelligence

The agent should learn the visual language of the target project.

Extract:

```text
Colors
Typography
Spacing
Border radius
Shadows
Breakpoints
Buttons
Cards
Inputs
Common layout patterns
```

Example:

```json
{
  "colors": {
    "primary": "#111827",
    "secondary": "#6B7280",
    "accent": "#F59E0B"
  },
  "radius": {
    "card": "12px",
    "button": "8px"
  }
}
```

The agent should not assume:

```text
purple = bad
gradient = bad
rounded = bad
```

Instead it should ask:

> Does this element match the established design language of this project?

---

# 19. AI-Style UI Smell Detection

One of the project's important differentiators.

The agent should detect patterns commonly associated with generic or low-quality AI-generated frontend output.

Examples:

```text
Excessive gradients
Excessive glassmorphism
Unnecessary glow effects
Random accent colors
Too many rounded cards
Inconsistent border radii
Excessive shadows
Generic decorative elements
Repetitive card layouts
Unnecessary icons
Weak information hierarchy
Generic hero sections
Generic imagery
```

The system must not claim:

> "This image was definitely generated by AI."

Instead:

```text
Potential AI-style UI pattern

Confidence: 91%

Evidence:
- 6 unrelated gradient treatments
- 4 different accent colors
- repeated glassmorphism cards
- inconsistent design tokens
```

The result is evidence-based rather than absolute.

---

# 20. Image and Asset Analysis

The agent should inspect:

```text
/public
/src/assets
/images
```

Possible findings:

- unused assets
- duplicate assets
- huge images
- low-resolution images
- incorrect aspect ratios
- broken references
- placeholder images
- suspicious generic imagery
- inconsistent image usage

Image provenance should be treated carefully.

The agent should report likelihood rather than make unsupported claims.

---

# 21. Phase 5 — Browser Agent

Playwright gives the agent access to the actual running application.

Workflow:

```text
Start dev server
      ↓
Launch Chromium
      ↓
Visit route
      ↓
Inspect DOM
      ↓
Inspect accessibility tree
      ↓
Inspect computed styles
      ↓
Capture screenshot
      ↓
Test viewport
```

Initial viewport set:

```text
375px
768px
1440px
```

Later:

```text
320px
390px
430px
1024px
1280px
1440px
1920px
```

Viewport selection should eventually be adaptive.

---

# 22. Visual QA

## Layout

Detect:

- overflow
- overlapping elements
- misalignment
- broken grids
- inconsistent spacing
- excessive whitespace

## Responsive behavior

Detect:

- mobile overflow
- broken navigation
- text clipping
- button wrapping
- unusable cards
- layout collapse

## Typography

Detect:

- inconsistent font sizes
- inconsistent weights
- poor hierarchy
- bad line heights
- overflow

## Visual consistency

Detect:

- unexpected colors
- inconsistent radius
- inconsistent shadows
- inconsistent button styles
- inconsistent spacing

---

# 23. Accessibility

Use axe-core plus browser/DOM information.

Potential checks:

- missing labels
- missing accessible names
- poor semantic structure
- keyboard issues
- contrast problems
- missing alt text
- focus problems
- invalid ARIA patterns

Automated accessibility checks should be distinguished from issues that require human judgment.

---

# 24. Performance Intelligence

Eventually inspect:

```text
bundle size
large assets
image optimization
unnecessary dependencies
rendering problems
layout shifts
network behavior
expensive components
```

Performance findings should be evidence-based.

Example:

```text
PERF-0021

Large hero image detected.

File:
public/images/hero.png

Size:
4.8 MB

Recommendation:
Convert to an optimized format and resize for actual display dimensions.
```

---

# 25. Finding Engine

All analyzers should output a common structure.

Example:

```json
{
  "id": "UI-0042",
  "category": "design",
  "severity": "medium",
  "file": "src/components/ProjectCard.tsx",
  "component": "ProjectCard",
  "route": "/projects",
  "message": "Card radius differs from the established project-card style",
  "evidence": {
    "actual": "18px",
    "expected": "12px"
  },
  "fixable": true
}
```

Possible categories:

```text
code
design
responsive
accessibility
performance
asset
architecture
```

---

# 26. Finding Lifecycle

```text
DETECTED
   ↓
VALIDATED
   ↓
PRIORITIZED
   ↓
PLANNED
   ↓
PATCHED
   ↓
VERIFIED
   ↓
RESOLVED
```

If verification fails:

```text
PATCHED
   ↓
FAILED
   ↓
ROLLED_BACK
```

The history should be retained.

---

# 27. LLM Reasoning Layer

Only introduce the LLM after deterministic scanning and analysis are reliable.

The LLM should receive evidence.

Example:

```text
Project graph
+
finding
+
affected files
+
design tokens
+
relevant DOM information
+
relevant screenshot
```

It should not receive the entire repository unnecessarily.

Responsibilities:

- reasoning
- code understanding
- finding prioritization
- ambiguous visual interpretation
- fix planning
- patch generation
- explanation

---

# 28. Tool Interface

The LLM should interact with explicit tools.

Potential tools:

```text
get_project_graph()
read_file(path)
search_code(query)
inspect_component(id)
inspect_route(route)
get_design_system()
inspect_dom(route)
get_screenshot(route, viewport)
run_lint()
run_tests()
run_build()
create_patch()
get_diff()
apply_patch()
rollback()
```

Every tool returns structured results.

The model should never invent tool output.

---

# 29. Model Strategy

The system should be provider-agnostic.

Conceptually:

```text
LLMProvider
    |
    +-- CloudProvider
    |
    +-- LocalProvider
```

The model should be selected according to task complexity.

### No model required

Use deterministic tools for:

- file discovery
- framework detection
- AST parsing
- linting
- type checking
- tests
- DOM measurements
- Git operations
- basic accessibility rules

### Small/fast model

Use for:

- simple explanations
- finding categorization
- basic fix suggestions

### Stronger model

Use for:

- multi-file reasoning
- architecture decisions
- difficult refactoring
- ambiguous design analysis

### Vision-capable model

Use only when screenshot interpretation provides value.

This avoids making every operation expensive.

---

# 30. Cost Strategy

The system should have a free/local baseline.

Free components:

```text
Python
Typer
Pydantic
Git
ESLint
TypeScript
Playwright
Chromium
axe-core
SQLite
pytest
AST parsing
```

The main potentially paid component is model inference.

Therefore:

> Minimize model calls.

Do not send the entire project to the model repeatedly.

Use targeted context.

---

# 31. Token Optimization

Instead of:

```text
Entire repository
+
all screenshots
+
all history
```

send:

```text
Finding
+
affected component
+
relevant styles
+
design tokens
+
relevant screenshot
+
small project context
```

This reduces:

- cost
- latency
- context noise

---

# 32. Caching

Cache:

```text
file hashes
AST results
project graph
design tokens
browser results
screenshots
model results where safe
```

If a file did not change, do not analyze it again.

---

# 33. Incremental Analysis

This is essential for performance.

Suppose:

```text
src/components/BookCard.tsx
```

changes.

The agent should not automatically re-audit the entire application.

Instead:

```text
Changed file
    ↓
Affected component
    ↓
Dependent components
    ↓
Affected routes
    ↓
Targeted verification
```

This becomes possible because of the project graph.

---

# 34. Parallel Processing

Independent operations can run concurrently:

```text
Code analysis
Asset analysis
Style analysis
Dependency analysis
```

Use bounded concurrency.

Do not create unlimited subprocesses or browser instances.

---

# 35. Patch Engine

The agent should never directly rewrite arbitrary files without controls.

Workflow:

```text
Finding
   ↓
Patch Plan
   ↓
Risk Classification
   ↓
Generate Diff
   ↓
Approval if required
   ↓
Apply
```

Every change should be Git-aware.

---

# 36. Risk Levels

## SAFE

Examples:

```text
formatting
unused imports
obvious lint fixes
dead code
```

Can eventually be automatically applied.

## REVIEW

Examples:

```text
style changes
layout changes
responsive fixes
accessibility changes
component restructuring
```

Require approval initially.

## HIGH RISK

Examples:

```text
dependency changes
API changes
major architecture changes
large refactors
infrastructure changes
```

Require explicit approval.

---

# 37. Verification Engine

A patch is not successful merely because it compiles.

Verification:

```text
Type checking
   ↓
Linting
   ↓
Unit tests
   ↓
Build
   ↓
Browser rendering
   ↓
Screenshot inspection
   ↓
Accessibility
   ↓
Responsive checks
```

Then:

```text
PASS → Keep
FAIL → Rollback / Re-plan
```

---

# 38. Git Safety

Before modifying:

```text
Create checkpoint
```

After modification:

```text
Build
Tests
Lint
Browser verification
```

If verification fails:

```text
Rollback
```

Git becomes a safety mechanism for autonomous development.

---

# 39. Security

The agent will eventually execute code from arbitrary frontend projects.

Treat target projects as potentially untrusted.

Important principles:

- read-only by default
- explicit write permissions
- Git checkpoints
- restricted tool access
- no unrestricted shell access
- protect environment variables
- do not expose secrets to models
- isolate risky operations where possible

Potential sensitive files:

```text
.env
credentials
private keys
tokens
API keys
```

These should not automatically become model context.

---

# 40. Project Memory

The agent needs project-specific memory.

Initially:

```text
.fagent/
├── project.json
├── graph.json
├── design-system.json
├── decisions.json
├── findings.json
└── history/
```

Memory can contain:

```text
preferred colors
preferred spacing
approved patterns
user decisions
known exceptions
previous findings
previous fixes
```

Example:

```json
{
  "decision": "Project cards use 12px radius",
  "scope": "ProjectCard",
  "reason": "Established design pattern",
  "source": "user-approved"
}
```

This prevents the agent from repeatedly reporting intentional exceptions.

---

# 41. Why Not a Vector Database Initially?

A vector database may be useful later, but it is unnecessary for the first version.

The first memory system can use:

```text
JSON
+
SQLite
+
project graph
+
file search
```

Introduce semantic retrieval only when actual usage demonstrates the need.

This keeps the project:

- simpler
- cheaper
- faster
- easier to debug

---

# 42. Autonomous Mode

Eventually:

```bash
fagent heal
```

could perform:

```text
Audit
 ↓
Prioritize
 ↓
Plan
 ↓
Patch
 ↓
Verify
 ↓
Repeat
```

But autonomous mode needs hard limits.

Example:

```text
max_iterations: 5
max_files_changed: 20
max_patch_lines: 200
max_risk: REVIEW
require_approval_for_high_risk: true
```

Stop conditions:

```text
No meaningful findings
OR
Repeated verification failure
OR
Change budget reached
OR
Approval required
OR
Risk threshold exceeded
```

---

# 43. Failure Modes and Loopholes

## 43.1 False positives

Problem:

The agent flags a valid design choice.

Solution:

Compare against:

```text
project design system
existing patterns
component context
project memory
user-approved decisions
```

---

## 43.2 Over-correction

Problem:

The agent makes a frontend too uniform.

Solution:

Preserve intentional variation.

The goal is consistency, not visual monotony.

---

## 43.3 AI hallucination

Problem:

The model claims something exists that does not.

Solution:

Require evidence from tools before creating a finding or patch.

---

## 43.4 Destructive fixes

Problem:

One fix breaks another area.

Solution:

```text
Git checkpoint
→ patch
→ build
→ tests
→ browser verification
→ rollback
```

---

## 43.5 Infinite loops

Problem:

The agent repeatedly fixes and reintroduces issues.

Solution:

- iteration limits
- finding history
- patch similarity detection
- maximum runtime
- maximum change count

---

## 43.6 Screenshot-only reasoning

Problem:

A screenshot does not reveal the complete implementation.

Solution:

Combine:

```text
Screenshot
+
DOM
+
computed styles
+
source
+
project graph
```

---

## 43.7 AI-generated image detection uncertainty

Problem:

Image provenance cannot reliably be determined from pixels alone.

Solution:

Report:

```text
Potential synthetic/generic asset
Confidence
Evidence
```

rather than an absolute claim.

---

## 43.8 Context overload

Problem:

The model receives too much project information.

Solution:

Use the graph to retrieve only relevant context.

---

## 43.9 Slow browser audits

Problem:

Rendering every page at every viewport becomes expensive.

Solution:

Use incremental analysis and affected-route selection.

---

## 43.10 Too many agents

Problem:

Multiple LLM agents create complexity, token cost, and coordination problems.

Solution:

Start with one orchestrator and deterministic specialized tools.

Introduce multi-agent behavior only if a measured limitation requires it.

---

# 44. Performance Architecture

The system should optimize for:

```text
Latency
Cost
Accuracy
Reliability
```

Not just model intelligence.

Important optimizations:

### 1. Incremental scanning

Only inspect changed files.

### 2. Dependency graph

Identify affected components/routes.

### 3. Cached analysis

Avoid repeated work.

### 4. Parallel deterministic analysis

Run independent analyzers concurrently.

### 5. Targeted browser rendering

Only render affected routes when possible.

### 6. Selective vision

Only send screenshots to vision models when visual reasoning is needed.

### 7. Small-context reasoning

Send evidence rather than repositories.

### 8. Model routing

Use the smallest model capable of the task.

---

# 45. Development Phases

## Phase 0 — Environment

```text
Create repository
Create Python environment
Create pyproject.toml
Install initial dependencies
Initialize Git
```

## Phase 1 — CLI

```text
fagent --help
fagent init
fagent scan
fagent status
```

## Phase 2 — Scanner

```text
Framework detection
Language detection
Package manager
File discovery
Component discovery
Route discovery
Asset discovery
Dependency discovery
```

## Phase 3 — Project Graph

```text
Project model
Component model
Route model
Asset model
Dependency model
Graph generation
Graph persistence
```

## Phase 4 — Code Intelligence

```text
ESLint
TypeScript
AST
Finding schema
Finding persistence
```

## Phase 5 — Design Intelligence

```text
Color extraction
Typography
Spacing
Radius
Shadows
Design tokens
Consistency analysis
AI-style UI smell detection
```

## Phase 6 — Browser Intelligence

```text
Start dev server
Launch Playwright
Discover routes
Render pages
Capture screenshots
Inspect DOM
Inspect accessibility
Test viewports
```

## Phase 7 — AI Reasoning

```text
LLM provider abstraction
Tool interface
Evidence collection
Finding reasoning
Prioritization
Fix planning
```

## Phase 8 — Patching

```text
Git checkpoint
Diff generation
Risk classification
Patch application
Approval workflow
Rollback
```

## Phase 9 — Verification

```text
Build
Tests
Lint
Browser
Visual
Accessibility
Performance
```

## Phase 10 — Memory

```text
Project memory
Decisions
Design preferences
Finding history
Change history
```

## Phase 11 — Autonomous Agent

```text
Observe
Analyze
Plan
Act
Test
Render
Verify
Learn
Iterate
```

---

# 46. MVP Definition

The first meaningful MVP should NOT be a fully autonomous coding agent.

It should be:

> **A CLI that can understand a real React frontend and produce an evidence-backed quality audit.**

MVP capabilities:

```text
[✓] Detect project
[✓] Detect framework
[✓] Discover components
[✓] Discover routes
[✓] Discover assets
[✓] Build project graph
[✓] Run static analysis
[✓] Extract design system
[✓] Run browser audit
[✓] Detect UI issues
[✓] Produce findings
```

Then add controlled fixes.

---

# 47. V1 Definition

V1 should be able to:

1. Accept a real frontend project.
2. Understand its structure.
3. Build a project graph.
4. Detect code issues.
5. Detect design inconsistencies.
6. Detect responsive issues.
7. Detect accessibility issues.
8. Run the application.
9. Inspect it through a browser.
10. Produce evidence-backed findings.
11. Propose a patch.
12. Show the user a diff.
13. Apply an approved patch.
14. Verify the patch.
15. Roll back failed changes.
16. Remember project-specific decisions.

---

# 48. V2 Definition

V2 becomes the autonomous frontend engineer.

It should:

```text
Detect changes
   ↓
Understand impact
   ↓
Audit
   ↓
Prioritize
   ↓
Plan
   ↓
Patch
   ↓
Verify
   ↓
Learn
   ↓
Repeat
```

This is where `fagent heal` becomes meaningful.

---

# 49. Advantages

## 49.1 Faster development

AI handles repetitive implementation and review tasks.

## 49.2 Better consistency

The agent learns the actual project's visual language.

## 49.3 Reduced manual QA

The browser agent can automatically check multiple routes and viewports.

## 49.4 Safer AI coding

Changes are verified instead of blindly accepted.

## 49.5 Project memory

The agent can remember approved decisions and exceptions.

## 49.6 Framework independence over time

The architecture can eventually support:

```text
React
Next.js
Vue
Nuxt
Svelte
Angular
```

without changing the fundamental agent architecture.

## 49.7 CI/CD potential

The same audit system can eventually run during:

```text
pull requests
CI
pre-commit
deployment pipelines
```

---

# 50. Disadvantages

## 50.1 Complexity

An autonomous coding agent is significantly more complex than a normal CLI.

### Solution

Build incrementally.

---

## 50.2 False positives

Visual quality is partly subjective.

### Solution

Use evidence, project-specific patterns, and user-approved decisions.

---

## 50.3 LLM cost

Complex reasoning can become expensive.

### Solution

Deterministic tools + caching + model routing + targeted context.

---

## 50.4 Browser execution cost

Rendering many pages is slower than static analysis.

### Solution

Incremental route selection and targeted verification.

---

## 50.5 Risk of bad autonomous changes

### Solution

Git checkpoints, risk levels, approval gates, verification, and rollback.

---

## 50.6 AI cannot fully replace human design judgment

Some design decisions are subjective.

### Solution

The agent should assist rather than pretend that every aesthetic decision is objectively correct.

---

## 50.7 Security concerns

The agent may execute project code.

### Solution

Restricted tools, isolated execution where necessary, secret filtering, explicit permissions.

---

# 51. How to Overcome the Cons

The overall strategy is:

```text
Complexity
→ modular architecture

Cost
→ deterministic analysis + caching + model routing

False positives
→ evidence + project memory

Bad patches
→ Git + verification + rollback

Slow performance
→ incremental analysis

Hallucination
→ tool-grounded reasoning

Security
→ permissioned tools

Subjectivity
→ user preferences + confidence + approval
```

---

# 52. Free / Low-Cost Strategy

A complete useful version can be developed with minimal or zero software licensing cost.

Use:

```text
Python
Git
Typer
Pydantic
pytest
Playwright
Chromium
TypeScript
ESLint
axe-core
SQLite
AST tooling
```

All core engineering infrastructure can be local.

The only component that may introduce recurring cost is LLM inference.

To minimize this:

```text
Use AI only where necessary
Cache results
Use small models for simple tasks
Use stronger models only for difficult reasoning
Keep prompts small
Do deterministic analysis first
```

A local model can also be supported later.

---

# 53. Can the Whole System Run Locally?

Yes, the architecture should be designed so that most of it can run locally.

```text
Developer Machine
│
├── FAgent
├── Python
├── Playwright
├── Chromium
├── TypeScript
├── ESLint
├── Git
├── SQLite
└── Optional local LLM
```

Cloud models can be optional rather than mandatory.

This is useful for:

- privacy
- cost control
- offline development
- client projects
- sensitive codebases

---

# 54. Future CI/CD Integration

Eventually:

```text
Pull Request
     ↓
fagent audit
     ↓
Code findings
     ↓
UI findings
     ↓
Accessibility
     ↓
Performance
     ↓
Report
```

Possible future integrations:

```text
GitHub Actions
GitLab CI
VS Code
JetBrains
pre-commit hooks
deployment pipelines
```

The CLI-first design makes these integrations easier.

---

# 55. Future Framework Support

The first target:

```text
React + Vite + TypeScript
```

Then:

```text
Next.js
Vue
Nuxt
Svelte
Angular
```

Framework-specific scanners should plug into a common interface:

```text
FrameworkAdapter
    |
    +-- ReactAdapter
    +-- NextAdapter
    +-- VueAdapter
    +-- SvelteAdapter
```

The project graph should remain framework-independent wherever possible.

---

# 56. Future Developer Experience

A mature interaction could look like:

```bash
fagent scan
```

```text
Project analyzed.

64 components
8 routes
37 assets
12 style files

3 critical issues
11 warnings
18 suggestions
```

Then:

```bash
fagent audit
```

```text
Frontend Quality Audit

Code             91%
Design           83%
Responsive       78%
Accessibility    86%
Performance      88%

AI-style UI patterns: 6
```

Then:

```bash
fagent fix
```

```text
Found 11 fixable issues.

5 safe
4 review required
2 high risk

Apply 5 safe fixes? [Y/n]
```

Then:

```text
Applying patches...

✓ Removed unused imports
✓ Unified button spacing
✓ Fixed mobile overflow
✓ Corrected card radius
✓ Optimized image loading

Running verification...

✓ Build
✓ Tests
✓ Lint
✓ Browser
✓ Responsive
✓ Accessibility

5/5 fixes verified.
```

This is the intended developer experience.

---

# 57. The Most Important Design Principle

The agent should not optimize only for:

> "How much code can AI generate?"

It should optimize for:

> **How quickly can a developer reach production-quality frontend code with confidence?**

That means the system must measure the whole engineering lifecycle:

```text
Generation speed
+
Review speed
+
Fix speed
+
Verification speed
+
Regression prevention
```

---

# 58. What the Agent Should Eventually "Know"

The agent should understand five layers.

## Layer 1 — Source

```text
Files
Components
Functions
Styles
Dependencies
```

## Layer 2 — Structure

```text
Routes
Component relationships
Imports
Layouts
Data flow
```

## Layer 3 — Design

```text
Colors
Typography
Spacing
Radius
Shadows
Patterns
```

## Layer 4 — Runtime

```text
DOM
Browser
Screenshots
Accessibility
Responsive behavior
Performance
```

## Layer 5 — History

```text
User decisions
Approved fixes
Known exceptions
Previous failures
Project preferences
```

Together:

```text
Source
  +
Structure
  +
Design
  +
Runtime
  +
History
```

creates the agent's understanding of the project.

---

# 59. What We Should NOT Compromise

The following capabilities should remain fundamental:

```text
Project-wide understanding
Component discovery
Design-system awareness
Browser verification
Responsive testing
Accessibility
Evidence-backed findings
Git safety
Rollback
Project memory
Incremental analysis
Provider-independent AI
```

Speed should come from architecture and optimization, not from removing these capabilities.

---

# 60. Immediate Implementation Plan

Do not start by implementing the entire architecture.

Start with:

## Step 1

Create:

```text
frontend-agent/
```

## Step 2

Open it in VS Code.

## Step 3

Create a Python virtual environment.

## Step 4

Create:

```text
pyproject.toml
```

## Step 5

Create:

```text
fagent/
tests/
examples/
docs/
```

## Step 6

Implement:

```bash
fagent --help
```

## Step 7

Implement:

```bash
fagent init
```

## Step 8

Implement:

```bash
fagent scan
```

## Step 9

Test against an actual React/Vite project.

## Step 10

Generate the first:

```text
.fagent/graph.json
```

Only after this works reliably should the next phase begin.

---

# 61. First Milestone Definition

The first milestone is complete when:

```text
[✓] fagent installs
[✓] fagent --help works
[✓] fagent init works
[✓] fagent scan works
[✓] Framework detected
[✓] Language detected
[✓] Components discovered
[✓] Routes discovered
[✓] Assets discovered
[✓] Dependencies discovered
[✓] graph.json generated
[✓] Scan does not modify source code
[✓] Scanner has tests
```

This becomes the foundation for the entire project.

---

# 62. Final Architecture

The mature system can be summarized as:

```text
                         DEVELOPER
                             │
                             ▼
                         FAGENT CLI
                             │
                             ▼
                      ORCHESTRATOR
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
       SCANNER           ANALYZERS           BROWSER
          │                  │                  │
          │          ┌───────┼────────┐         │
          │          │       │        │         │
          │        CODE    DESIGN   ACCESS.   RENDER
          │          │       │        │         │
          └──────────┴───────┴────────┴─────────┘
                             │
                             ▼
                         EVIDENCE
                             │
                             ▼
                       LLM REASONER
                             │
                             ▼
                       FIX PLANNER
                             │
                             ▼
                       PATCH ENGINE
                             │
                             ▼
                         GIT CHECKPOINT
                             │
                             ▼
                          VERIFIER
                             │
                  ┌──────────┴──────────┐
                  │                     │
                 PASS                  FAIL
                  │                     │
                  ▼                     ▼
                KEEP                  ROLLBACK
                  │
                  ▼
               MEMORY
                  │
                  └──────────► NEXT LOOP
```

---

# 63. Final Project Definition

FAgent is an **agentic frontend engineering system**.

It is designed to make AI-assisted frontend development:

```text
FAST
+
CONSISTENT
+
OPTIMIZED
+
VERIFIABLE
+
SAFE
```

It is not simply an AI code generator.

It is not simply a code reviewer.

It is not simply a visual testing tool.

It combines all three with project memory and controlled autonomous execution.

The ultimate workflow is:

```text
Developer creates
       ↓
FAgent understands
       ↓
FAgent reviews
       ↓
FAgent finds problems
       ↓
FAgent proposes improvements
       ↓
FAgent modifies safely
       ↓
FAgent runs the application
       ↓
FAgent verifies the real UI
       ↓
FAgent rolls back failures
       ↓
FAgent remembers decisions
       ↓
FAgent continues improving
```

The long-term goal is:

> **A frontend engineer that lets the developer move at AI speed while maintaining the engineering discipline of a highly experienced human frontend developer.**

---

# 64. Current Project Status

## Planning complete

The following have been defined:

```text
✓ Project vision
✓ Problem statement
✓ Product positioning
✓ CLI-first strategy
✓ Project separation
✓ Agent loop
✓ Architecture
✓ Repository structure
✓ Scanner
✓ Project graph
✓ Code intelligence
✓ Design intelligence
✓ AI-style UI detection
✓ Browser intelligence
✓ Accessibility
✓ Performance
✓ LLM strategy
✓ Tool interface
✓ Patch engine
✓ Verification
✓ Git safety
✓ Project memory
✓ Security
✓ Failure modes
✓ Cost strategy
✓ Performance strategy
✓ Free/local strategy
✓ Development phases
✓ MVP
✓ V1
✓ V2
✓ Pros
✓ Cons
✓ Mitigations
✓ Long-term roadmap
```

## Next task

Begin implementation with:

```text
CLI
→ init
→ scan
→ project graph
```

Do not introduce autonomous LLM behavior until the deterministic foundation is reliable.

---

# 65. One-Sentence Summary

> **FAgent is a local-first, CLI-based agentic AI frontend engineer that understands a project at source, structural, design, runtime, and historical levels, uses deterministic tools for evidence and AI for reasoning, safely modifies code, verifies the real browser output, remembers project decisions, and continuously improves frontend quality.**
