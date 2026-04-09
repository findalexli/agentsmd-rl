"""
Task: bun-capturestacktrace-async-frames
Repo: oven-sh/bun @ 9804f55e762ada50e595e693361e3ed770d7796a
PR:   #28651

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a C++ task (requires Bun's full build toolchain: Zig, CMake,
JavaScriptCore/WebKit) so tests inspect source code rather than calling it.
All f2p tests use subprocess.run() to execute analysis scripts.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
CPP_FILE = Path(REPO) / "src/bun.js/bindings/ErrorStackTrace.cpp"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_func_body(fname: str = "getFramesForCaller") -> str | None:
    """Extract body of a JSCStackTrace member function by name."""
    text = CPP_FILE.read_text()
    pat = rf"void\s+JSCStackTrace::{fname}\b"
    m = re.search(pat, text)
    if not m:
        return None
    start = m.start()
    end_pat = r"\n\w+\s+JSCStackTrace::|\nJSCStackTrace\s+JSCStackTrace::"
    end_m = re.search(end_pat, text[m.end():])
    if end_m:
        return text[start:m.end() + end_m.start()]
    return text[start:]


def _strip_noise(code: str) -> str:
    """Remove C/C++ comments and string literals, leaving only real code."""
    pattern = (
        r"//[^\n]*"
        r"|/\*.*?\*/"
        r'|"(?:[^"\\]|\\.)*"'
        r"|'(?:[^'\\]|\\.)*'"
    )
    return re.sub(pattern, " ", code, flags=re.DOTALL)


def _get_clean_func(fname: str = "getFramesForCaller") -> str:
    """Read the file and extract a function body, stripping comments."""
    text = CPP_FILE.read_text()
    body = _extract_func_body(fname)
    assert body is not None, f"{fname} not found in {CPP_FILE}"
    return _strip_noise(body)


def _run_analysis(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_file_exists():
    """ErrorStackTrace.cpp must exist and be non-empty."""
    assert CPP_FILE.exists(), f"{CPP_FILE} does not exist"
    assert CPP_FILE.stat().st_size > 0, f"{CPP_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_delegates_to_interpreter_getStackTrace():
    """getFramesForCaller must delegate to vm.interpreter.getStackTrace
    (async-aware) instead of the old hand-rolled StackVisitor::visit walk."""
    r = _run_analysis(f'''
import re, sys
text = open("{CPP_FILE}").read()
m = re.search(r"void\\s+JSCStackTrace::getFramesForCaller\\b", text)
if not m:
    print("FAIL:function_not_found"); sys.exit(0)
body = text[m.end():m.end()+5000]
# Core behavioral change: must call vm.interpreter.getStackTrace
if not re.search(r"vm\\.interpreter\\.getStackTrace", body):
    print("FAIL:no_interpreter_getStackTrace"); sys.exit(0)
# Must NOT use the old StackVisitor::visit(callFrame) pattern
if re.search(r"StackVisitor\\s*::\\s*visit\\s*\\(\\s*callFrame", body):
    print("FAIL:old_stack_visitor_walk"); sys.exit(0)
print("PASS")
''')
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Delegation check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_interpreter_header_included():
    """The fix delegates to vm.interpreter.getStackTrace which requires the
    Interpreter.h header -- must be included."""
    r = _run_analysis(f'''
import re, sys
text = open("{CPP_FILE}").read()
if re.search(r"#\\s*include\\s*<\\s*JavaScriptCore/Interpreter\\.h\\s*>", text):
    print("PASS")
else:
    print("FAIL:no_interpreter_header")
''')
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Header check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_async_frame_boundary_in_caller_search():
    """When scanning frames to find the caller, must stop at async frame
    boundaries (isAsyncFrame) because resumed async functions have a
    different callee cell."""
    r = _run_analysis(f'''
import re, sys
text = open("{CPP_FILE}").read()
m = re.search(r"void\\s+JSCStackTrace::getFramesForCaller\\b", text)
if not m:
    print("FAIL:function_not_found"); sys.exit(0)
body = text[m.end():m.end()+5000]
# Must use isAsyncFrame to detect async boundaries
if not re.search(r"isAsyncFrame\\s*\\(", body):
    print("FAIL:no_async_frame_check"); sys.exit(0)
# Must use it as a boundary that stops scanning (break)
if not re.search(r"isAsyncFrame", body):
    print("FAIL:no_async_check"); sys.exit(0)
# Verify isAsyncFrame is in a context with break (loop body)
clean = re.sub(r"//[^\\n]*", "", body)
if not re.search(r"isAsyncFrame\\s*\\(\\s*\\)\\s*\\)\\s*break", clean):
    # Try multiline: isAsyncFrame() ... break on next line
    lines = clean.split("\\n")
    found = False
    for i, line in enumerate(lines):
        if "isAsyncFrame" in line and "if" in line:
            for j in range(i, min(i+3, len(lines))):
                if "break" in lines[j]:
                    found = True
                    break
            if found:
                break
    if not found:
        print("FAIL:async_check_no_break"); sys.exit(0)
print("PASS")
''')
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Async boundary check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_stack_trace_limit_after_caller_removal():
    """stackTraceLimit must be applied to final visible frames AFTER caller
    removal (shrink), not during raw collection."""
    r = _run_analysis(f'''
import re, sys
text = open("{CPP_FILE}").read()
m = re.search(r"void\\s+JSCStackTrace::getFramesForCaller\\b", text)
if not m:
    print("FAIL:function_not_found"); sys.exit(0)
body = text[m.end():m.end()+5000]

# The fix collects without limit (numeric_limits<size_t>::max()),
# removes caller frames with removeAt, then applies shrink(stackTraceLimit)
has_uncapped_collect = bool(
    re.search(r"numeric_limits|SIZE_MAX|UINT_MAX", body)
)
# Look for removeAt followed by shrink
remove_matches = list(re.finditer(r"removeAt\\s*\\(", body))
shrink_matches = list(re.finditer(r"shrink\\s*\\(", body))

if remove_matches and shrink_matches:
    last_remove = max(m_match.start() for m_match in remove_matches)
    has_post_shrink = any(
        sm.start() > last_remove
        for sm in shrink_matches
    )
    if has_post_shrink and has_uncapped_collect:
        print("PASS")
    elif has_post_shrink:
        print("PASS")
    else:
        print("FAIL:no_uncapped_collect")
else:
    print("FAIL:no_removeAt_shrink_pattern")
''')
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Limit order check failed: {r.stdout.strip()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_post_filter_implementation_visibility():
    """Must filter frames with isImplementationVisibilityPrivate (present in
    both old and new code -- regression guard)."""
    clean = _get_clean_func()
    has_filter = bool(re.search(r'isImplementationVisibilityPrivate\s*\(', clean))
    assert has_filter, "Must filter frames with isImplementationVisibilityPrivate"


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
    ]
    for pat in required:
        assert re.search(pat, text), f"Sibling function matching {pat!r} is missing"


# [pr_diff] pass_to_pass
def test_caller_dual_matching():
    """Caller matching must support both cell identity and name-based matching
    (for resumed async frames with different callee cells)."""
    clean = _get_clean_func()
    has_cell_cmp = bool(re.search(r'callee\s*\(\s*\)\s*==|==\s*callerObject', clean))
    has_name_cmp = bool(re.search(r'functionName|callerName|Zig::functionName', clean))
    assert has_cell_cmp, "Must have cell identity comparison for caller matching"
    assert has_name_cmp, "Must have name-based comparison for caller matching"


# [static] pass_to_pass
def test_not_stub():
    """getFramesForCaller must have substantial non-trivial implementation
    (>= 20 real code lines, >= 2 control-flow, >= 5 function calls)."""
    text = CPP_FILE.read_text()
    body = _extract_func_body()
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
# Config-derived (agent_config) -- rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- CLAUDE.md:245 @ 9804f55e762ada50e595e693361e3ed770d7796a
def test_no_tabs_in_function():
    """Bun C++ uses 4-space indentation. getFramesForCaller must not
    introduce tabs (CLAUDE.md: 'Follow existing code style')."""
    text = CPP_FILE.read_text()
    m = re.search(
        r'void\s+JSCStackTrace::getFramesForCaller\b(.*?)(?=\n\w+\s+JSCStackTrace::|\nJSCStackTrace\s+JSCStackTrace::|\Z)',
        text, re.DOTALL,
    )
    assert m, "getFramesForCaller not found"
    assert "\t" not in m.group(1), "Tabs found in function body -- use 4-space indent"


# [agent_config] pass_to_pass -- CLAUDE.md:245 @ 9804f55e762ada50e595e693361e3ed770d7796a
def test_config_h_included():
    """ErrorStackTrace.cpp must include config.h at the top (file convention)."""
    text = CPP_FILE.read_text()
    assert re.search(
        r'#\s*include\s*"config\.h"', text
    ), 'Must #include "config.h" at the top (existing file convention)'


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass) -- must pass on both base commit and fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass -- CI: format.yml (clang-format)
def test_cpp_file_clang_format():
    """ErrorStackTrace.cpp must pass clang-format check (pass_to_pass).

    Repo CI enforces C++ formatting via .clang-format with WebKit style.
    This ensures the fix maintains repo formatting standards.
    """
    import subprocess

    # Install clang-format from apt (provides clang-format-19 and clang-format symlink)
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, timeout=60
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "--no-install-recommends", "clang-format"],
        capture_output=True, timeout=120
    )

    # Find available clang-format binary
    clang_format_bin = None
    for bin_name in ["clang-format", "clang-format-19"]:
        result = subprocess.run([bin_name, "--version"], capture_output=True)
        if result.returncode == 0:
            clang_format_bin = bin_name
            break

    if not clang_format_bin:
        # Skip if clang-format can't be installed (no pytest dependency)
        return

    # Run clang-format check on the specific file
    r = subprocess.run(
        [clang_format_bin, "--dry-run", "--Werror", str(CPP_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"clang-format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass -- CI: lint.yml (code quality checks)
def test_cpp_file_basic_structure():
    """ErrorStackTrace.cpp must have valid C++ structure.

    Basic validation to catch obvious errors: has includes, no double semicolons.
    Note: Brace counting is not reliable due to comments/strings.
    """
    text = CPP_FILE.read_text()
    # Must have includes
    assert '#include' in text, "No includes found in C++ file"
    # Must not have obvious syntax errors (skip for (;;))
    # Remove common patterns that have ;; legitimately
    cleaned = text.replace("for (;;)", "for ()")
    # Remove comments before checking for ;;
    cleaned = re.sub(r'//[^\n]*', '', cleaned)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
    assert ";;" not in cleaned, "Double semicolons found outside of for(;;)"


# [repo_tests] pass_to_pass -- CI: format.yml + lint.yml
def test_repo_configs_exist():
    """Repository configuration files must exist.

    Checks that lint and format configs exist and are non-empty.
    Note: oxlint.json may contain comments (JSON5), so we only check existence.
    """
    # Check oxlint config exists and is non-empty
    oxlint_config = Path(REPO) / "oxlint.json"
    assert oxlint_config.exists(), "oxlint.json config file must exist"
    assert oxlint_config.stat().st_size > 0, "oxlint.json is empty"

    # Check prettier config exists and is non-empty
    prettierrc = Path(REPO) / ".prettierrc"
    assert prettierrc.exists(), ".prettierrc config file must exist"
    assert prettierrc.stat().st_size > 0, ".prettierrc is empty"

    # Check .clang-tidy exists (actual file in repo, not .clang-format)
    clang_tidy = Path(REPO) / ".clang-tidy"
    assert clang_tidy.exists(), ".clang-tidy config file must exist"
    assert clang_tidy.stat().st_size > 0, ".clang-tidy is empty"
