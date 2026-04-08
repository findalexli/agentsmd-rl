"""
Task: nextjs-turbopack-graph-span-modules
Repo: vercel/next.js @ 25646b928f900c12504b8a30ce5939207533aa54
PR:   #91697

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rust codebase — no compiler in Docker image. f2p tests use subprocess to
execute Python validation scripts that parse Rust source files and verify
the structural changes required by the PR.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
APP_FILE = f"{REPO}/crates/next-api/src/app.rs"
PROJECT_FILE = f"{REPO}/crates/next-api/src/project.rs"
MOD_FILE = f"{REPO}/turbopack/crates/turbopack-core/src/module_graph/mod.rs"


def _run_validator(name: str, code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a Python validation script to /tmp and execute it via subprocess."""
    script = Path(f"/tmp/_validator_{name}.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass — anti-stub gate
# ---------------------------------------------------------------------------


def test_antistub_files_have_substantial_content():
    """All three modified files have substantial Rust code (not replaced with stubs)."""
    for path, name, min_lines in [
        (APP_FILE, "app.rs", 500),
        (PROJECT_FILE, "project.rs", 500),
        (MOD_FILE, "mod.rs", 200),
    ]:
        lines = Path(path).read_text().splitlines()
        assert len(lines) >= min_lines, f"{name} has {len(lines)} lines (need >= {min_lines})"
        fn_count = sum(1 for line in lines if "fn " in line)
        assert fn_count >= 5, f"{name} has {fn_count} fn defs (need >= 5)"


# ---------------------------------------------------------------------------
# fail_to_pass — subprocess-executed validation
# ---------------------------------------------------------------------------


def test_module_count_method_in_single_module_graph():
    """impl SingleModuleGraph exposes module count via turbo_tasks::function."""
    r = _run_validator("mod_count", _MOD_COUNT_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_MOD_COUNT_VALIDATOR = '''
import sys
from pathlib import Path

lines = Path("/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/mod.rs").read_text().splitlines()

count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]

found = False
for i, line in enumerate(lines):
    fn_name = None
    for name in count_fn_names:
        if "fn " + name in line:
            fn_name = name
            break
    if fn_name is None:
        continue

    # Must be inside impl SingleModuleGraph (scan upward for impl header)
    depth = 0
    in_impl = False
    for j in range(i, -1, -1):
        depth += lines[j].count("}") - lines[j].count("{")
        if "impl SingleModuleGraph" in lines[j] and depth <= 0:
            in_impl = True
            break
    if not in_impl:
        continue

    # Must have #[turbo_tasks::function] annotation in preceding lines
    preceding = lines[max(0, i - 5) : i + 1]
    if not any("turbo_tasks" in l and "function" in l for l in preceding):
        sys.exit(fn_name + " missing #[turbo_tasks::function] annotation")

    # Body must reference self (accessing internal data)
    body = lines[i : i + 15]
    if not any("self" in l for l in body):
        sys.exit(fn_name + " body does not reference self")

    # Must involve a numeric type (return type or cast)
    body_text = " ".join(body)
    if not any(t in body_text for t in ["u64", "usize", "i64", "u32"]):
        sys.exit(fn_name + " body does not involve numeric type (u64/usize/etc.)")

    # Anti-stub: body must have meaningful content beyond signature
    meaningful = [l.strip() for l in lines[i + 1 : i + 15]
                  if l.strip() and l.strip() not in ("{", "}")]
    if len(meaningful) < 1:
        sys.exit(fn_name + " body is empty - likely a stub")

    found = True
    break

if not found:
    sys.exit("No module count method found in SingleModuleGraph impl")
print("PASS")
'''


def test_app_rs_records_module_count_in_span():
    """app.rs has a tracing span with 'modules' field and records module count."""
    r = _run_validator("app_span", _APP_SPAN_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_APP_SPAN_VALIDATOR = '''
import sys
from pathlib import Path

lines = Path("/workspace/next.js/crates/next-api/src/app.rs").read_text().splitlines()

# 1. Find a tracing span with "modules" field declared
span_keywords = ["info_span!", "span!", "debug_span!", "trace_span!"]
has_span_with_modules = False
for i, line in enumerate(lines):
    has_span = any(kw in line for kw in span_keywords)
    has_modules_field = "modules" in line and ("=" in line or "Empty" in line)
    if has_span and has_modules_field:
        has_span_with_modules = True
        break

if not has_span_with_modules:
    sys.exit("No tracing span with 'modules' field found in app.rs")

# 2. Must record module count into the span
has_record = False
for line in lines:
    if ".record(" in line and "modules" in line:
        has_record = True
        break
if not has_record:
    sys.exit("No span.record('modules', ...) found in app.rs")

# 3. Must call module_count (or equivalent) somewhere
count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]
has_count_call = False
for line in lines:
    for name in count_fn_names:
        if name + "(" in line:
            has_count_call = True
            break
    if has_count_call:
        break
if not has_count_call:
    sys.exit("No module count call found in app.rs")

print("PASS")
'''


def test_project_rs_records_module_count_in_span():
    """project.rs has a tracing span with 'modules' for whole-app graph path."""
    r = _run_validator("project_span", _PROJECT_SPAN_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_PROJECT_SPAN_VALIDATOR = '''
import sys
from pathlib import Path

lines = Path("/workspace/next.js/crates/next-api/src/project.rs").read_text().splitlines()

# 1. Find a tracing span with "modules" field
span_keywords = ["info_span!", "span!", "debug_span!", "trace_span!"]
has_span_with_modules = False
for i, line in enumerate(lines):
    has_span = any(kw in line for kw in span_keywords)
    has_modules_field = "modules" in line and ("=" in line or "Empty" in line)
    if has_span and has_modules_field:
        has_span_with_modules = True
        break

if not has_span_with_modules:
    sys.exit("No tracing span with 'modules' field found in project.rs")

# 2. Must record module count into the span
record_lines = []
for i, line in enumerate(lines):
    if ".record(" in line and "modules" in line:
        record_lines.append(i)
if not record_lines:
    sys.exit("No span.record('modules', ...) found in project.rs")

# 3. Must call module_count (or equivalent)
count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]
count_lines = []
for i, line in enumerate(lines):
    for name in count_fn_names:
        if name + "(" in line:
            count_lines.append(i)
            break
if not count_lines:
    sys.exit("No module count call found in project.rs")

# 4. Span/record must be near a whole-app graph function
whole_app_lines = [i for i, line in enumerate(lines)
                   if "whole_app" in line or "module_graph_operation" in line]

def near(a_lines, b_lines, distance):
    return any(abs(a - b) <= distance for a in a_lines for b in b_lines)

if not near(record_lines + count_lines, whole_app_lines, 80):
    sys.exit("modules span/record not scoped to whole-app graph code in project.rs")

print("PASS")
'''


def test_performance_guard_before_module_count():
    """Both app.rs and project.rs guard module count computation on span activity."""
    r = _run_validator("perf_guard", _PERF_GUARD_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_PERF_GUARD_VALIDATOR = '''
import sys
from pathlib import Path

count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]

for filepath, name in [
    ("/workspace/next.js/crates/next-api/src/app.rs", "app.rs"),
    ("/workspace/next.js/crates/next-api/src/project.rs", "project.rs"),
]:
    lines = Path(filepath).read_text().splitlines()

    # Find guard lines (is_disabled, is_enabled, has_field)
    guard_lines = []
    for i, line in enumerate(lines):
        if ("is_disabled" in line or "is_enabled" in line or
                "has_field" in line):
            guard_lines.append(i)
    if not guard_lines:
        sys.exit(name + " missing performance guard")

    # Find module count call lines and record lines
    relevant_lines = []
    for i, line in enumerate(lines):
        for fn_name in count_fn_names:
            if fn_name + "(" in line:
                relevant_lines.append(i)
                break
        if ".record(" in line and "modules" in line:
            relevant_lines.append(i)
    if not relevant_lines:
        sys.exit(name + " count call lines not found")

    # Guard must be within 40 lines of a relevant line
    near = any(abs(g - r) <= 40 for g in guard_lines for r in relevant_lines)
    if not near:
        sys.exit(name + " guard not near module count computation")

print("PASS")
'''


# ---------------------------------------------------------------------------
# pass_to_pass — existing functions/types preserved
# ---------------------------------------------------------------------------


def test_existing_functions_and_types_preserved():
    """Enhancement must not remove existing functions or types."""
    proj_raw = Path(PROJECT_FILE).read_text()
    for name in ["whole_app_module_graphs", "whole_app_module_graph_operation"]:
        assert ("fn " + name) in proj_raw, f"{name} function missing from project.rs"
    assert "BaseAndFullModuleGraph" in proj_raw, "BaseAndFullModuleGraph type missing"

    mod_raw = Path(MOD_FILE).read_text()
    assert "SingleModuleGraph" in mod_raw, "SingleModuleGraph missing from mod.rs"
    assert "number_of_modules" in mod_raw, "number_of_modules field missing from mod.rs"
