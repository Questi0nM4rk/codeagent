"""Orchestrate config generation from .guardrails-exceptions.toml."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from codeagent.core.paths import get_configs_dir
from codeagent.guardrails.generators.allowlist import generate_allowlist
from codeagent.guardrails.generators.biome import generate_biome
from codeagent.guardrails.generators.codespell import generate_codespell
from codeagent.guardrails.generators.markdownlint import generate_markdownlint
from codeagent.guardrails.generators.pyright import generate_pyright
from codeagent.guardrails.generators.ruff import generate_ruff
from codeagent.guardrails.registry import ExceptionRegistry

console = Console()

REGISTRY_FILENAME = ".guardrails-exceptions.toml"


def run_generate_configs(
    project_dir: str = ".",
    dry_run: bool = False,
) -> bool:
    """Generate tool configs from the exception registry.

    Args:
        project_dir: Path to project root.
        dry_run: If True, validate only, don't write files.

    Returns:
        True if generation succeeded.

    """
    project_path = Path(project_dir).resolve()
    registry_path = project_path / REGISTRY_FILENAME

    if not registry_path.exists():
        console.print(
            f"[red]Error: {REGISTRY_FILENAME} not found in {project_path}[/]",
        )
        console.print("Run 'codeagent init' to scaffold one.")
        return False

    # Load and validate
    registry = ExceptionRegistry.load(registry_path)
    errors = registry.validate()
    if errors:
        console.print(f"[red]Validation errors in {REGISTRY_FILENAME}:[/]")
        for err in errors:
            console.print(f"  - {err}")
        return False

    if dry_run:
        console.print("[green]Registry is valid.[/]")
        return True

    # Look for base templates: project's configs/ first, then global
    local_configs = project_path / "configs"
    global_configs = get_configs_dir()

    def _find_base(name: str) -> Path | None:
        for d in [local_configs, global_configs]:
            p = d / name
            if p.exists():
                return p
        return None

    # Generate ruff.toml
    base_ruff = _find_base("ruff.toml")
    if base_ruff:
        generate_ruff(registry, base_ruff, project_path / "ruff.toml")
        console.print("[green]\u2713[/] Generated ruff.toml")

    # Generate biome.json
    base_biome = _find_base("biome.json")
    if base_biome:
        generate_biome(registry, base_biome, project_path / "biome.json")
        console.print("[green]\u2713[/] Generated biome.json")

    # Generate .markdownlint.jsonc
    base_mdlint = _find_base(".markdownlint.jsonc")
    if base_mdlint:
        generate_markdownlint(
            registry,
            base_mdlint,
            project_path / ".markdownlint.jsonc",
        )
        console.print("[green]\u2713[/] Generated .markdownlint.jsonc")

    # Generate .codespellrc
    if registry.global_rules.get("codespell"):
        generate_codespell(registry, project_path / ".codespellrc")
        console.print("[green]\u2713[/] Generated .codespellrc")

    # Generate .suppression-allowlist
    if registry.inline_suppressions:
        generate_allowlist(registry, project_path / ".suppression-allowlist")
        console.print("[green]\u2713[/] Generated .suppression-allowlist")

    # Merge pyright into pyproject.toml
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists() and registry.global_rules.get("pyright"):
        generate_pyright(registry, pyproject)
        console.print("[green]\u2713[/] Updated pyproject.toml [tool.pyright]")

    console.print(
        f"\n[bold green]Configs generated from {REGISTRY_FILENAME}[/]",
    )
    return True
