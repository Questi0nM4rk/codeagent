"""Path constants and utilities for CodeAgent."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache
def get_codeagent_dir() -> Path:
    """Get the CodeAgent installation directory (~/.codeagent/)."""
    return Path.home() / ".codeagent"


@lru_cache
def get_package_dir() -> Path:
    """Get the package root directory for development fallback.

    This is used ONLY as a fallback when the global install directory
    (~/.codeagent/) doesn't contain the requested resources. In production,
    resources are installed to ~/.codeagent/ by the install script.

    For development, searches upward to find pyproject.toml. Falls back to
    parents[1] if pyproject.toml not found (installed environment).
    """
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    # In installed environments, return package root (parents[1] from this file)
    # This won't have bundled resources, but global path should be primary
    return Path(__file__).resolve().parents[1]


@lru_cache
def get_configs_dir() -> Path:
    """Get configs directory (global install or package fallback)."""
    global_configs = get_codeagent_dir() / "configs"
    if global_configs.exists():
        return global_configs
    return get_package_dir() / "configs"


@lru_cache
def get_templates_dir() -> Path:
    """Get templates directory (global install or package fallback)."""
    global_templates = get_codeagent_dir() / "templates"
    if global_templates.exists():
        return global_templates
    return get_package_dir() / "templates"


@lru_cache
def get_data_dir() -> Path:
    """Get data directory for persistent storage (~/.codeagent/data/)."""
    data_dir = get_codeagent_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_skills_dir() -> Path:
    """Get skills directory (global install or package fallback)."""
    global_skills = get_codeagent_dir() / "skills"
    if global_skills.exists():
        return global_skills
    return get_package_dir() / "skills"


def get_hooks_dir() -> Path:
    """Get hooks directory (global install or package fallback)."""
    global_hooks = get_codeagent_dir() / "hooks"
    if global_hooks.exists():
        return global_hooks
    return get_package_dir() / "hooks"
