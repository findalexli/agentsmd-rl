"""Tests for: vendor and simplify minimist as TypeScript (microsoft/playwright#39734).

The PR vendors a stripped-down `minimist` argument parser as a standalone
TypeScript file at packages/playwright-core/src/tools/cli-client/minimist.ts,
removes the npm `minimist` dependency, and updates program.ts / session.ts
to use the vendored module.

Each test_* maps 1:1 to a check id in eval_manifest.yaml.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/playwright")
CLI_CLIENT = REPO / "packages/playwright-core/src/tools/cli-client"
MINIMIST_TS = CLI_CLIENT / "minimist.ts"
PROGRAM_TS = CLI_CLIENT / "program.ts"
SESSION_TS = CLI_CLIENT / "session.ts"
DEPS_LIST = CLI_CLIENT / "DEPS.list"
PKG_JSON = REPO / "package.json"

_COMPILE_DIR = Path("/tmp/minimist_compiled")
_COMPILE_OUT = _COMPILE_DIR / "minimist.js"


def _compile_minimist() -> Path:
    """Compile minimist.ts to JS once per pytest session and return the .js path."""
    if _COMPILE_OUT.exists():
        return _COMPILE_OUT
    if not MINIMIST_TS.exists():
        raise FileNotFoundError(f"{MINIMIST_TS} does not exist")
    if _COMPILE_DIR.exists():
        shutil.rmtree(_COMPILE_DIR)
    _COMPILE_DIR.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            "tsc",
            "--target", "es2020",
            "--module", "commonjs",
            "--strict",
            "--esModuleInterop",
            "--skipLibCheck",
            "--outDir", str(_COMPILE_DIR),
            str(MINIMIST_TS),
        ],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"tsc failed (exit {r.returncode}):\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
        )
    if not _COMPILE_OUT.exists():
        raise RuntimeError(f"tsc did not produce {_COMPILE_OUT}")
    return _COMPILE_OUT


def _run_minimist(args, opts=None):
    """Invoke the compiled vendored minimist via Node and return parsed result."""
    js = _compile_minimist()
    payload = {"args": args, "opts": opts or {}}
    script = (
        f"const m = require({json.dumps(str(js))});"
        f"const p = {json.dumps(payload)};"
        "try {"
        "  const out = m.minimist(p.args, p.opts);"
        "  process.stdout.write(JSON.stringify({ok:true, value: out}));"
        "} catch (e) {"
        "  process.stdout.write(JSON.stringify({ok:false, error: String(e && e.message || e)}));"
        "}"
    )
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"node failed: stdout={r.stdout!r} stderr={r.stderr!r}"
    return json.loads(r.stdout)


# ────────────────────────── existence / compilation ──────────────────────────

def test_minimist_file_exists():
    assert MINIMIST_TS.exists(), f"vendored parser file missing at {MINIMIST_TS}"


def test_minimist_compiles_to_js():
    js = _compile_minimist()
    assert js.exists() and js.stat().st_size > 0


def test_minimist_exports_function():
    """The vendored module must export a `minimist` function."""
    js = _compile_minimist()
    r = subprocess.run(
        ["node", "-e",
         f"const m = require({json.dumps(str(js))});"
         "process.stdout.write(JSON.stringify({"
         "  hasFn: typeof m.minimist === 'function',"
         "  keys: Object.keys(m)"
         "}));"],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["hasFn"] is True, f"`minimist` not exported as function; module keys: {out['keys']}"


# ────────────────────────── parser behavior ──────────────────────────────────

def test_minimist_parses_long_eq():
    res = _run_minimist(["--foo=bar"])
    assert res["ok"] is True, res
    assert res["value"] == {"_": [], "foo": "bar"}


def test_minimist_parses_long_space():
    res = _run_minimist(["--foo", "bar"])
    assert res["ok"] is True, res
    assert res["value"] == {"_": [], "foo": "bar"}


def test_minimist_long_no_value_is_true():
    res = _run_minimist(["--foo"])
    assert res["ok"] is True, res
    assert res["value"] == {"_": [], "foo": True}


def test_minimist_no_prefix_negates_to_false():
    res = _run_minimist(["--no-foo"])
    assert res["ok"] is True, res
    assert res["value"] == {"_": [], "foo": False}


def test_minimist_boolean_default_unset():
    """Simplification: declared boolean options NOT passed get NO default value
    (they must be absent from the result, not set to false). The original npm
    minimist defaulted them to false."""
    res = _run_minimist([], {"boolean": ["foo"]})
    assert res["ok"] is True, res
    assert res["value"] == {"_": []}
    assert "foo" not in res["value"], (
        f"boolean opts not passed should be absent, got {res['value']}"
    )


def test_minimist_boolean_eq_value_throws():
    """Simplification: passing `--bool=value` for a declared boolean option must
    throw an error (rather than silently accepting it)."""
    res = _run_minimist(["--enabled=true"], {"boolean": ["enabled"]})
    assert res["ok"] is False, f"expected error, got {res}"
    assert "should not be passed with '=value'" in res["error"], res["error"]
    assert "--enabled" in res["error"]


def test_minimist_no_prefix_works_for_boolean_opt():
    res = _run_minimist(["--no-enabled"], {"boolean": ["enabled"]})
    assert res["ok"] is True, res
    assert res["value"]["enabled"] is False


def test_minimist_double_dash_separator():
    res = _run_minimist(["--foo", "bar", "--", "baz", "--qux", "quux"])
    assert res["ok"] is True, res
    v = res["value"]
    assert v["foo"] == "bar"
    assert v["_"] == ["baz", "--qux", "quux"]


def test_minimist_positional_args():
    res = _run_minimist(["alpha", "beta", "gamma"])
    assert res["ok"] is True, res
    assert res["value"] == {"_": ["alpha", "beta", "gamma"]}


def test_minimist_short_flag_no_value():
    res = _run_minimist(["-x"])
    assert res["ok"] is True, res
    assert res["value"] == {"_": [], "x": True}


def test_minimist_long_with_true_string_for_boolean_opt_coerces():
    """When a boolean option is followed by 'true' or 'false', coerce to bool."""
    r1 = _run_minimist(["--enabled", "true"], {"boolean": ["enabled"]})
    assert r1["ok"] is True, r1
    assert r1["value"]["enabled"] is True

    r2 = _run_minimist(["--enabled", "false"], {"boolean": ["enabled"]})
    assert r2["ok"] is True, r2
    assert r2["value"]["enabled"] is False


def test_minimist_repeated_long_collects_array():
    res = _run_minimist(["--tag", "a", "--tag", "b", "--tag", "c"])
    assert res["ok"] is True, res
    assert res["value"]["tag"] == ["a", "b", "c"]


def test_minimist_string_opt_no_value_is_empty_string():
    """String options without a value get '' rather than true."""
    res = _run_minimist(["--name"], {"string": ["name"]})
    assert res["ok"] is True, res
    assert res["value"]["name"] == ""


def test_minimist_mixed_positional_and_flag():
    res = _run_minimist(["cmd", "--opt", "val", "extra"])
    assert res["ok"] is True, res
    v = res["value"]
    assert v["opt"] == "val"
    assert v["_"] == ["cmd", "extra"]


# ────────────────────────── integration into program.ts/session.ts ──────────

def test_program_no_require_minimist():
    """program.ts must no longer use `require('minimist')`."""
    txt = PROGRAM_TS.read_text()
    assert "require('minimist')" not in txt, "program.ts still calls require('minimist')"
    assert 'require("minimist")' not in txt, "program.ts still calls require(\"minimist\")"


def test_program_imports_vendored_minimist():
    """program.ts must import the vendored `minimist` from the local module."""
    txt = PROGRAM_TS.read_text()
    has_import = (
        "from './minimist'" in txt or 'from "./minimist"' in txt
    )
    assert has_import, "program.ts does not import from './minimist'"
    # Must use the imported function, not require('minimist')
    assert "minimist(" in txt, "program.ts should call minimist(...)"


def test_session_imports_minimistargs_type():
    """session.ts must import MinimistArgs as a type from the vendored module."""
    txt = SESSION_TS.read_text()
    has_type_import = (
        "from './minimist'" in txt or 'from "./minimist"' in txt
    )
    assert has_type_import, "session.ts does not import from './minimist'"
    assert "MinimistArgs" in txt, "session.ts no longer references MinimistArgs"


def test_session_no_local_minimistargs_decl():
    """The local `type MinimistArgs = { ... }` should be removed from session.ts."""
    txt = SESSION_TS.read_text()
    assert "type MinimistArgs = {" not in txt, (
        "session.ts still declares its own `type MinimistArgs`; should import from ./minimist"
    )


def test_program_no_local_minimistargs_decl():
    """The local `type MinimistArgs = { ... }` should be removed from program.ts."""
    txt = PROGRAM_TS.read_text()
    assert "type MinimistArgs = {" not in txt, (
        "program.ts still declares its own `type MinimistArgs`; should import from ./minimist"
    )


def test_deps_list_minimist_section():
    """DEPS.list must declare the new minimist.ts module."""
    txt = DEPS_LIST.read_text()
    assert "[minimist.ts]" in txt, "DEPS.list missing [minimist.ts] section"


def test_deps_list_program_includes_minimist():
    """program.ts's DEPS.list section must list ./minimist.ts as an allowed import."""
    txt = DEPS_LIST.read_text()
    # Find the [program.ts] section
    idx = txt.find("[program.ts]")
    assert idx != -1, "DEPS.list missing [program.ts] section"
    next_section = txt.find("\n[", idx + 1)
    section = txt[idx:next_section if next_section != -1 else len(txt)]
    assert "./minimist.ts" in section, (
        f"DEPS.list [program.ts] section does not list ./minimist.ts as a dep:\n{section}"
    )


