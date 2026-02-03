"""Project initialization command implementation."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rich.console import Console

from codeagent.core.paths import get_configs_dir, get_templates_dir
from codeagent.init.detector import detect_languages, load_registry
from codeagent.init.precommit import assemble_config, write_config

console = Console()


def run_init(
    project_dir: str,
    force: bool = False,
    skip_precommit: bool = False,
    skip_coderabbit: bool = False,
    skip_workflow: bool = False,
) -> None:
    """Initialize a project with CodeAgent configuration.

    Args:
        project_dir: Path to project directory
        force: Overwrite existing configs
        skip_precommit: Skip pre-commit setup
        skip_coderabbit: Skip CodeRabbit setup
        skip_workflow: Skip GitHub workflow setup

    """
    project_path = Path(project_dir).resolve()

    # Validate project path exists and is a directory
    if not project_path.exists():
        console.print(f"[red]Error: Directory does not exist: {project_path}[/]")
        return
    if not project_path.is_dir():
        console.print(f"[red]Error: Path is not a directory: {project_path}[/]")
        return

    console.print(f"[bold blue]Initializing CodeAgent in {project_path}[/]")

    configs_dir = get_configs_dir()
    templates_dir = get_templates_dir()

    # Load language registry
    registry_path = configs_dir / "languages.yaml"
    if not registry_path.exists():
        console.print(f"[red]Error: Registry not found at {registry_path}[/]")
        console.print("Run 'codeagent install' first or check your installation.")
        return

    registry = load_registry(registry_path)

    # Detect languages
    detected = detect_languages(project_path, registry)
    if detected:
        console.print(f"Detected languages: {', '.join(detected)}")
    else:
        console.print("[yellow]No languages detected, using base config only[/]")

    # Generate pre-commit config
    if not skip_precommit:
        precommit_path = project_path / ".pre-commit-config.yaml"
        if precommit_path.exists() and not force:
            console.print("[yellow]⚠[/] .pre-commit-config.yaml exists (use --force to overwrite)")
        else:
            config = assemble_config(detected, registry, templates_dir / "pre-commit")
            write_config(config, precommit_path)
            console.print("[green]✓[/] Generated .pre-commit-config.yaml")

        # Copy language configs
        for lang in detected:
            for config_file in registry.get(lang, {}).get("configs", []):
                src = configs_dir / config_file
                dst = project_path / config_file
                if src.exists() and (not dst.exists() or force):
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(src, dst)
                    console.print(f"[green]✓[/] Copied {config_file}")

    # Setup CodeRabbit
    if not skip_coderabbit:
        coderabbit_src = templates_dir / ".coderabbit.yaml"
        coderabbit_dst = project_path / ".coderabbit.yaml"
        if coderabbit_src.exists() and (not coderabbit_dst.exists() or force):
            shutil.copy(coderabbit_src, coderabbit_dst)
            console.print("[green]✓[/] Created .coderabbit.yaml")

    # Setup GitHub workflow
    if not skip_workflow:
        workflow_src = templates_dir / "workflows" / "claude-review.yaml"
        workflow_dir = project_path / ".github" / "workflows"
        workflow_dst = workflow_dir / "claude-review.yaml"
        if workflow_src.exists() and (not workflow_dst.exists() or force):
            workflow_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(workflow_src, workflow_dst)
            console.print("[green]✓[/] Created .github/workflows/claude-review.yaml")

    # Create .claude/ structure
    claude_dir = project_path / ".claude"
    claude_dir.mkdir(exist_ok=True)
    project_info = claude_dir / "project-info"
    if not project_info.exists() or force:
        project_info.write_text(f"project_name: {project_path.name}\n")
        console.print("[green]✓[/] Created .claude/project-info")

    # Create docs/decisions/ for ADRs
    decisions_dir = project_path / "docs" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    # Install pre-commit hooks (resolve absolute path to mitigate PATH hijacking)
    if not skip_precommit:
        precommit_bin = shutil.which("pre-commit")
        if precommit_bin:
            result = subprocess.run(
                [precommit_bin, "install"],
                cwd=project_path,
                check=False,
                capture_output=True,
            )
            if result.returncode == 0:
                console.print("[green]✓[/] Installed pre-commit hooks")
            else:
                console.print("[yellow]⚠[/] Failed to install pre-commit hooks")
        else:
            console.print("[yellow]⚠[/] pre-commit not found, skipping hook install")

    # Initialize secrets baseline (resolve absolute path to mitigate PATH hijacking)
    detect_secrets_bin = shutil.which("detect-secrets")
    if detect_secrets_bin:
        result = subprocess.run(
            [detect_secrets_bin, "scan", "--baseline", ".secrets.baseline"],
            cwd=project_path,
            check=False,
            capture_output=True,
        )
        if result.returncode == 0:
            console.print("[green]✓[/] Initialized secrets baseline")

    console.print("\n[bold green]CodeAgent initialized successfully![/]")
