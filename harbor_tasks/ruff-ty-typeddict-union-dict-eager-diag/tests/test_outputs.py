"""
Task: ruff-ty-typeddict-union-dict-eager-diag
Repo: astral-sh/ruff @ 6cff03427e386e38dc2ead0cc7718a71bfa288f8
PR:   24151

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import tempfile
from pathlib import Path

REPO = "/repo"
BUILDER_FILE = f"{REPO}/crates/ty_python_semantic/src/types/infer/builder.rs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_ty():
    """Compile the ty binary. Returns path to binary or raises on failure."""
    ty_bin = Path(REPO) / "target" / "debug" / "ty"
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        timeout=480,
        env={
            **__import__("os").environ,
            "CARGO_PROFILE_DEV_OPT_LEVEL": "1",
        },
    )
    assert r.returncode == 0, (
        f"cargo build failed:\n{r.stderr.decode()[-2000:]}"
    )
    return str(ty_bin)


def _ty_check(ty_bin: str, code: str) -> str:
    """Write code to a temp file, run ty check, return combined output."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            [ty_bin, "check", f.name],
            capture_output=True,
            timeout=120,
        )
    return r.stdout.decode() + r.stderr.decode()


# Cache the build across tests
_ty_bin_cache = None


def _get_ty():
    global _ty_bin_cache
    if _ty_bin_cache is None:
        _ty_bin_cache = _build_ty()
    return _ty_bin_cache


# ---------------------------------------------------------------------------
# Gate (static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """Modified Rust code must compile successfully."""
    _get_ty()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_union_dict_no_false_positive():
    """TypedDict | dict[str, Any] union must not emit false-positive diagnostics for dict literals."""
    ty = _get_ty()
    output = _ty_check(ty, """\
from typing import TypedDict, Any

class FormatterConfig(TypedDict, total=False):
    format: str

def takes_formatter(config: FormatterConfig | dict[str, Any]) -> None: ...

# Matches TypedDict arm
takes_formatter({"format": "%(message)s"})
# Matches dict[str, Any] arm — extra keys not in TypedDict
takes_formatter({"factory": object(), "facility": "local0"})
# Matches dict[str, Any] arm — completely unrelated keys
takes_formatter({"debug": True, "verbose": False, "timeout": 30})
""")
    assert not re.search(r"missing-typed-dict-key|invalid-key", output), (
        f"False positive TypedDict diagnostic emitted:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_union_dict_var_assignment():
    """TypedDict | dict[str, int] via variable assignment must not emit false positives."""
    ty = _get_ty()
    output = _ty_check(ty, """\
from typing import TypedDict

class ServerConfig(TypedDict):
    host: str
    port: int

# dict[str, int] arm accepts arbitrary string keys with int values
settings: ServerConfig | dict[str, int] = {"timeout": 30, "retries": 3}

class DBConfig(TypedDict):
    name: str

# dict[str, str] arm accepts any string-keyed dict
db: DBConfig | dict[str, str] = {"driver": "postgres", "charset": "utf8"}
""")
    assert not re.search(r"missing-typed-dict-key|invalid-key", output), (
        f"False positive TypedDict diagnostic for dict fallback arm:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_union_dict_triple_union():
    """TypedDict | dict[str, str] | None must not emit false-positive for dict arm."""
    ty = _get_ty()
    output = _ty_check(ty, """\
from typing import TypedDict

class LogConfig(TypedDict, total=False):
    level: str
    file: str

# Triple union: TypedDict | dict | None — dict arm should suppress TypedDict diagnostics
cfg: LogConfig | dict[str, str] | None = {"custom_key": "value", "another": "data"}
""")
    assert not re.search(r"missing-typed-dict-key|invalid-key", output), (
        f"False positive TypedDict diagnostic for triple union:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_fallback_still_validates():
    """TypedDict | None (no dict fallback) must still emit eager diagnostics."""
    ty = _get_ty()
    output = _ty_check(ty, """\
from typing import TypedDict

class Foo(TypedDict):
    foo: int

x: Foo | None = {"bar": 1}
""")
    assert "missing-typed-dict-key" in output, (
        f"Expected missing-typed-dict-key for Foo | None:\n{output}"
    )
    assert "invalid-key" in output, (
        f"Expected invalid-key for Foo | None:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_single_typeddict_validates():
    """Single TypedDict annotation (no union) must still validate missing keys."""
    ty = _get_ty()
    output = _ty_check(ty, """\
from typing import TypedDict

class Config(TypedDict):
    host: str
    port: int

def use_config(c: Config) -> None: ...

use_config({"host": "localhost"})
""")
    assert "missing-typed-dict-key" in output, (
        f"Expected missing-typed-dict-key for single TypedDict:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_typeddict_valid_usage_no_error():
    """Correct TypedDict usage (all required keys present) produces no diagnostics."""
    ty = _get_ty()
    output = _ty_check(ty, """\
from typing import TypedDict

class Movie(TypedDict):
    name: str
    year: int

m1: Movie = {"name": "Blade Runner", "year": 1982}
m2: Movie = {"name": "Alien", "year": 1979}
m3: Movie = {"name": "2001", "year": 1968}
""")
    assert not re.search(r"error\[", output), (
        f"Unexpected error for valid TypedDict usage:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:79 @ 6cff034
def test_no_fragile_expect():
    """No fragile .expect('filtered out...') calls in builder.rs."""
    content = Path(BUILDER_FILE).read_text()
    matches = re.findall(r'\.expect\("filtered out', content)
    assert len(matches) == 0, (
        f"Found {len(matches)} fragile .expect('filtered out...') call(s) in builder.rs"
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 6cff034
def test_no_local_imports():
    """Rust use-imports must be at top of file, not inside function bodies (8+ spaces indent)."""
    content = Path(BUILDER_FILE).read_text()
    local_imports = [
        line for line in content.splitlines()
        if re.match(r"^\s{8,}use\s+", line) and "//" not in line
    ]
    assert len(local_imports) == 0, (
        f"Found {len(local_imports)} local import(s) in builder.rs:\n"
        + "\n".join(local_imports[:5])
    )