def test_deps_list_session_includes_minimist():
    """session.ts's DEPS.list section must list ./minimist.ts as an allowed import."""
    txt = DEPS_LIST.read_text()
    idx = txt.find("[session.ts]")
    assert idx != -1, "DEPS.list missing [session.ts] section"
    next_section = txt.find("\n[", idx + 1)
    section = txt[idx:next_section if next_section != -1 else len(txt)]
    assert "./minimist.ts" in section, (
        f"DEPS.list [session.ts] section does not list ./minimist.ts as a dep:\n{section}"
    )


def test_package_json_no_types_minimist():
    """The @types/minimist devDependency must be removed from package.json."""
    pkg = json.loads(PKG_JSON.read_text())
    assert "@types/minimist" not in pkg.get("devDependencies", {}), (
        "@types/minimist should be removed from devDependencies"
    )
    assert "@types/minimist" not in pkg.get("dependencies", {})


# ────────────────────────── pass-to-pass (sanity) ────────────────────────────

def test_other_cli_client_files_intact():
    """cli.ts and registry.ts must still exist (PR should not delete them)."""
    assert (CLI_CLIENT / "cli.ts").exists()
    assert (CLI_CLIENT / "registry.ts").exists()


def test_deps_list_other_sections_intact():
    """DEPS.list retains [program.ts], [session.ts], [registry.ts] sections."""
    txt = DEPS_LIST.read_text()
    for section in ("[program.ts]", "[session.ts]", "[registry.ts]"):
        assert section in txt, f"DEPS.list missing {section}"


def test_package_json_node_engine_intact():
    """The repo's Node engine constraint should not have changed."""
    pkg = json.loads(PKG_JSON.read_text())
    assert pkg.get("engines", {}).get("node") == ">=18"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_playwright_driver_npm():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_playwright_driver_npm_2():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")