from __future__ import annotations
import importlib
from typing import Any

def load_entrypoint(entrypoint: str) -> Any:
    mod_path, symbol = entrypoint.split(":")
    module = importlib.import_module(mod_path)
    return getattr(module, symbol)
