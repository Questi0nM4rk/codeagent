"""Shared fixtures for CodeAgent tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def python_project(temp_project: Path) -> Path:
    """Create a Python project with pyproject.toml."""
    (temp_project / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    (temp_project / "src").mkdir()
    (temp_project / "src" / "main.py").write_text("print('hello')\n")
    return temp_project


@pytest.fixture
def rust_project(temp_project: Path) -> Path:
    """Create a Rust project with Cargo.toml."""
    (temp_project / "Cargo.toml").write_text("[package]\nname = 'test'\n")
    (temp_project / "src").mkdir()
    (temp_project / "src" / "main.rs").write_text("fn main() {}\n")
    return temp_project


@pytest.fixture
def node_project(temp_project: Path) -> Path:
    """Create a Node.js project with package.json."""
    (temp_project / "package.json").write_text('{"name": "test"}\n')
    (temp_project / "src").mkdir()
    (temp_project / "src" / "index.ts").write_text("console.log('hello');\n")
    return temp_project


@pytest.fixture
def multi_language_project(temp_project: Path) -> Path:
    """Create a project with multiple languages."""
    (temp_project / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    (temp_project / "Cargo.toml").write_text("[package]\nname = 'test'\n")
    (temp_project / "scripts").mkdir()
    (temp_project / "scripts" / "build.sh").write_text("#!/bin/bash\n")
    return temp_project


@pytest.fixture
def sample_registry() -> dict:
    """Sample language registry for testing."""
    return {
        "python": {
            "name": "Python",
            "detect": {
                "files": ["pyproject.toml", "setup.py"],
                "patterns": ["*.py"],
            },
            "pre_commit_template": "python.yaml",
            "configs": ["ruff.toml"],
        },
        "rust": {
            "name": "Rust",
            "detect": {
                "files": ["Cargo.toml"],
                "patterns": ["*.rs"],
            },
            "pre_commit_template": "rust.yaml",
            "configs": ["rustfmt.toml"],
        },
        "node": {
            "name": "Node.js",
            "detect": {
                "files": ["package.json"],
                "patterns": ["*.ts", "*.tsx", "*.js", "*.jsx"],
            },
            "pre_commit_template": "node.yaml",
            "configs": ["biome.json"],
        },
        "shell": {
            "name": "Shell",
            "detect": {
                "patterns": ["*.sh", "*.bash"],
            },
            "pre_commit_template": "shell.yaml",
            "configs": [],
        },
    }
