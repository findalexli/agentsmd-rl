"""
Task: prime-rl-config-none-toml-serialize
Repo: PrimeIntellect-ai/prime-rl @ 692dfc8a4b9471e65004d8ac154d07ebb73bc61c
PR:   #2093

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/prime-rl"
CONFIG_PY = Path(f"{REPO}/src/prime_rl/utils/config.py")
ENTRYPOINTS = ["inference", "rl", "sft"]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo's environment."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass - TOML config files must be valid
def test_repo_toml_configs_valid():
    """All TOML config files in the repo must be valid (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            "import tomllib; from pathlib import Path; "
            "[tomllib.load(open(f, 'rb')) for f in (list(Path('configs').rglob('*.toml')) + list(Path('examples').rglob('*.toml')))]; "
            "print('TOML OK')",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stderr[-500:]}"
    assert "TOML OK" in r.stdout


# [repo_tests] pass_to_pass - Config module must import correctly
def test_repo_config_module_imports():
    """Config module must import and have required exports (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            "from prime_rl.utils.config import cli, BaseConfig; "
            "assert hasattr(BaseConfig, '_none_str_to_none'), '_none_str_to_none missing'; "
            "assert callable(cli), 'cli not callable'; "
            "print('Config imports OK')",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Config import test failed:\n{r.stderr[-500:]}"
    assert "Config imports OK" in r.stdout


# [repo_tests] pass_to_pass - BaseConfig._none_str_to_none feature works
def test_repo_config_none_str_to_none():
    """BaseConfig._none_str_to_none converts 'None' strings to None values (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            "from prime_rl.utils.config import BaseConfig; import tomllib, tempfile, os; "
            "content = b'value = \"None\"\\n'; "
            "f = tempfile.NamedTemporaryFile(delete=False, suffix='.toml'); "
            "f.write(content); f.close(); "
            "loaded = BaseConfig._none_str_to_none(tomllib.load(open(f.name, 'rb'))); "
            "assert loaded.get('value') is None, f'Expected None, got {loaded.get(\"value\")}'; "
            "os.unlink(f.name); "
            "print('_none_str_to_none OK')",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"_none_str_to_none test failed:\n{r.stderr[-500:]}"
    assert "_none_str_to_none OK" in r.stdout


# [static] pass_to_pass
def test_syntax_check():
    """Modified files (config.py, all entrypoints) must parse without errors."""
    files = [CONFIG_PY] + [
        Path(f"{REPO}/src/prime_rl/entrypoints/{ep}.py") for ep in ENTRYPOINTS
    ]
    for f in files:
        ast.parse(f.read_text())


# [repo_tests] pass_to_pass - from .github/workflows/style.yaml
def test_repo_ruff_linting():
    """Repo's ruff linting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # pip install may return 0 even with warnings
    r = subprocess.run(
        [
            "ruff", "check",
            "--config=pyproject.toml",
            "src/prime_rl/utils/config.py",
            "src/prime_rl/entrypoints/inference.py",
            "src/prime_rl/entrypoints/rl.py",
            "src/prime_rl/entrypoints/sft.py",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - from .github/workflows/style.yaml
def test_repo_ruff_formatting():
    """Repo's ruff formatting check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        [
            "ruff", "format", "--check",
            "--config=pyproject.toml",
            "src/prime_rl/utils/config.py",
            "src/prime_rl/entrypoints/inference.py",
            "src/prime_rl/entrypoints/rl.py",
            "src/prime_rl/entrypoints/sft.py",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_flat_none_conversion():
    """Flat dict None values are converted to 'None' strings."""
    r = _run_py("""
from prime_rl.utils.config import none_to_none_str

result = none_to_none_str({"a": None, "b": 42, "c": "hello", "d": None})
assert result == {"a": "None", "b": 42, "c": "hello", "d": "None"}, f"Got {result}"

assert none_to_none_str({"x": None}) == {"x": "None"}

result2 = none_to_none_str({"p": 0, "q": None, "r": False})
assert result2 == {"p": 0, "q": "None", "r": False}, f"Got {result2}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_nested_none_conversion():
    """Nested dict None values are converted recursively."""
    r = _run_py("""
from prime_rl.utils.config import none_to_none_str

result = none_to_none_str({
    "top": None,
    "nested": {"a": None, "b": 1, "deep": {"x": None, "y": "ok"}},
})
assert result["top"] == "None", f"top: {result['top']}"
assert result["nested"]["a"] == "None"
assert result["nested"]["b"] == 1
assert result["nested"]["deep"]["x"] == "None"
assert result["nested"]["deep"]["y"] == "ok"

result2 = none_to_none_str({"l1": {"l2": {"v": None}}, "other": None})
assert result2["l1"]["l2"]["v"] == "None"
assert result2["other"] == "None"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_toml_roundtrip():
    """TOML round-trip preserves None as 'None' string."""
    r = _run_py("""
import io, tomli_w, tomllib
from prime_rl.utils.config import none_to_none_str

configs = [
    {"model": {"name": "test", "max_len": None}, "seed": None, "lr": 0.001},
    {"a": None, "b": {"c": None, "d": 1}},
    {"top": None},
]

for d in configs:
    converted = none_to_none_str(d)
    buf = io.BytesIO()
    tomli_w.dump(converted, buf)
    buf.seek(0)
    loaded = tomllib.load(buf)

    def check_none(orig, loaded_d):
        for k, v in orig.items():
            if v is None:
                assert loaded_d[k] == "None", f"{k} not preserved as 'None'"
            elif isinstance(v, dict):
                check_none(v, loaded_d[k])
            else:
                assert loaded_d[k] == v, f"{k} changed unexpectedly"
    check_none(d, loaded)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_edge_cases():
    """Handles empty dicts, all-None, bools, lists; does not mutate input."""
    r = _run_py("""
import copy
from prime_rl.utils.config import none_to_none_str

assert none_to_none_str({}) == {}
assert none_to_none_str({"a": None}) == {"a": "None"}
assert none_to_none_str({"a": {"b": None}}) == {"a": {"b": "None"}}

# Lists passed through unchanged
assert none_to_none_str({"x": [1, 2, 3]}) == {"x": [1, 2, 3]}

# Bools preserved
assert none_to_none_str({"x": True, "y": False}) == {"x": True, "y": False}

# Ints/strings preserved
assert none_to_none_str({"n": 0, "s": ""}) == {"n": 0, "s": ""}

# Non-mutation check
original = {"a": None, "b": 1, "nested": {"c": None}}
original_copy = copy.deepcopy(original)
none_to_none_str(original)
assert original == original_copy, "Function must not mutate input dict"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_entrypoints_no_exclude_none():
    """Entrypoints no longer use exclude_none=True in model_dump calls."""
    r = _run_py("""
import ast
from pathlib import Path

for ep in ["inference", "rl", "sft"]:
    path = Path(f"/workspace/prime-rl/src/prime_rl/entrypoints/{ep}.py")
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "model_dump":
                for kw in node.keywords:
                    if kw.arg == "exclude_none":
                        if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            raise AssertionError(
                                f"{ep}.py still uses exclude_none=True in model_dump"
                            )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_non_none_passthrough():
    """Non-None config values serialize identically after conversion."""
    r = _run_py("""
from prime_rl.utils.config import none_to_none_str

configs = [
    {"model": {"name": "Qwen/Qwen3-0.6B", "max_model_len": 4096, "eager": True}, "seed": 42},
    {"port": 8000, "host": "0.0.0.0"},
    {"x": 1, "y": 2.5, "z": "hello"},
]
for d in configs:
    assert none_to_none_str(d) == d, f"Non-None values changed: {d}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:5 @ 692dfc8a
def test_no_try_except_in_converter():
    """Conversion function must not use try/except (AGENTS.md rule)."""
    source = CONFIG_PY.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "none_to_none_str":
            tries = [n for n in ast.walk(node) if isinstance(n, ast.Try)]
            assert not tries, (
                f"none_to_none_str uses try/except (violates AGENTS.md:5 — "
                "avoid try/except unless truly necessary)"
            )


# [agent_config] pass_to_pass — AGENTS.md:7 @ 692dfc8a
def test_no_process_comments():
    """Changed files must not contain comments referring to old code or work process (AGENTS.md rule)."""
    import re

    process_patterns = re.compile(
        r"#.*\b(previously|used to|was changed|old code|removed|replaced with|"
        r"changed from|refactored|updated to|modified to|before this|original)\b",
        re.IGNORECASE,
    )
    files = [CONFIG_PY] + [
        Path(f"{REPO}/src/prime_rl/entrypoints/{ep}.py") for ep in ENTRYPOINTS
    ]
    for f in files:
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if process_patterns.search(line):
                raise AssertionError(
                    f"{f.name}:{i} has process-referencing comment "
                    f"(violates AGENTS.md:7): {line.strip()!r}"
                )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_tests_run_tests():
    """pass_to_pass | CI job 'Unit tests' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTEST_OUTPUT_DIR=/tmp/outputs uv run pytest tests/unit -m "not gpu"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")