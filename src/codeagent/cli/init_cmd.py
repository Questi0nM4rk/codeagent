"""Project initialization command implementation."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

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
            console.print(
                "[yellow]⚠[/] .pre-commit-config.yaml exists"
                " (use --force to overwrite)",
            )
        else:
            config = assemble_config(detected, registry, templates_dir / "pre-commit")
            write_config(config, precommit_path)
            console.print("[green]✓[/] Generated .pre-commit-config.yaml")

    # Copy language configs (always, regardless of skip_precommit)
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

    # Scaffold .guardrails-exceptions.toml if not present
    exceptions_path = project_path / ".guardrails-exceptions.toml"
    if not exceptions_path.exists() or force:
        _scaffold_exceptions_file(exceptions_path)
        console.print("[green]\u2713[/] Created .guardrails-exceptions.toml")

    # Generate merged configs from registry + base templates
    if exceptions_path.exists():
        from codeagent.guardrails.generate import run_generate_configs

        run_generate_configs(project_dir=str(project_path))

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


_SCAFFOLD_TEMPLATE = """\
# =============================================================================
# .guardrails-exceptions.toml - Unified Exception Registry
# =============================================================================
# SINGLE SOURCE OF TRUTH for all lint/type/analysis exceptions in this project.
#
# DO NOT MODIFY unless you are the project owner.
# AI agents MUST NOT edit this file. Ask the project owner to add exceptions.
#
# Regenerate tool configs: codeagent generate-configs
# =============================================================================

schema_version = 1

[global.ruff]
# Formatter conflicts (always needed when using ruff format)
"W191"   = "formatter-conflict: tab-indentation"
"E111"   = "formatter-conflict: indentation-with-invalid-multiple"
"E114"   = "formatter-conflict: indentation-with-invalid-multiple-comment"
"E117"   = "formatter-conflict: over-indented"
"D206"   = "formatter-conflict: indent-with-spaces"
"D300"   = "formatter-conflict: triple-single-quotes"
"Q000"   = "formatter-conflict: bad-quotes-inline-string"
"Q001"   = "formatter-conflict: bad-quotes-multiline-string"
"Q002"   = "formatter-conflict: bad-quotes-docstring"
"Q003"   = "formatter-conflict: avoidable-escaped-quote"
"COM812" = "formatter-conflict: missing-trailing-comma"
"COM819" = "formatter-conflict: prohibited-trailing-comma"
"ISC001" = "formatter-conflict: single-line-implicit-string-concatenation"
"ISC002" = "formatter-conflict: multi-line-implicit-string-concatenation"

[global.codespell]
skip = [".git", "*.lock", "*.baseline", "node_modules", "venv", ".venv"]
ignore_words = []

# Add file_exceptions, inline_suppressions, and skip sections as needed.
# See: https://github.com/Questi0nM4rk/codeagent for documentation.
"""


def _scaffold_exceptions_file(path: Path) -> None:
    """Write a minimal .guardrails-exceptions.toml scaffold.

    Args:
        path: Where to write the file.

    """
    path.write_text(_SCAFFOLD_TEMPLATE)
