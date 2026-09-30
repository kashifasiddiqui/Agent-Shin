# FAgent — Agentic Frontend Engineer

> Autonomous frontend quality and development engineer.

FAgent is a local-first, CLI-based agentic AI frontend engineer designed to assist with rapid frontend development without sacrificing code quality, visual consistency, responsiveness, accessibility, or maintainability.

## Core Philosophy

> **Use deterministic software to establish facts. Use AI to reason about those facts. Never use AI where a reliable deterministic tool can answer the question more cheaply and precisely.**

## Getting Started

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd Agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install editable package
pip install -e ".[dev]"
```

### Basic Commands

```bash
# Display help and commands
fagent --help

# Initialize FAgent in a frontend project
fagent init

# Scan project structure, components, routes, assets, and dependencies
fagent scan

# View current project status and statistics
fagent status
```
