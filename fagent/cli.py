import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Ensure UTF-8 output on Windows consoles if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fagent.core.state import StateManager
from fagent.core.audit import AuditEngine
from fagent.core.memory import ProjectMemory
from fagent.core.orchestrator import HealingLoop
from fagent.patcher.engine import PatchEngine
from fagent.browser.verifier import BrowserVerifier
from fagent.scanner.project import ProjectScanner
from fagent.schemas.finding import Finding, Severity
from fagent.schemas.patch import PatchRiskLevel
from fagent import __version__

app = typer.Typer(
    name="fagent",
    help="FAgent - Autonomous frontend quality, auditing, and development engineer.",
    add_completion=False,
)
console = Console(safe_box=True)


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]FAgent[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show FAgent version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """FAgent CLI - Agentic Frontend Engineer."""
    pass


@app.command()
def init(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)")
):
    """Initialize FAgent in a frontend project directory."""
    project_root = Path(target).resolve()
    if not project_root.exists():
        console.print(f"[bold red]Error:[/bold red] Target directory does not exist: {project_root}")
        raise typer.Exit(code=1)

    state = StateManager(project_root)
    if state.is_initialized():
        console.print(f"[yellow]Project is already initialized at:[/yellow] {state.fagent_dir}")
        return

    fagent_path = state.init_fagent()
    console.print(
        Panel.fit(
            f"[bold green]Initialized FAgent project![/bold green]\n"
            f"[dim]State directory:[/dim] {fagent_path}\n"
            f"[dim]Config created:[/dim] {fagent_path / 'config.json'}\n\n"
            f"Next step: run [bold cyan]fagent scan {target}[/bold cyan] to analyze the project.",
            title="FAgent Init",
            border_style="cyan"
        )
    )


@app.command()
def scan(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)"),
    save: bool = typer.Option(True, "--save/--no-save", help="Persist results to .fagent/ directory")
):
    """Scan and build the project graph, identifying components, routes, assets, and styling."""
    project_root = Path(target).resolve()
    if not project_root.exists():
        console.print(f"[bold red]Error:[/bold red] Target directory does not exist: {project_root}")
        raise typer.Exit(code=1)

    with console.status("[bold cyan]Scanning project structure and components...", spinner="dots"):
        scanner = ProjectScanner(project_root)
        graph = scanner.scan()

    state = StateManager(project_root)
    if save:
        if not state.is_initialized():
            state.init_fagent()
        state.save_project_info(graph.project)
        state.save_graph(graph)

    # 1. Project Summary Table
    proj_table = Table(title=f"Project Identity: [bold cyan]{graph.project.name}[/bold cyan]", box=box.ROUNDED)
    proj_table.add_column("Property", style="dim")
    proj_table.add_column("Detected Value", style="bold")

    proj_table.add_row("Framework", f"{graph.project.framework.value} {graph.project.framework_version or ''}")
    proj_table.add_row("Bundler / Build Tool", graph.project.bundler or "Standard")
    proj_table.add_row("Language", graph.project.language.value)
    proj_table.add_row("Package Manager", graph.project.package_manager.value)
    proj_table.add_row("Styling Systems", ", ".join([s.value for s in graph.project.styling_systems]))
    proj_table.add_row("Source Directory", graph.project.src_dir or ".")
    proj_table.add_row("Entry Points", ", ".join(graph.project.entry_points) or "None")
    proj_table.add_row("Total Source Files", str(graph.project.total_files))
    proj_table.add_row("Components Discovered", str(len(graph.components)))
    proj_table.add_row("Routes Discovered", str(len(graph.routes)))
    proj_table.add_row("Static Assets", str(len(graph.assets)))

    console.print(proj_table)

    # 2. Components Table (if any)
    if graph.components:
        comp_table = Table(title="Discovered Components", box=box.SIMPLE_HEAVY)
        comp_table.add_column("Component", style="cyan")
        comp_table.add_column("Type", style="magenta")
        comp_table.add_column("File Path", style="dim")
        comp_table.add_column("Imports", style="blue")
        comp_table.add_column("Hooks Used", style="green")
        comp_table.add_column("LOC", justify="right")

        for name, comp in list(graph.components.items())[:15]:
            comp_type = "Page" if comp.is_page else ("Layout" if comp.is_layout else "Component")
            comp_table.add_row(
                name,
                comp_type,
                comp.file_path,
                ", ".join(comp.imported_components[:3]) + ("..." if len(comp.imported_components) > 3 else ""),
                ", ".join(comp.hooks[:3]) + ("..." if len(comp.hooks) > 3 else ""),
                str(comp.lines_of_code),
            )
        if len(graph.components) > 15:
            comp_table.add_row("...", f"... and {len(graph.components) - 15} more", "", "", "", "")

        console.print(comp_table)

    # 3. Routes Table (if any)
    if graph.routes:
        route_table = Table(title="Discovered Routes", box=box.SIMPLE)
        route_table.add_column("Path", style="bold green")
        route_table.add_column("Component", style="cyan")
        route_table.add_column("File Path", style="dim")

        for r in graph.routes:
            route_table.add_row(r.path, r.component_name or "-", r.file_path or "-")

        console.print(route_table)

    if save:
        console.print(f"[bold green][OK][/bold green] Saved project graph to [dim]{state.fagent_dir / 'graph.json'}[/dim]")


