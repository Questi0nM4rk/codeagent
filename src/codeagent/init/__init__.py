"""Project initialization for CodeAgent."""

from __future__ import annotations

from codeagent.init.detector import detect_languages, load_registry
from codeagent.init.precommit import assemble_config, write_config

__all__ = [
    "assemble_config",
    "detect_languages",
    "load_registry",
    "write_config",
]
