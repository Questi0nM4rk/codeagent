"""Language detection for projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_registry(registry_path: Path) -> dict[str, Any]:
    """Load language registry from YAML file.

    Args:
        registry_path: Path to languages.yaml

    Returns:
        Dictionary of language configurations

    Raises:
        FileNotFoundError: If registry file doesn't exist
        yaml.YAMLError: If registry file is invalid YAML
        TypeError: If registry is not a dict

    """
    with registry_path.open() as f:
        result = yaml.safe_load(f)
    if not isinstance(result, dict):
        msg = f"Registry must be a dict, got {type(result).__name__}"
        raise TypeError(msg)
    return result


def detect_languages(project_dir: Path, registry: dict[str, Any]) -> list[str]:
    """Detect languages present in project based on registry rules.

    Detection rules are evaluated in order:
    1. Check for specific files (exact match)
    2. Check for file patterns (glob match)
    3. Check for directories

    Args:
        project_dir: Path to project directory
        registry: Language registry from languages.yaml

    Returns:
        List of detected language keys (e.g., ["python", "go"])

    """
    detected: list[str] = []

    for lang, config in registry.items():
        rules = config.get("detect", {})

        # Check for specific files
        files = rules.get("files", [])
        if any((project_dir / f).exists() for f in files):
            detected.append(lang)
            continue

        # Check for file patterns (recursive search)
        patterns = rules.get("patterns", [])
        for pattern in patterns:
            recursive_pattern = f"**/{pattern}"
            if any(project_dir.glob(recursive_pattern)):
                detected.append(lang)
                break
        else:
            # Check for directories
            directories = rules.get("directories", [])
            if any((project_dir / d).is_dir() for d in directories):
                detected.append(lang)

    return detected
