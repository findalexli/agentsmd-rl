"""
Task: ruff-ty-dataclass-transform-kwargs
Repo: astral-sh/ruff @ 32f644c3bfa09271cc54ca04f7259fbf8a99b81f
PR:   24170

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

REPO = "/repo"
TY = "ty"


def run_ty(code: str) -> str:
    """Write code to a temp file and run ty check on it."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            [TY, "check", f.name],
            capture_output=True, text=True, timeout=120,
            cwd=REPO,
        )
        return r.stdout + r.stderr


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """Rust code must compile (cargo check --bin ty)."""
    r = subprocess.run(
        ["cargo", "check", "--bin", "ty"],
        capture_output=True, text=True, timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_func_transformer_kwargs_frozen():
    """Function-based transformer with **kwargs respects frozen=True."""
    output = run_ty("""\
from typing import dataclass_transform, Callable

@dataclass_transform()
def create_model[T: type](**kwargs) -> Callable[[T], T]:
    raise NotImplementedError

@create_model(frozen=True)
class Frozen:
    name: str

f = Frozen("Alice")
f.name = "Bob"
""")
    assert "invalid-assignment" in output, (
        f"Expected invalid-assignment for frozen field mutation, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_metaclass_transformer_kwargs_frozen():
    """Metaclass-based transformer with **kwargs respects frozen=True."""
    output = run_ty("""\
from typing import dataclass_transform

@dataclass_transform()
class ModelMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs): ...

class ModelBase(metaclass=ModelMeta): ...

class Frozen(ModelBase, frozen=True):
    name: str

f = Frozen(name="test")
f.name = "new"
""")
    assert "invalid-assignment" in output, (
        f"Expected invalid-assignment for frozen field mutation, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_base_class_transformer_kwargs_frozen():
    """Base-class-based transformer with __init_subclass__(**kwargs) respects frozen=True."""
    output = run_ty("""\
from typing import dataclass_transform

@dataclass_transform()
class ModelBase:
    def __init_subclass__(cls, **kwargs): ...

class Frozen(ModelBase, frozen=True):
    name: str

f = Frozen(name="test")
f.name = "new"
""")
    assert "invalid-assignment" in output, (
        f"Expected invalid-assignment for frozen field mutation, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression: explicit params still work
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_explicit_params_still_work():
    """Explicit frozen param in function transformer still recognized."""
    output = run_ty("""\
from typing import dataclass_transform

@dataclass_transform()
def create_model(*, frozen: bool = False): ...

@create_model(frozen=True)
class ExplicitFrozen:
    name: str

f = ExplicitFrozen(name="test")
f.name = "new"
""")
    assert "invalid-assignment" in output, (
        f"Expected invalid-assignment for explicit frozen param, got:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_non_frozen_allows_mutation():
    """Non-frozen dataclass via **kwargs allows field mutation (no false positive)."""
    output = run_ty("""\
from typing import dataclass_transform, Callable

@dataclass_transform()
def create_model[T: type](**kwargs) -> Callable[[T], T]:
    raise NotImplementedError

@create_model()
class Mutable:
    name: str

m = Mutable("Alice")
m.name = "Bob"
""")
    assert "invalid-assignment" not in output, (
        f"Unexpected invalid-assignment on non-frozen class:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass -- AGENTS.md:72 @ 32f644c3bfa09271cc54ca04f7259fbf8a99b81f
def test_mdtest_updated_with_kwargs():
    """AGENTS.md:72 'All changes must be tested' -- mdtest file should cover kwargs."""
    mdtest_path = Path(REPO) / "crates/ty_python_semantic/resources/mdtest/dataclasses/dataclass_transform.md"
    assert mdtest_path.exists(), "dataclass_transform.md mdtest file not found"
    content = mdtest_path.read_text()
    # The PR adds a "### Transformers using `**kwargs`" section — this heading
    # does not exist on the base commit, so the check is a valid fail_to_pass.
    assert "### Transformers using" in content, (
        "mdtest file should include a section testing kwargs transformer patterns"
    )


# [agent_config] pass_to_pass -- AGENTS.md:79 @ 32f644c3bfa09271cc54ca04f7259fbf8a99b81f
def test_no_unwrap_panic_in_dataclass_flags():
    """AGENTS.md:79 'Avoid panic!/unreachable!/.unwrap()' in DATACLASS_FLAGS section."""
    bind_rs = Path(REPO) / "crates/ty_python_semantic/src/types/call/bind.rs"
    content = bind_rs.read_text()
    # Extract section from DATACLASS_FLAGS to end of the flags loop
    start = content.find("DATACLASS_FLAGS")
    assert start != -1, "DATACLASS_FLAGS not found in bind.rs"
    section = content[start:start + 2000]
    for pattern in [".unwrap()", "panic!(", "unreachable!("]:
        assert pattern not in section, (
            f"Found '{pattern}' in DATACLASS_FLAGS section of bind.rs"
        )
