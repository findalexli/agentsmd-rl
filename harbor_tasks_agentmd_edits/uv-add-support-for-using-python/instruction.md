# Add Python 3.6 Interpreter Support

## Problem

uv's vendored `packaging` modules (used by the interpreter discovery script) rely on `from __future__ import annotations` and use PEP 604 union syntax (`str | None`) and PEP 585 lowercase generics (`tuple[int, ...]`). These features are not available on Python 3.6, so uv fails when it encounters a Python 3.6 interpreter on the system.

The interpreter info script in `crates/uv-python/python/get_interpreter_info.py` also rejects Python versions below 3.7, when 3.6 should be supported.

## Expected Behavior

1. The vendored packaging modules under `crates/uv-python/python/packaging/` should be compatible with Python 3.6. This means removing `from __future__ import annotations` and quoting any type annotations that use syntax not available in Python 3.6.

2. The version floor check in `get_interpreter_info.py` should be lowered to 3.6.

3. A reapplicable patch file should be created in the packaging directory so that these compatibility changes can be reapplied when the vendored code is updated.

4. After making the code changes, update the relevant documentation in the packaging directory to reflect the patches that have been applied to the vendored code.

## Files to Look At

- `crates/uv-python/python/packaging/_elffile.py` — vendored ELF file parser, uses `from __future__ import annotations`
- `crates/uv-python/python/packaging/_manylinux.py` — vendored manylinux tag detection, uses `from __future__ import annotations`
- `crates/uv-python/python/packaging/_musllinux.py` — vendored musllinux tag detection, uses `from __future__ import annotations`
- `crates/uv-python/python/get_interpreter_info.py` — interpreter info collection script with version floor check
- `crates/uv-python/python/packaging/README.md` — documents the vendored packaging modules and any modifications
