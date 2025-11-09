from __future__ import annotations
from types import SimpleNamespace
from typing import Any, Optional
import os

class _Cfg(SimpleNamespace):
    """Dict-like + attribute access (provides .get for legacy code)."""
    def get(self, key: str, default: Optional[Any] = None):
        return getattr(self, key, default)

def _load_memory_config() -> _Cfg:
    """
    Minimal replacement for the original memory config loader.
    We expose an 'enabled' flag and keep room for future options.
    """
    enabled = os.getenv("SRE_MEMORY_ENABLED", "true").lower() != "false"
    return _Cfg(
        enabled=enabled,
        # Add more knobs here if supervisor ever reads them:
        # e.g., preferences_ttl_days=90, infrastructure_ttl_days=30, investigation_ttl_days=60
    )