@app.command()
def status(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)")
):
    """View current FAgent project status and graph statistics."""
    project_root = Path(target).resolve()
    state = StateManager(project_root)

    if not state.is_initialized():
        console.print(f"[yellow]Project is not initialized yet. Run [bold cyan]fagent init {target}[/bold cyan] first.[/yellow]")
        return

    proj = state.load_project_info()
    graph = state.load_graph()

    if not proj or not graph:
        console.print("[yellow]Project is initialized, but has not been scanned yet. Run [bold cyan]fagent scan[/bold cyan].[/yellow]")
        return

    console.print(
        Panel.fit(
            f"[bold cyan]Project:[/bold cyan] {proj.name}\n"
            f"[dim]Framework:[/dim] {proj.framework.value} ({proj.language.value})\n"
            f"[dim]Bundler:[/dim] {proj.bundler or 'Standard'}\n"
            f"[dim]Components:[/dim] {len(graph.components)}\n"
            f"[dim]Routes:[/dim] {len(graph.routes)}\n"
            f"[dim]Assets:[/dim] {len(graph.assets)}\n"
            f"[dim]Last scan:[/dim] {graph.generated_at}",
            title="FAgent Status",
            border_style="green"
        )
    )


@app.command()
def audit(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)"),
    save: bool = typer.Option(True, "--save/--no-save", help="Persist findings to .fagent/findings.json")
):
    """Run static and quality analyzers across the project to produce an evidence-backed audit report."""
    project_root = Path(target).resolve()
    if not project_root.exists():
        console.print(f"[bold red]Error:[/bold red] Target directory does not exist: {project_root}")
        raise typer.Exit(code=1)

    state = StateManager(project_root)
    graph = state.load_graph()

    # If graph doesn't exist, run scan first
    if not graph:
        with console.status("[bold cyan]Scanning project structure first...", spinner="dots"):
            scanner = ProjectScanner(project_root)
            graph = scanner.scan()
            if save:
                if not state.is_initialized():
                    state.init_fagent()
                state.save_project_info(graph.project)
                state.save_graph(graph)

    with console.status("[bold cyan]Running code and asset intelligence analyzers...", spinner="dots"):
        engine = AuditEngine(project_root)
        report = engine.run_audit(graph)

    if save:
        if not state.is_initialized():
            state.init_fagent()
        state.save_findings(report.findings)
        state.save_audit_report(report)

    # 1. Overall Score Panel
    score_color = "green" if report.overall_score >= 85 else ("yellow" if report.overall_score >= 70 else "red")
    console.print(
        Panel.fit(
            f"Overall Quality Score: [bold {score_color}]{report.overall_score}%[/bold {score_color}]\n"
            f"Total Findings: [bold]{report.total_findings}[/bold] ([cyan]{report.fixable_findings} fixable[/cyan])",
            title="Frontend Quality Audit",
            border_style=score_color,
        )
    )

    # 2. Category Breakdown Table
    cat_table = Table(title="Category Scores", box=box.ROUNDED)
    cat_table.add_column("Category", style="cyan")
    cat_table.add_column("Score", style="bold")
    cat_table.add_column("Findings", justify="right")
    cat_table.add_column("Critical", style="bold red", justify="right")
    cat_table.add_column("High", style="red", justify="right")
    cat_table.add_column("Medium", style="yellow", justify="right")
    cat_table.add_column("Low", style="dim", justify="right")

    for cat_name, cat_score in report.category_scores.items():
        c_color = "green" if cat_score.score >= 85 else ("yellow" if cat_score.score >= 70 else "red")
        cat_table.add_row(
            cat_name.capitalize(),
            f"[{c_color}]{cat_score.score}%[/{c_color}]",
            str(cat_score.total_findings),
            str(cat_score.critical_count),
            str(cat_score.high_count),
            str(cat_score.medium_count),
            str(cat_score.low_count),
        )

    console.print(cat_table)

    # 3. Findings Detail Table
    if report.findings:
        find_table = Table(title=f"Detected Findings ({len(report.findings)})", box=box.SIMPLE_HEAVY)
        find_table.add_column("ID", style="bold cyan")
        find_table.add_column("Severity", style="bold")
        find_table.add_column("Category", style="magenta")
        find_table.add_column("Location", style="dim")
        find_table.add_column("Message", style="white")
        find_table.add_column("Fixable", style="green", justify="center")

        severity_colors = {
            Severity.CRITICAL: "bold red",
            Severity.HIGH: "red",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "dim blue",
            Severity.INFO: "dim",
        }

        for f in report.findings[:20]:
            sev_color = severity_colors.get(f.severity, "white")
            loc = f.file or "-"
            if f.line:
                loc += f":{f.line}"

            find_table.add_row(
                f.id,
                f"[{sev_color}]{f.severity.value.upper()}[/{sev_color}]",
                f.category.value,
                loc,
                f.message,
                "[OK]" if f.fixable else "-",
            )

        if len(report.findings) > 20:
            find_table.add_row("...", "", "", "", f"... and {len(report.findings) - 20} more", "")

        console.print(find_table)
    else:
        console.print("[bold green][OK] No issues detected! Clean frontend codebase.[/bold green]")

    if save:
        console.print(f"[bold green][OK][/bold green] Saved {len(report.findings)} findings to [dim]{state.fagent_dir / 'findings.json'}[/dim]")


