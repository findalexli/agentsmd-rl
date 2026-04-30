"""Unit tests for exec_f2p_miner — the SWE-rebench-V2-style execution-based
fail-to-pass miner. Covers:

  * parser routing (PARSER_MAP head match, JS smart dispatcher fallback)
  * picker selection across f2p/p2p, install-step extraction, deny rules
  * pip install patching (--break-system-packages on PEP 668 images)
  * generic install fallbacks per runner head

No E2B / docker calls — the dual-pass executor is exercised separately.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from taskforge.exec_f2p_miner import (
    PARSER_MAP,
    _parse_log_js_smart,
    _patch_pip_install,
    pick_parser,
    pick_setup_and_test_commands,
)
from taskforge.exec_log_parsers import (
    parse_log_pytest, parse_log_cargo, parse_log_gotest,
    parse_log_vitest, parse_log_jest,
)


def _ok(name: str, cond: bool, detail: str = ""):
    flag = "PASS" if cond else "FAIL"
    print(f"  [{flag}] {name}{(' — ' + detail) if detail and not cond else ''}")
    return cond


# -----------------------------------------------------------------------------
# Parser routing
# -----------------------------------------------------------------------------

def test_pick_parser():
    print("\n=== pick_parser ===")
    cases = [
        ("pytest tests/", parse_log_pytest),
        ("pytest --cov=src tests/unit", parse_log_pytest),
        ("cargo test --workspace", parse_log_cargo),
        ("cargo test -p mycrate -- --nocapture", parse_log_cargo),
        ("go test ./...", parse_log_gotest),
        ("mage -v test", parse_log_gotest),
        ("vitest run", parse_log_vitest),
        ("jest --ci", parse_log_jest),
        ("pnpm -F @org/pkg test", _parse_log_js_smart),
        ("npm run test", _parse_log_js_smart),
        ("yarn workspace foo test", _parse_log_js_smart),
        ("bun test", _parse_log_js_smart),
        ("/bin/false", None),                     # not a recognized runner
        ("", None),
    ]
    n_ok = 0
    for cmd, expected in cases:
        actual = pick_parser(cmd)
        ok = actual is expected or (expected is None and actual is None)
        n_ok += _ok(f"{cmd!r:50s} → {expected.__name__ if expected else None}", ok,
                    f"got {actual.__name__ if actual else None}")
    return n_ok == len(cases)


# -----------------------------------------------------------------------------
# Real-world parser outputs
# -----------------------------------------------------------------------------

def test_parsers_on_real_outputs():
    print("\n=== parsers on representative log outputs ===")
    n_ok = 0; n_total = 0
    # cargo
    cargo_log = "test foo ... ok\ntest bar ... FAILED\ntest baz ... ok\n\ntest result: ok. 2 passed; 1 failed"
    out = parse_log_cargo(cargo_log)
    n_total += 1; n_ok += _ok("cargo: 3 tests parsed", len(out) == 3, f"got {len(out)}: {out}")
    # pytest
    pytest_log = "PASSED tests/a.py::test_one\nFAILED tests/a.py::test_two - oops\nSKIPPED tests/a.py::test_three\n"
    out = parse_log_pytest(pytest_log)
    n_total += 1; n_ok += _ok("pytest: 3 tests parsed", len(out) == 3, f"got {out}")
    # gotest
    go_log = "=== RUN   TestA\n--- PASS: TestA (0.00s)\n=== RUN   TestB\n--- FAIL: TestB (0.01s)\n"
    out = parse_log_gotest(go_log)
    n_total += 1; n_ok += _ok("gotest: 2 tests parsed", len(out) == 2, f"got {out}")
    # vitest (with vitest's checkmark format)
    vitest_log = " ✓ src/foo.test.ts > should work (3ms)\n × src/bar.test.ts > broken (5ms)\n"
    out = parse_log_vitest(vitest_log)
    n_total += 1; n_ok += _ok("vitest: 2 tests parsed", len(out) == 2, f"got {out}")
    # JS smart dispatcher routes vitest output correctly
    out = _parse_log_js_smart(vitest_log)
    n_total += 1; n_ok += _ok("js_smart: vitest log → vitest parser", len(out) == 2, f"got {out}")
    return n_ok == n_total


# -----------------------------------------------------------------------------
# Test command picking
# -----------------------------------------------------------------------------

def test_pick_setup_and_test_commands():
    print("\n=== pick_setup_and_test_commands ===")
    n_ok = 0
    # f2p check with prior install steps in same job
    spec = {
        "checks": [
            {"name": "test", "kind": "f2p", "steps": [
                {"step_name": "Install deps", "command": "pip install -e ."},
                {"step_name": "Run tests", "command": "pytest tests/"},
            ]},
        ]
    }
    res = pick_setup_and_test_commands(spec)
    n_ok += _ok("f2p chosen, prior install captured",
                res is not None and "pytest tests/" in res[1] and any("pip install" in c for c in res[0]),
                f"got {res}")

    # No f2p, fall through to p2p
    spec = {
        "checks": [
            {"name": "lint", "kind": "p2p", "steps": [
                {"step_name": "Run linter", "command": "ruff check ."},   # not in allowlist → drop
            ]},
            {"name": "test", "kind": "p2p", "steps": [
                {"step_name": "Test", "command": "cargo test"},
            ]},
        ]
    }
    res = pick_setup_and_test_commands(spec)
    n_ok += _ok("p2p chosen when f2p absent",
                res is not None and res[1] == "cargo test", f"got {res}")

    # Deny: install command (even if it has a recognized head) shouldn't be picked
    spec = {
        "checks": [
            {"name": "build", "kind": "p2p", "steps": [
                {"step_name": "Install", "command": "pip install -e ."},  # head=pip, deny by name
                {"step_name": "Run tests", "command": "pytest tests/"},
            ]},
        ]
    }
    res = pick_setup_and_test_commands(spec)
    n_ok += _ok("install step not chosen as test cmd",
                res is not None and "pytest tests/" in res[1], f"got {res}")

    # GHA template ${{ ... }} should be skipped
    spec = {
        "checks": [
            {"name": "test", "kind": "f2p", "steps": [
                {"step_name": "Run", "command": "pytest --cov=${{ env.COV_DIR }} tests/"},
                {"step_name": "Run real", "command": "pytest tests/unit"},
            ]},
        ]
    }
    res = pick_setup_and_test_commands(spec)
    n_ok += _ok("GHA-template steps skipped",
                res is not None and res[1] == "pytest tests/unit", f"got {res}")

    # No usable step → None
    spec = {"checks": [{"name": "x", "kind": "p2p", "steps": [{"command": "echo hi"}]}]}
    res = pick_setup_and_test_commands(spec)
    n_ok += _ok("returns None when no parsable test command", res is None, f"got {res}")

    return n_ok == 5


# -----------------------------------------------------------------------------
# Pip install patching
# -----------------------------------------------------------------------------

def test_pip_install_patch():
    print("\n=== _patch_pip_install ===")
    cases = [
        ("pip install -e .", "pip install --break-system-packages -e ."),
        ("pip3 install -r req.txt", "pip3 install --break-system-packages -r req.txt"),
        # Already has flag → no double-patch
        ("pip install --break-system-packages foo", "pip install --break-system-packages foo"),
        # --user mode → don't patch (different install location)
        ("pip install --user foo", "pip install --user foo"),
        # Compound shell: each pip install gets patched
        ("cd src && pip install -e . && pytest",
         "cd src && pip install --break-system-packages -e . && pytest"),
        # No pip install → unchanged
        ("cargo test", "cargo test"),
    ]
    n_ok = 0
    for inp, expected in cases:
        actual = _patch_pip_install(inp)
        n_ok += _ok(f"{inp!r:50s} → expected", actual == expected,
                    f"got {actual!r}")
    return n_ok == len(cases)


# -----------------------------------------------------------------------------
# Run all
# -----------------------------------------------------------------------------

def main():
    suite = [
        test_pick_parser,
        test_parsers_on_real_outputs,
        test_pick_setup_and_test_commands,
        test_pip_install_patch,
    ]
    n_pass = 0
    for fn in suite:
        if fn(): n_pass += 1
    print(f"\n=== {n_pass}/{len(suite)} test functions passed ===")
    return 0 if n_pass == len(suite) else 1


if __name__ == "__main__":
    raise SystemExit(main())
