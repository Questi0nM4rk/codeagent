"""CodeAgent CLI entry point."""

from __future__ import annotations

import typer
from rich.console import Console

from codeagent import __version__

app = typer.Typer(
    name="codeagent",
    help="Accuracy-optimized AI coding framework",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"codeagent {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """CodeAgent - Accuracy-optimized AI coding framework."""


@app.command()
def init(
    project_dir: str = typer.Argument(".", help="Project directory to initialize"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing configs"),
    no_precommit: bool = typer.Option(False, "--no-precommit", help="Skip pre-commit setup"),
    no_coderabbit: bool = typer.Option(False, "--no-coderabbit", help="Skip CodeRabbit setup"),
    no_workflow: bool = typer.Option(False, "--no-workflow", help="Skip GitHub workflow setup"),
) -> None:
    """Initialize a project with CodeAgent configuration."""
    from codeagent.cli.init_cmd import run_init

    run_init(
        project_dir=project_dir,
        force=force,
        skip_precommit=no_precommit,
        skip_coderabbit=no_coderabbit,
        skip_workflow=no_workflow,
    )


@app.command()
def start() -> None:
    """Start CodeAgent services (SurrealDB)."""
    console.print("[yellow]Not implemented yet[/]")


@app.command()
def stop() -> None:
    """Stop CodeAgent services."""
    console.print("[yellow]Not implemented yet[/]")


@app.command()
def status() -> None:
    """Show CodeAgent service status."""
    console.print("[yellow]Not implemented yet[/]")


if __name__ == "__main__":
    app()