@app.command()
def fix(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)"),
    safe_only: bool = typer.Option(True, "--safe-only/--all", help="Apply only safe non-breaking fixes"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Automatically accept patch proposals without prompt"),
    show_diff: bool = typer.Option(True, "--diff/--no-diff", help="Display patch diff previews"),
):
    """Safely apply verified patches to resolve fixable findings."""
    project_root = Path(target).resolve()
    if not project_root.exists():
        console.print(f"[bold red]Error:[/bold red] Target directory does not exist: {project_root}")
        raise typer.Exit(code=1)

    state = StateManager(project_root)
    findings_data = state.load_findings()
    findings = [Finding.model_validate(f) for f in findings_data]

    # If no stored findings, run audit first
    if not findings:
        console.print("[dim]No existing audit findings found. Running audit first...[/dim]")
        graph = state.load_graph()
        if not graph:
            scanner = ProjectScanner(project_root)
            graph = scanner.scan()
            state.save_graph(graph)
        audit_engine = AuditEngine(project_root)
        report = audit_engine.run_audit(graph)
        state.save_findings(report.findings)
        state.save_audit_report(report)
        findings = report.findings

    engine = PatchEngine(project_root)
    plan = engine.create_plan(findings)

    if not plan.patches:
        console.print("[bold green][OK] No fixable issues found! Project is clean.[/bold green]")
        return

    # Filter by risk level
    allowed_risks = [PatchRiskLevel.SAFE] if safe_only else [PatchRiskLevel.SAFE, PatchRiskLevel.REVIEW]
    target_patches = [p for p in plan.patches if p.risk_level in allowed_risks]

    console.print(
        Panel.fit(
            f"Found [bold]{plan.total_patches}[/bold] fixable issues:\n"
            f"- [green]{plan.safe_count} safe[/green] (automatic non-breaking fixes)\n"
            f"- [yellow]{plan.review_count} review required[/yellow] (component/design changes)\n"
            f"- [red]{plan.high_risk_count} high risk[/red]\n\n"
            f"Selected for application: [bold cyan]{len(target_patches)} patches[/bold cyan] (allowed: {', '.join(r.value for r in allowed_risks)})",
            title="FAgent Controlled Patch Engine",
            border_style="cyan"
        )
    )

    if not target_patches:
        console.print("[yellow]No patches match the selected risk threshold. Run with --all to include review-level fixes.[/yellow]")
        return

    # Display Diff Previews
    if show_diff:
        console.print("\n[bold]Proposed Patch Diffs:[/bold]")
        for idx, patch in enumerate(target_patches, start=1):
            console.print(f"\n[cyan]Patch {idx}/{len(target_patches)}: {patch.description}[/cyan] ([dim]{patch.file_path}[/dim])")
            if patch.diff:
                for line in patch.diff.splitlines():
                    if line.startswith("+") and not line.startswith("+++"):
                        console.print(f"[green]{line}[/green]")
                    elif line.startswith("-") and not line.startswith("---"):
                        console.print(f"[red]{line}[/red]")
                    else:
                        console.print(f"[dim]{line}[/dim]")

    # Confirmation Gate
    if not yes:
        confirm = typer.confirm(f"\nApply {len(target_patches)} patches with Git safety checkpoint?", default=True)
        if not confirm:
            console.print("[yellow]Patch application cancelled by user.[/yellow]")
            return

    with console.status("[bold cyan]Creating Git checkpoint and applying patches...", spinner="dots"):
        success, applied, msgs = engine.apply_plan_with_safety(plan, allowed_risks=allowed_risks)

    if success:
        console.print(f"\n[bold green][OK] Successfully applied and verified {len(applied)} patches![/bold green]")
        for m in msgs:
            console.print(f"  [green]✓[/green] {m}")
        console.print("[dim]Decision recorded in .fagent/decisions.json[/dim]")
    else:
        console.print(f"\n[bold red][FAILED] Patch application failed verification.[/bold red]")
        for m in msgs:
            console.print(f"  [red]✗[/red] {m}")


