"""
Task: bun-capturestacktrace-async-frames
Repo: oven-sh/bun @ 9804f55e762ada50e595e693361e3ed770d7796a
PR:   #28651

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a C++ task (requires Bun's full build toolchain: Zig, CMake,
JavaScriptCore/WebKit) so tests inspect source code rather than calling it.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
CPP_FILE = Path(REPO) / "src/bun.js/bindings/ErrorStackTrace.cpp"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_cpp_noise(code: str) -> str:
    """Remove C/C++ comments and string literals, leaving only real code."""
    pattern = (
        r"//[^\n]*"
        r"|/\*.*?\*/"
        r'|"(?:[^"\\]|\\.)*"'
        r"|'(?:[^'\\]|\\.)*'"
    )
    return re.sub(pattern, " ", code, flags=re.DOTALL)


def _extract_func(text: str, fname: str) -> str | None:
    """Extract body of a JSCStackTrace member function by name."""
    pat = (
        r"void\s+JSCStackTrace::" + fname +
        r"\b(.*?)(?=\n\w+\s+JSCStackTrace::|\nJSCStackTrace\s+JSCStackTrace::|\Z)"
    )
    m = re.search(pat, text, re.DOTALL)
    return m.group(1) if m else None


def _get_func_body(fname: str = "getFramesForCaller") -> str:
    """Read the file and extract a function body, stripping comments."""
    text = CPP_FILE.read_text()
    body = _extract_func(text, fname)
    assert body is not None, f"{fname} not found in {CPP_FILE}"
    return _strip_cpp_noise(body)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_file_exists():
    """ErrorStackTrace.cpp must exist and be non-empty."""
    assert CPP_FILE.exists(), f"{CPP_FILE} does not exist"
    assert CPP_FILE.stat().st_size > 0, f"{CPP_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_delegates_to_async_aware_collector():
    """getFramesForCaller must call getStackTrace (async-aware) instead of
    the old hand-rolled StackVisitor::visit walk for main frame collection."""
    clean = _get_func_body()
    uses_async_collector = bool(re.search(r'\bgetStackTrace\s*\(', clean))
    has_old_walk = bool(re.search(r'StackVisitor\s*::\s*visit\s*\(\s*callFrame', clean))
    assert uses_async_collector, "Must delegate to async-aware getStackTrace"
    assert not has_old_walk, "Must not retain old StackVisitor::visit(callFrame walk"


# [pr_diff] fail_to_pass
def test_async_frame_boundary_in_caller_search():
    """When scanning frames to find the caller, must stop at async frame
    boundaries (isAsyncFrame) because resumed async functions have a
    different callee cell."""
    clean = _get_func_body()
    has_async_guard = bool(re.search(
        r'(?:if|while|for)\s*\([^)]*isAsyncFrame|isAsyncFrame[^;]*(?:break|return|continue)',
        clean
    )) or bool(re.search(r'isAsyncFrame\s*\(\s*\)', clean))
    assert has_async_guard, "Must handle async frame boundary in caller search"


# [pr_diff] fail_to_pass
def test_stack_trace_limit_after_caller_removal():
    """stackTraceLimit must be applied to final visible frames AFTER caller
    removal, not during raw collection (which would lose deep frames)."""
    clean = _get_func_body()

    # Approach A: explicit removal before limit
    remove_matches = list(re.finditer(r'removeAt|erase\s*\(|remove\s*\(', clean))
    limit_matches = list(re.finditer(r'shrink\s*\(|resize\s*\(|stackTraceLimit', clean))

    approach_a = False
    if remove_matches and limit_matches:
        last_remove = max(m.start() for m in remove_matches)
        last_limit = max(m.start() for m in limit_matches)
        approach_a = last_limit > last_remove

    # Approach B: collect without cap, then limit afterwards
    approach_b = (
        bool(re.search(r'max\s*\(|numeric_limits|SIZE_MAX|UINT_MAX', clean))
        and bool(re.search(r'shrink|resize', clean))
    )

    assert approach_a or approach_b, (
        "stackTraceLimit must be applied after caller removal"
    )


# [pr_diff] fail_to_pass
def test_interpreter_header_included():
    """The fix delegates to vm.interpreter.getStackTrace which requires the
    Interpreter.h header — must be included."""
    text = CPP_FILE.read_text()
    assert re.search(
        r'#\s*include\s*<\s*JavaScriptCore/Interpreter\.h\s*>', text
    ), "Must #include <JavaScriptCore/Interpreter.h> for getStackTrace"


# [pr_diff] pass_to_pass
def test_post_filter_implementation_visibility():
    """Must filter frames with isImplementationVisibilityPrivate (present in
    both old and new code — regression guard)."""
    clean = _get_func_body()
    has_filter = bool(re.search(r'isImplementationVisibilityPrivate\s*\(', clean))
    assert has_filter, "Must filter frames with isImplementationVisibilityPrivate"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_function_signature_preserved():
    """getFramesForCaller function signature must be preserved."""
    text = CPP_FILE.read_text()
    assert re.search(
        r'void\s+JSCStackTrace::getFramesForCaller\s*\(\s*JSC::VM\s*&', text
    ), "getFramesForCaller signature is missing or altered"


# [pr_diff] pass_to_pass
def test_sibling_functions_preserved():
    """Other functions in ErrorStackTrace.cpp must not be deleted."""
    text = CPP_FILE.read_text()
    required = [
        r'JSCStackTrace\s+JSCStackTrace::fromExisting',
        r'JSCStackTrace\s+JSCStackTrace::getStackTraceForThrownValue',
        r'JSCStackTrace\s+JSCStackTrace::captureCurrentJSStackTrace',
    ]
    for pat in required:
        assert re.search(pat, text), f"Sibling function matching {pat!r} is missing"


# [pr_diff] pass_to_pass
def test_caller_dual_matching():
    """Caller matching must support both cell identity and name-based matching
    (for resumed async frames with different callee cells)."""
    clean = _get_func_body()
    has_cell_cmp = bool(re.search(r'callee\s*\(\s*\)\s*==|==\s*caller', clean))
    has_name_cmp = bool(re.search(r'functionName|callerName|name\s*\(\s*\)', clean))
    assert has_cell_cmp, "Must have cell identity comparison for caller matching"
    assert has_name_cmp, "Must have name-based comparison for caller matching"


# [static] pass_to_pass
def test_not_stub():
    """getFramesForCaller must have substantial non-trivial implementation
    (>= 20 real code lines, >= 2 control-flow, >= 5 function calls)."""
    text = CPP_FILE.read_text()
    body = _extract_func(text, "getFramesForCaller")
    assert body is not None, "getFramesForCaller not found"

    real_lines = []
    for line in body.strip().split("\n"):
        s = line.strip()
        if not s or s.startswith("//") or s.startswith("/*") or s.startswith("*"):
            continue
        if re.match(r'^auto\s+\w+\s*=\s*\d+\s*;$', s):
            continue
        if s in ("{", "}", "};"):
            continue
        real_lines.append(s)

    control_flow = [l for l in real_lines if re.search(r'\b(for|while|if)\s*\(', l)]
    func_calls = [l for l in real_lines if re.search(r'\w+\s*\(', l)]

    assert len(real_lines) >= 20, f"Only {len(real_lines)} real lines, need >= 20"
    assert len(control_flow) >= 2, f"Only {len(control_flow)} control-flow stmts, need >= 2"
    assert len(func_calls) >= 5, f"Only {len(func_calls)} function calls, need >= 5"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:245 @ 9804f55e762ada50e595e693361e3ed770d7796a
def test_no_tabs_in_function():
    """Bun C++ uses 4-space indentation. getFramesForCaller must not
    introduce tabs (CLAUDE.md: 'Follow existing code style')."""
    text = CPP_FILE.read_text()
    m = re.search(
        r'void\s+JSCStackTrace::getFramesForCaller\b(.*?)(?=\n\w+\s+JSCStackTrace::|\nJSCStackTrace\s+JSCStackTrace::|\Z)',
        text, re.DOTALL,
    )
    assert m, "getFramesForCaller not found"
    assert "\t" not in m.group(1), "Tabs found in function body — use 4-space indent"


# [agent_config] pass_to_pass — .claude/skills/implementing-jsc-classes-cpp/SKILL.md:184 @ 9804f55e762ada50e595e693361e3ed770d7796a
def test_root_h_included():
    """C++ files must include root.h at the top (Bun convention)."""
    text = CPP_FILE.read_text()
    assert re.search(
        r'#\s*include\s*"root\.h"', text
    ), 'Must #include "root.h" at the top of C++ files'
