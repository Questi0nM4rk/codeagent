"""CodeAgent CLI entry point."""

from __future__ import annotations

from rich.console import Console
import typer

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
        raise typer.Exit


@app.callback()
def main(
    _version: bool = typer.Option(
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
    project_dir: str = typer.Argument(
        ".",
        help="Project directory to initialize",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configs",
    ),
    no_precommit: bool = typer.Option(
        False,
        "--no-precommit",
        help="Skip pre-commit setup",
    ),
    no_coderabbit: bool = typer.Option(
        False,
        "--no-coderabbit",
        help="Skip CodeRabbit setup",
    ),
    no_workflow: bool = typer.Option(
        False,
        "--no-workflow",
        help="Skip GitHub workflow setup",
    ),
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


@app.command("generate-configs")
def generate_configs(
    project_dir: str = typer.Argument(
        ".",
        help="Project directory containing .guardrails-exceptions.toml",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Validate registry only, don't write files",
    ),
) -> None:
    """Generate tool configs from .guardrails-exceptions.toml."""
    from codeagent.guardrails.generate import run_generate_configs

    success = run_generate_configs(project_dir=project_dir, dry_run=dry_run)
    if not success:
        raise typer.Exit(code=1)


@app.command()
def start() -> None:
    """Start CodeAgent services (SurrealDB)."""
    # TODO(Epic 5): Implement SurrealDB startup via docker compose
    console.print("[yellow]Not implemented yet[/]")


@app.command()
def stop() -> None:
    """Stop CodeAgent services."""
    # TODO(Epic 5): Implement service shutdown via docker compose
    console.print("[yellow]Not implemented yet[/]")


@app.command()
def status() -> None:
    """Show CodeAgent service status."""
    # TODO(Epic 5): Implement health check for SurrealDB
    console.print("[yellow]Not implemented yet[/]")


if __name__ == "__main__":
    app()