@app.command()
def verify(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)"),
    url: Optional[str] = typer.Option(None, "--url", help="Base URL of running frontend server (auto-detected if omitted)"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser in headless mode"),
    save: bool = typer.Option(True, "--save/--no-save", help="Persist findings to .fagent/ directory"),
):
    """Run Playwright browser verification across routes, viewports, overflow, and accessibility."""
    project_root = Path(target).resolve()
    if not project_root.exists():
        console.print(f"[bold red]Error:[/bold red] Target directory does not exist: {project_root}")
        raise typer.Exit(code=1)

    state = StateManager(project_root)
    graph = state.load_graph()
    if not graph:
        with console.status("[bold cyan]Scanning project graph first...", spinner="dots"):
            scanner = ProjectScanner(project_root)
            graph = scanner.scan()
            if save:
                state.save_graph(graph)

    with console.status("[bold cyan]Launching Playwright Chromium & crawling routes across viewports...", spinner="dots"):
        verifier = BrowserVerifier(project_root, headless=headless)
        findings, audit_data = verifier.run_browser_verification(graph, base_url=url)

    if audit_data.get("status") == "error":
        console.print(
            Panel.fit(
                f"[bold red]Dev server not detected![/bold red]\n\n"
                f"{audit_data.get('message')}\n\n"
                f"Example: start your application with [bold cyan]npm run dev[/bold cyan] in another terminal,\n"
                f"then run [bold cyan]fagent verify --url http://localhost:5173[/bold cyan].",
                title="Browser Verification",
                border_style="red"
            )
        )
        return

    # Display Verification Results
    console.print(
        Panel.fit(
            f"Inspected Base URL: [bold cyan]{audit_data.get('base_url')}[/bold cyan]\n"
            f"Routes Inspected: [bold]{len(audit_data.get('routes_inspected', {}))}[/bold]\n"
            f"Screenshots Captured: [bold]{audit_data.get('total_screenshots', 0)}[/bold]\n"
            f"Browser Findings: [bold]{len(findings)}[/bold]",
            title="Browser & Responsive Verification",
            border_style="green" if not findings else "yellow"
        )
    )

    if findings:
        table = Table(title="Runtime & Responsive Findings", box=box.SIMPLE_HEAVY)
        table.add_column("ID", style="bold cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Severity", style="bold")
        table.add_column("Route", style="green")
        table.add_column("Message", style="white")

        for f in findings:
            table.add_row(f.id, f.category.value, f.severity.value.upper(), f.route or "-", f.message)
        console.print(table)
    else:
        console.print("[bold green][OK] All viewports verified! Zero horizontal overflow or accessibility defects.[/bold green]")

    if save:
        console.print(f"[dim]Screenshots saved to: {state.fagent_dir / 'screenshots'}[/dim]")
        console.print(f"[dim]Audit metadata saved to: {state.fagent_dir / 'browser-audit.json'}[/dim]")


