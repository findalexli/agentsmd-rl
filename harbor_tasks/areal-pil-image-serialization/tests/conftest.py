"""Mock heavy dependencies and pre-register areal package hierarchy.

The areal package's __init__.py imports controllers, launchers, etc. which pull
in aiohttp, ray, sglang, vllm — none of which are installed.  We pre-register
the package namespace so Python skips __init__.py, then mock torch and colorlog
so serialization.py can import cleanly.
"""

import sys
import types

# --- Pre-register areal package hierarchy (skips __init__.py imports) ---
for pkg, path in [
    ("areal", "/workspace/AReaL/areal"),
    ("areal.infra", "/workspace/AReaL/areal/infra"),
    ("areal.infra.rpc", "/workspace/AReaL/areal/infra/rpc"),
    ("areal.utils", "/workspace/AReaL/areal/utils"),
]:
    if pkg not in sys.modules:
        m = types.ModuleType(pkg)
        m.__path__ = [path]
        m.__package__ = pkg
        sys.modules[pkg] = m

# --- Mock torch (serialization.py: `import torch`) ---
if "torch" not in sys.modules:
    _torch = types.ModuleType("torch")
    _torch.Tensor = type("Tensor", (), {})
    _torch.dtype = type("dtype", (), {})
    _torch.from_numpy = lambda x: x
    _torch.tensor = lambda *a, **kw: None
    _torch.float32 = "float32"
    _torch.float64 = "float64"
    _torch.int32 = "int32"
    _torch.int64 = "int64"
    _torch.bool = "bool"
    sys.modules["torch"] = _torch

# --- Mock colorlog (areal.utils.logging imports it) ---
for mod_name in ("colorlog", "colorlog.escape_codes", "colorlog.formatter"):
    if mod_name not in sys.modules:
        _m = types.ModuleType(mod_name)
        if mod_name == "colorlog":
            _m.ColoredFormatter = type(
                "ColoredFormatter",
                (),
                {"__init__": lambda self, *a, **kw: None},
            )
            _m.escape_codes = types.ModuleType("colorlog.escape_codes")
            _m.formatter = types.ModuleType("colorlog.formatter")
        sys.modules[mod_name] = _m
