"""Tests for codeagent init module."""

from __future__ import annotations

from pathlib import Path

import pytest

from codeagent.init.detector import detect_languages, load_registry


@pytest.fixture
def sample_registry(tmp_path: Path) -> dict:
    """Create a sample registry for testing."""
    registry_content = """
python:
  name: Python
  detect:
    files:
      - pyproject.toml
      - setup.py
    patterns:
      - "*.py"
    directories: []
  configs:
    - ruff.toml
  pre_commit_template: python.yaml

rust:
  name: Rust
  detect:
    files:
      - Cargo.toml
    patterns:
      - "*.rs"
    directories: []
  configs: []
  pre_commit_template: rust.yaml
"""
    registry_path = tmp_path / "languages.yaml"
    registry_path.write_text(registry_content)
    return load_registry(registry_path)


def test_load_registry(tmp_path: Path) -> None:
    """Test loading a valid registry."""
    registry_path = tmp_path / "test.yaml"
    registry_path.write_text("python:\n  name: Python\n")
    registry = load_registry(registry_path)
    assert "python" in registry
    assert registry["python"]["name"] == "Python"


def test_load_registry_invalid(tmp_path: Path) -> None:
    """Test loading an invalid registry raises TypeError."""
    registry_path = tmp_path / "invalid.yaml"
    registry_path.write_text("- item1\n- item2\n")
    with pytest.raises(TypeError, match="must be a dict"):
        load_registry(registry_path)


def test_detect_python_by_file(tmp_path: Path, sample_registry: dict) -> None:
    """Test detecting Python via pyproject.toml."""
    (tmp_path / "pyproject.toml").touch()
    detected = detect_languages(tmp_path, sample_registry)
    assert "python" in detected


def test_detect_python_by_pattern(tmp_path: Path, sample_registry: dict) -> None:
    """Test detecting Python via .py files."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").touch()
    detected = detect_languages(tmp_path, sample_registry)
    assert "python" in detected


def test_detect_rust(tmp_path: Path, sample_registry: dict) -> None:
    """Test detecting Rust via Cargo.toml."""
    (tmp_path / "Cargo.toml").touch()
    detected = detect_languages(tmp_path, sample_registry)
    assert "rust" in detected


def test_detect_multiple(tmp_path: Path, sample_registry: dict) -> None:
    """Test detecting multiple languages."""
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "Cargo.toml").touch()
    detected = detect_languages(tmp_path, sample_registry)
    assert "python" in detected
    assert "rust" in detected


def test_detect_none(tmp_path: Path, sample_registry: dict) -> None:
    """Test detecting no languages in empty directory."""
    detected = detect_languages(tmp_path, sample_registry)
    assert detected == []
