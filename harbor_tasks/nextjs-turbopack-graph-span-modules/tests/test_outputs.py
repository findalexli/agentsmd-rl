"""
Task: nextjs-turbopack-graph-span-modules
Repo: vercel/next.js @ 25646b928f900c12504b8a30ce5939207533aa54
PR:   #91697

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

WHY STRUCTURAL: Rust code in a ~200-crate Turbopack workspace.
No Rust toolchain in the Docker image — cannot compile or execute.
All tests use line-based regex on raw source to verify the code changes.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
APP_FILE = Path(REPO) / "crates/next-api/src/app.rs"
PROJECT_FILE = Path(REPO) / "crates/next-api/src/project.rs"
MOD_FILE = Path(REPO) / "turbopack/crates/turbopack-core/src/module_graph/mod.rs"

# Acceptable method names for the module count accessor
COUNT_FN_NAMES = (
    "module_count",
    "get_module_count",
    "num_modules",
    "modules_count",
    "count_modules",
    "module_len",
)
COUNT_FN_RE = re.compile(r"\bfn\s+(" + "|".join(COUNT_FN_NAMES) + r")\b")
COUNT_CALL_RE = re.compile(r"\b(" + "|".join(COUNT_FN_NAMES) + r")\s*\(")

# Performance guard patterns
GUARD_PATTERNS = [
    re.compile(p)
    for p in [
        r"is_disabled\s*\(\)",
        r"is_none\s*\(\)",
        r"!\s*\w+\.is_enabled\s*\(\)",
        r"\.is_enabled\s*\(\)",
        r"!\s*\w+\.is_disabled\s*\(\)",
        r"has_field\s*\(",
        r"match\s+\w+\.metadata",
    ]
]


def _lines(path: Path) -> list[str]:
    return path.read_text().splitlines()


def _find_lines(lines: list[str], pattern: re.Pattern) -> list[int]:
    """Return 0-based line indices matching pattern."""
    return [i for i, line in enumerate(lines) if pattern.search(line)]


def _any_within(a_lines: list[int], b_lines: list[int], distance: int) -> bool:
    """Check if any line in a_lines is within `distance` of any line in b_lines."""
    return any(abs(a - b) <= distance for a in a_lines for b in b_lines)


def _find_enclosing_impl(lines: list[str], target_line: int, type_name: str) -> bool:
    """Check if target_line is inside an impl block for type_name (search upward)."""
    impl_pat = re.compile(r"\bimpl\s+" + re.escape(type_name) + r"\b")
    depth = 0
    for i in range(target_line, -1, -1):
        line = lines[i]
        depth += line.count('}') - line.count('{')
        if impl_pat.search(line) and depth <= 0:
            return True
    return False


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — anti-stub: files have substantial Rust content
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_antistub_files_have_substantial_content():
    """All three modified files must have substantial Rust code (not replaced with stubs)."""
    checks = [
        (APP_FILE, "app.rs", 500),
        (PROJECT_FILE, "project.rs", 500),
        (MOD_FILE, "mod.rs", 200),
    ]
    for path, name, min_lines in checks:
        lines = _lines(path)
        assert len(lines) >= min_lines, (
            f"{name} has {len(lines)} lines (need >= {min_lines})"
        )
        content = path.read_text()
        fn_count = len(re.findall(r"\bfn\s+\w+", content))
        assert fn_count >= 5, f"{name} has {fn_count} fn defs (need >= 5)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_module_count_method_in_single_module_graph():
    """impl SingleModuleGraph must have a turbo_tasks::function that exposes module count."""
    lines = _lines(MOD_FILE)
    raw = MOD_FILE.read_text()

    # Find lines with fn module_count (or equivalent)
    fn_lines = _find_lines(lines, COUNT_FN_RE)
    assert fn_lines, "No module count method found in mod.rs"

    found = False
    for fn_line in fn_lines:
        fn_name = COUNT_FN_RE.search(lines[fn_line]).group(1)

        # Must be inside impl SingleModuleGraph
        assert _find_enclosing_impl(lines, fn_line, "SingleModuleGraph"), (
            f"{fn_name} not inside impl SingleModuleGraph"
        )

        # Must be annotated with #[turbo_tasks::function] in preceding lines
        preceding = "\n".join(lines[max(0, fn_line - 5) : fn_line + 1])
        assert "turbo_tasks" in preceding and "function" in preceding, (
            f"{fn_name} not annotated with #[turbo_tasks::function]"
        )

        # Must reference self (accessing internal data)
        # Check next ~10 lines for the function body
        body = "\n".join(lines[fn_line : fn_line + 15])
        assert "self" in body, f"{fn_name} doesn't reference self"

        # Must involve a numeric type (return type or cast)
        assert re.search(r"\b(u64|usize|i64|u32)\b", body), (
            f"{fn_name} doesn't involve a numeric type (u64/usize/etc.)"
        )

        # Anti-stub: body must have meaningful content beyond just a signature
        body_lines = [
            l.strip()
            for l in lines[fn_line + 1 : fn_line + 15]
            if l.strip() and l.strip() != "}" and l.strip() != "{"
        ]
        assert len(body_lines) >= 1, f"{fn_name} body is empty — likely a stub"

        found = True
        break

    assert found, "No valid module count method found in impl SingleModuleGraph"


# [pr_diff] fail_to_pass
def test_app_rs_records_module_count_in_span():
    """app.rs must have a tracing span with 'modules' field and record the module count."""
    lines = _lines(APP_FILE)
    raw = APP_FILE.read_text()

    # Tracing span with "modules" field
    span_pat = re.compile(r"(?:tracing\s*::\s*)?(?:info_span!|span!|debug_span!|trace_span!)")
    modules_field_pat = re.compile(r"\bmodules\s*=")
    span_lines = _find_lines(lines, span_pat)
    modules_lines = _find_lines(lines, modules_field_pat)
    has_span_with_modules = _any_within(span_lines, modules_lines, 3)

    instrument_pat = re.compile(r"#\[instrument\s*\([^]]*fields\s*\([^)]*modules")
    has_instrument = bool(instrument_pat.search(raw))

    assert has_span_with_modules or has_instrument, (
        "No tracing span with 'modules' field found in app.rs"
    )

    # Module count recorded into span
    assert re.search(r'\.record\(\s*["\']modules["\']', raw), (
        'No span.record("modules", ...) found in app.rs'
    )

    # module_count (or equivalent) called
    assert COUNT_CALL_RE.search(raw), "No module count call found in app.rs"


# [pr_diff] fail_to_pass
def test_project_rs_records_module_count_in_span():
    """project.rs must have a tracing span with 'modules' for the whole-app graph path."""
    lines = _lines(PROJECT_FILE)
    raw = PROJECT_FILE.read_text()

    # Tracing span with "modules" field
    span_pat = re.compile(r"(?:tracing\s*::\s*)?(?:info_span!|span!|debug_span!|trace_span!)")
    modules_field_pat = re.compile(r"\bmodules\s*=")
    span_lines = _find_lines(lines, span_pat)
    modules_lines = _find_lines(lines, modules_field_pat)
    has_span_with_modules = _any_within(span_lines, modules_lines, 3)

    instrument_pat = re.compile(r"#\[instrument\s*\([^]]*fields\s*\([^)]*modules")
    has_instrument = bool(instrument_pat.search(raw))

    assert has_span_with_modules or has_instrument, (
        "No tracing span with 'modules' field found in project.rs"
    )

    # Module count recorded
    assert re.search(r'\.record\(\s*["\']modules["\']', raw), (
        'No span.record("modules", ...) found in project.rs'
    )

    # Module count call
    assert COUNT_CALL_RE.search(raw), "No module count call found in project.rs"

    # Scoped: span/record must be near a whole-app graph function
    whole_app_pat = re.compile(r"(?:whole_app|module_graph_operation)")
    record_modules_pat = re.compile(r'\.record\(\s*["\']modules["\']')
    whole_app_lines = _find_lines(lines, whole_app_pat)
    record_lines = _find_lines(lines, record_modules_pat)
    span_modules_lines = [
        i for i in span_lines if _any_within([i], modules_lines, 3)
    ]

    near_whole_app = (
        _any_within(record_lines, whole_app_lines, 80)
        or _any_within(span_modules_lines, whole_app_lines, 80)
    )
    assert near_whole_app, (
        "modules span/record not scoped to whole-app graph code in project.rs"
    )


# [pr_diff] fail_to_pass
def test_performance_guard_before_module_count():
    """Both app.rs and project.rs must guard module count computation on span activity."""
    for path, name in [(APP_FILE, "app.rs"), (PROJECT_FILE, "project.rs")]:
        lines = _lines(path)

        guard_lines = []
        for pat in GUARD_PATTERNS:
            guard_lines.extend(_find_lines(lines, pat))
        assert guard_lines, f"{name} missing performance guard"

        count_lines = _find_lines(lines, COUNT_CALL_RE)
        record_lines = _find_lines(
            lines, re.compile(r'\.record\(\s*["\']modules["\']')
        )
        relevant_lines = count_lines + record_lines
        assert relevant_lines, f"{name} count call lines not found"

        assert _any_within(guard_lines, relevant_lines, 40), (
            f"{name} guard not near module count computation"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing functions/types preserved
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_functions_and_types_preserved():
    """Enhancement must not remove existing functions or types."""
    proj_raw = PROJECT_FILE.read_text()

    for name in ["whole_app_module_graphs", "whole_app_module_graph_operation"]:
        assert f"fn {name}" in proj_raw, f"{name} function missing from project.rs"

    assert "BaseAndFullModuleGraph" in proj_raw, (
        "BaseAndFullModuleGraph type missing from project.rs"
    )

    mod_raw = MOD_FILE.read_text()
    assert "SingleModuleGraph" in mod_raw, "SingleModuleGraph missing from mod.rs"
    assert "number_of_modules" in mod_raw, "number_of_modules field missing from mod.rs"
