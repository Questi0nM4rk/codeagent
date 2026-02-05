"""Tests for codeagent.init.precommit module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import yaml

from codeagent.init.precommit import (
    assemble_config,
    load_template,
    write_config,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestLoadTemplate:
    """Tests for load_template function."""

    def test_load_valid_template(self, tmp_path: Path) -> None:
        """Test loading a valid YAML template."""
        template_path = tmp_path / "template.yaml"
        template_path.write_text("repos:\n  - repo: test\n")

        result = load_template(template_path)

        assert isinstance(result, dict)
        assert "repos" in result

    def test_load_missing_template(self, tmp_path: Path) -> None:
        """Test loading missing template raises FileNotFoundError."""
        template_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_template(template_path)

    def test_load_non_dict_template(self, tmp_path: Path) -> None:
        """Test loading non-dict template raises TypeError."""
        template_path = tmp_path / "list.yaml"
        template_path.write_text("- item1\n- item2\n")

        with pytest.raises(TypeError, match="Template must be a dict"):
            load_template(template_path)


class TestAssembleConfig:
    """Tests for assemble_config function."""

    @pytest.fixture
    def templates_dir(self, tmp_path: Path) -> Path:
        """Create templates directory with base and language templates."""
        templates = tmp_path / "templates"
        templates.mkdir()

        # Base template
        (templates / "base.yaml").write_text(
            "repos:\n"
            "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
            "    rev: v4.0.0\n"
            "    hooks:\n"
            "      - id: trailing-whitespace\n"
        )

        # Python template
        (templates / "python.yaml").write_text(
            "repos:\n"
            "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
            "    rev: v0.1.0\n"
            "    hooks:\n"
            "      - id: ruff\n"
        )

        # Rust template
        (templates / "rust.yaml").write_text(
            "repos:\n" "  - repo: local\n" "    hooks:\n" "      - id: cargo-fmt\n"
        )

        return templates

    def test_assemble_base_only(self, templates_dir: Path, sample_registry: dict) -> None:
        """Test assembling config with no languages uses base only."""
        result = assemble_config([], sample_registry, templates_dir)

        assert "repos" in result
        assert len(result["repos"]) == 1
        assert "pre-commit-hooks" in result["repos"][0]["repo"]

    def test_assemble_with_python(self, templates_dir: Path, sample_registry: dict) -> None:
        """Test assembling config includes Python template."""
        result = assemble_config(["python"], sample_registry, templates_dir)

        assert len(result["repos"]) == 2
        repos = [r["repo"] for r in result["repos"]]
        assert any("ruff" in r for r in repos)

    def test_assemble_multiple_languages(self, templates_dir: Path, sample_registry: dict) -> None:
        """Test assembling config with multiple languages."""
        result = assemble_config(["python", "rust"], sample_registry, templates_dir)

        assert len(result["repos"]) == 3

    def test_assemble_missing_template_warns(
        self, templates_dir: Path, sample_registry: dict, capsys: pytest.CaptureFixture
    ) -> None:
        """Test missing language template prints warning but continues."""
        # node template doesn't exist
        result = assemble_config(["node"], sample_registry, templates_dir)

        # Should still have base
        assert len(result["repos"]) == 1

        # Should warn about missing template
        captured = capsys.readouterr()
        assert "Warning" in captured.err


class TestWriteConfig:
    """Tests for write_config function."""

    def test_write_config_creates_file(self, tmp_path: Path) -> None:
        """Test write_config creates output file."""
        output_path = tmp_path / ".pre-commit-config.yaml"
        config = {"repos": [{"repo": "test"}]}

        write_config(config, output_path)

        assert output_path.exists()

    def test_write_config_has_header(self, tmp_path: Path) -> None:
        """Test written config has CodeAgent header."""
        output_path = tmp_path / ".pre-commit-config.yaml"
        config = {"repos": []}

        write_config(config, output_path)

        content = output_path.read_text()
        assert "CodeAgent" in content
        assert "Auto-Generated" in content

    def test_write_config_valid_yaml(self, tmp_path: Path) -> None:
        """Test written config is valid YAML."""
        output_path = tmp_path / ".pre-commit-config.yaml"
        config = {"repos": [{"repo": "test", "hooks": [{"id": "test-hook"}]}]}

        write_config(config, output_path)

        # Should be parseable YAML (skip header lines starting with #)
        content = output_path.read_text()
        yaml_content = "\n".join(line for line in content.split("\n") if not line.startswith("#"))
        parsed = yaml.safe_load(yaml_content)
        assert parsed["repos"][0]["repo"] == "test"

    def test_write_config_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Test write_config creates parent directories."""
        output_path = tmp_path / "deep" / "nested" / ".pre-commit-config.yaml"
        config = {"repos": []}

        write_config(config, output_path)

        assert output_path.exists()

    def test_write_config_multiline_strings(self, tmp_path: Path) -> None:
        """Test multiline strings use block style."""
        output_path = tmp_path / ".pre-commit-config.yaml"
        config = {
            "repos": [
                {"repo": "test", "hooks": [{"id": "test", "entry": "echo 'line1'\necho 'line2'"}]}
            ]
        }

        write_config(config, output_path)

        content = output_path.read_text()
        # Block style uses | indicator and preserves multiline content
        assert "entry: |" in content, "Multiline strings should use block style (|)"
        assert "echo 'line1'" in content, "First line of multiline content should be preserved"
        assert "echo 'line2'" in content, "Second line of multiline content should be preserved"
