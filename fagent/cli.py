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
from fagent.scanner.project import ProjectScanner
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


if __name__ == "__main__":
    app()
