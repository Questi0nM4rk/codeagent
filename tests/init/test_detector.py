"""Tests for codeagent.init.detector module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import yaml

from codeagent.init.detector import detect_languages, load_registry

if TYPE_CHECKING:
    from pathlib import Path

    from codeagent.init.detector import LanguageRegistry


class TestLoadRegistry:
    """Tests for load_registry function."""

    def test_load_valid_registry(self, tmp_path: Path) -> None:
        """Test loading a valid YAML registry."""
        registry_path = tmp_path / "languages.yaml"
        registry_path.write_text("python:\n  name: Python\n")

        result = load_registry(registry_path)

        assert isinstance(result, dict)
        assert "python" in result
        assert result["python"]["name"] == "Python"

    def test_load_missing_registry(self, tmp_path: Path) -> None:
        """Test loading a non-existent registry raises FileNotFoundError."""
        registry_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_registry(registry_path)

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        """Test loading invalid YAML raises error."""
        registry_path = tmp_path / "invalid.yaml"
        registry_path.write_text("invalid: yaml: content:")

        with pytest.raises(yaml.YAMLError):
            load_registry(registry_path)

    def test_load_non_dict_registry(self, tmp_path: Path) -> None:
        """Test loading non-dict registry raises TypeError."""
        registry_path = tmp_path / "list.yaml"
        registry_path.write_text("- item1\n- item2\n")

        with pytest.raises(TypeError, match="Registry must be a dict"):
            load_registry(registry_path)


class TestDetectLanguages:
    """Tests for detect_languages function."""

    def test_detect_python_by_file(
        self, python_project: Path, sample_registry: LanguageRegistry
    ) -> None:
        """Test detecting Python by pyproject.toml presence."""
        result = detect_languages(python_project, sample_registry)

        assert "python" in result

    def test_detect_rust_by_file(
        self, rust_project: Path, sample_registry: LanguageRegistry
    ) -> None:
        """Test detecting Rust by Cargo.toml presence."""
        result = detect_languages(rust_project, sample_registry)

        assert "rust" in result

    def test_detect_node_by_file(
        self, node_project: Path, sample_registry: LanguageRegistry
    ) -> None:
        """Test detecting Node.js by package.json presence."""
        result = detect_languages(node_project, sample_registry)

        assert "node" in result

    def test_detect_shell_by_pattern(
        self, multi_language_project: Path, sample_registry: LanguageRegistry
    ) -> None:
        """Test detecting shell scripts by *.sh pattern."""
        result = detect_languages(multi_language_project, sample_registry)

        assert "shell" in result

    def test_detect_multiple_languages(
        self, multi_language_project: Path, sample_registry: LanguageRegistry
    ) -> None:
        """Test detecting multiple languages in one project."""
        result = detect_languages(multi_language_project, sample_registry)

        assert "python" in result
        assert "rust" in result
        assert "shell" in result

    def test_detect_no_languages(
        self, temp_project: Path, sample_registry: LanguageRegistry
    ) -> None:
        """Test empty project returns empty list."""
        result = detect_languages(temp_project, sample_registry)

        assert result == []

    def test_detect_by_nested_pattern(
        self, tmp_path: Path, sample_registry: LanguageRegistry
    ) -> None:
        """Test detecting by recursive file pattern."""
        project = tmp_path / "nested"
        project.mkdir()
        (project / "deep" / "nested" / "dir").mkdir(parents=True)
        (project / "deep" / "nested" / "dir" / "script.sh").write_text("#!/bin/bash\n")

        result = detect_languages(project, sample_registry)

        assert "shell" in result

    def test_detect_by_directory_rule(self, tmp_path: Path) -> None:
        """Test detecting by directory presence rule."""
        project = tmp_path / "dir-project"
        project.mkdir()
        (project / "vendor").mkdir()
        registry: LanguageRegistry = {
            "vendorlang": {"detect": {"directories": ["vendor"]}},
        }

        result = detect_languages(project, registry)

        assert "vendorlang" in result

    def test_directory_rule_not_triggered_for_file(self, tmp_path: Path) -> None:
        """Test directory rule doesn't match files with same name."""
        project = tmp_path / "file-project"
        project.mkdir()
        (project / "vendor").write_text("not a directory")  # File, not dir
        registry: LanguageRegistry = {
            "vendorlang": {"detect": {"directories": ["vendor"]}},
        }

        result = detect_languages(project, registry)

        assert "vendorlang" not in result
