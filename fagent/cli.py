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
from fagent.scanner.project import ProjectScanner
from fagent.schemas.finding import Severity
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


if __name__ == "__main__":
    app()