@app.command()
def memory(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)"),
    add: Optional[str] = typer.Option(None, "--add", help="Record a new project decision or pattern exception"),
    reason: Optional[str] = typer.Option(None, "--reason", help="Rationale for recorded decision"),
):
    """View or record project decisions, design rules, and approved exceptions."""
    project_root = Path(target).resolve()
    if not project_root.exists():
        console.print(f"[bold red]Error:[/bold red] Target directory does not exist: {project_root}")
        raise typer.Exit(code=1)

    mem = ProjectMemory(project_root)

    if add:
        entry = mem.record_decision(decision=add, reason=reason, source="cli-user")
        console.print(f"[bold green][OK] Decision recorded:[/bold green] {entry['decision']} ([dim]{entry['id']}[/dim])")
        return

    decisions = mem.get_decisions()
    if not decisions:
        console.print("[dim]No decisions recorded in project memory yet.[/dim]")
        return

    table = Table(title="Project Memory & Approved Decisions", box=box.ROUNDED)
    table.add_column("ID", style="bold cyan")
    table.add_column("Decision", style="white")
    table.add_column("Target File", style="dim")
    table.add_column("Reason", style="green")
    table.add_column("Source", style="dim blue")

    for d in decisions:
        table.add_row(
            d.get("id", "-"),
            d.get("decision", "-"),
            d.get("file") or "-",
            d.get("reason", "Approved"),
            d.get("source", "user"),
        )

    console.print(table)


@app.command()
def heal(
    target: str = typer.Argument(".", help="Target project root directory (default: current directory)"),
    max_iterations: int = typer.Option(5, "--max-iterations", "-m", help="Maximum autonomous healing loops"),
    allow_review: bool = typer.Option(False, "--allow-review", help="Allow applying REVIEW-level patches automatically"),
):
    """Run closed-loop autonomous healing: Audit -> Plan -> Patch -> Verify -> Iterate."""
    project_root = Path(target).resolve()
    if not project_root.exists():
        console.print(f"[bold red]Error:[/bold red] Target directory does not exist: {project_root}")
        raise typer.Exit(code=1)

    console.print(
        Panel.fit(
            f"Target: [bold cyan]{project_root.name}[/bold cyan]\n"
            f"Max Iterations: [bold]{max_iterations}[/bold]\n"
            f"Allowed Risk: [bold]{'SAFE + REVIEW' if allow_review else 'SAFE ONLY'}[/bold]\n\n"
            f"The agent will iteratively observe, plan, patch with Git checkpoints, and verify until convergence.",
            title="FAgent Autonomous Healing Loop",
            border_style="cyan"
        )
    )

    with console.status("[bold cyan]Executing autonomous healing loop...", spinner="dots"):
        loop = HealingLoop(project_root, max_iterations=max_iterations, allow_review=allow_review)
        result = loop.run()

    console.print(
        Panel.fit(
            f"Iterations Run: [bold]{result['iterations_run']}[/bold]\n"
            f"Total Fixes Applied: [bold green]{result['total_applied_fixes']}[/bold green]\n"
            f"Final Quality Score: [bold cyan]{result['final_score']}%[/bold cyan]\n"
            f"Remaining Findings: [bold]{result['final_findings_count']}[/bold]",
            title="Autonomous Healing Complete",
            border_style="green"
        )
    )

    if result.get("history"):
        hist_table = Table(title="Iteration Timeline", box=box.SIMPLE)
        hist_table.add_column("Iter", style="bold")
        hist_table.add_column("Score Before", style="dim")
        hist_table.add_column("Fixes Planned", justify="right")
        hist_table.add_column("Fixes Applied", justify="right", style="green")
        hist_table.add_column("Outcome", style="cyan")

        for h in result["history"]:
            hist_table.add_row(
                str(h["iteration"]),
                f"{h['score_before']}%",
                str(h["fixable_count"]),
                str(h["applied_count"]),
                h["status"],
            )
        console.print(hist_table)


if __name__ == "__main__":
    app()




