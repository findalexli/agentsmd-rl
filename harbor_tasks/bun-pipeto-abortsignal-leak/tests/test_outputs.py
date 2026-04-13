"""
Task: bun-pipeto-abortsignal-leak
Repo: oven-sh/bun @ fe4a66e086bebd2c3c5a238effa801426d736278
PR:   28491

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"

ALGO_CPP = "src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp"
ALGO_H = "src/bun.js/bindings/webcore/JSAbortAlgorithm.h"
SIGNAL_CPP = "src/bun.js/bindings/webcore/AbortSignal.cpp"
SIGNAL_H = "src/bun.js/bindings/webcore/AbortSignal.h"
CUSTOM_CPP = "src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp"
TEST_FILE = "test/js/web/streams/pipeTo-signal-leak.test.ts"

TARGET_FILES = [ALGO_CPP, ALGO_H, SIGNAL_CPP, SIGNAL_H, CUSTOM_CPP]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_cpp(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Compile and run a standalone C++ program."""
    src = Path(f"{REPO}/_eval_tmp.cpp")
    bin_ = Path(f"{REPO}/_eval_tmp_bin")
    src.write_text(code)
    try:
        comp = subprocess.run(
            ["g++", "-std=c++17", "-o", str(bin_), str(src)],
            capture_output=True, text=True, timeout=timeout,
        )
        if comp.returncode != 0:
            return comp
        return subprocess.run(
            [str(bin_)], capture_output=True, text=True, timeout=timeout,
        )
    finally:
        src.unlink(missing_ok=True)
        bin_.unlink(missing_ok=True)


def _run_py(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a Python analysis script to a temp file and execute it."""
    tmp = Path(f"{REPO}/_eval_tmp.py")
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["python3", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


# Shared preamble for subprocess-based analysis scripts
_PREAMBLE = r"""
import re, sys
from pathlib import Path

def strip(s):
    s = re.sub(r"//[^\n]*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    return s

def read_stripped(path):
    return strip(Path(path).read_text())

def extract_fn_body(src, sig):
    m = re.search(sig, src)
    if not m: return None
    brace = src.find("{", m.end())
    if brace == -1: return None
    depth, end = 0, brace
    for i in range(brace, len(src)):
        if src[i] == "{": depth += 1
        elif src[i] == "}": depth -= 1
        if depth == 0: end = i; break
    return src[brace:end+1]
"""


def _check(body: str) -> subprocess.CompletedProcess:
    """Run an analysis script with the shared preamble."""
    return _run_py(_PREAMBLE + "\n" + body)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) -- target files must exist
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_target_files_exist():
    """All five target source files must exist and be non-empty."""
    for f in TARGET_FILES:
        p = Path(f"{REPO}/{f}")
        assert p.exists() and p.stat().st_size > 0, f"{f} missing or empty"


# [repo_tests] pass_to_pass -- CI: shellcheck on repo shell scripts
def test_repo_shellcheck():
    """Shell scripts in the repo must pass shellcheck validation (pass_to_pass)."""
    scripts = [
        "scripts/check-node.sh",
        "scripts/check-node-all.sh",
        "scripts/run-clang-format.sh",
    ]
    for script in scripts:
        script_path = f"{REPO}/{script}"
        if not Path(script_path).exists():
            continue
        r = subprocess.run(
            ["shellcheck", "--severity=error", script_path],
            capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, f"Shellcheck failed for {script}: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass -- CI: C++ syntax validation with clang-format
def test_repo_cpp_syntax():
    """Modified C++ files have valid syntax (clang-format can parse them) (pass_to_pass)."""
    cpp_files = [ALGO_CPP, SIGNAL_CPP, CUSTOM_CPP]
    for f in cpp_files:
        filepath = f"{REPO}/{f}"
        r = subprocess.run(
            ["clang-format", "--dry-run", filepath],
            capture_output=True, text=True, timeout=60,
        )
        # clang-format returns 0 on successful parse
        assert r.returncode == 0, f"Syntax check failed for {f}: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass -- CI: check-node scripts are syntactically valid
def test_repo_check_node_scripts():
    """Node compatibility check scripts must be syntactically valid (pass_to_pass)."""
    scripts = ["scripts/check-node.sh", "scripts/check-node-all.sh"]
    for script in scripts:
        script_path = f"{REPO}/{script}"
        if not Path(script_path).exists():
            continue
        r = subprocess.run(
            ["bash", "-n", script_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Script {script} has syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass -- CI: repo directory structure
def test_repo_structure():
    """Required repo directories and build files exist (pass_to_pass)."""
    required_paths = [
        "cmake/Globals.cmake",
        "scripts",
        "src/bun.js/bindings/webcore",
        "test/js/web/streams",
    ]
    for p in required_paths:
        full_path = f"{REPO}/{p}"
        assert Path(full_path).exists(), f"Required repo path does not exist: {p}"


# [static] pass_to_pass -- validate header structure
def test_static_header_structure_valid():
    """Header files have valid structure (pragma once or include guards) -- pass_to_pass."""
    header_files = [ALGO_H, SIGNAL_H]
    for f in header_files:
        p = Path(f"{REPO}/{f}")
        content = p.read_text()
        has_pragma = "#pragma once" in content
        has_guard = "#ifndef" in content and "#define" in content
        assert has_pragma or has_guard, f"{f} missing pragma once or include guards"


# [static] pass_to_pass -- CI: validate C++ syntax basic
def test_static_cpp_syntax_basic():
    """C++ source files have balanced braces and valid includes -- pass_to_pass."""
    cpp_files = [ALGO_CPP, SIGNAL_CPP, CUSTOM_CPP]
    for f in cpp_files:
        p = Path(f"{REPO}/{f}")
        content = p.read_text()
        open_braces = content.count("{")
        close_braces = content.count("}")
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_braces == close_braces, f"{f} has unbalanced braces"
        assert open_parens == close_parens, f"{f} has unbalanced parentheses"
        for line in content.split("\n"):
            if line.strip().startswith("#include"):
                assert "<" in line or '"' in line, f"{f} has invalid include: {line}"


# [static] pass_to_pass -- CI: validate code style patterns
def test_static_code_patterns_consistent():
    """C++ files follow repo code style (consistent indentation, no excessive tabs)."""
    for f in TARGET_FILES:
        p = Path(f"{REPO}/{f}")
        content = p.read_text()
        lines = content.split("\n")
        tab_lines = [i for i, line in enumerate(lines, 1) if "\t" in line]
        assert len(tab_lines) <= 5, f"{f} has {len(tab_lines)} lines with tabs"


# [static] pass_to_pass -- CI: repo has consistent include patterns
def test_static_include_patterns_valid():
    """C++ files use valid include syntax (angle brackets or quotes) -- pass_to_pass."""
    cpp_files = [ALGO_CPP, SIGNAL_CPP, CUSTOM_CPP]
    for f in cpp_files:
        p = Path(f"{REPO}/{f}")
        content = p.read_text()
        for line in content.split("\n"):
            if line.strip().startswith("#include"):
                assert ("<" in line and ">" in line) or ('"' in line), \
                    f"{f} has invalid include syntax: {line}"


# [static] pass_to_pass -- CI: header files have valid C++ guards
def test_static_header_guards_valid():
    """Header files have valid include guards or pragma once -- pass_to_pass."""
    header_files = [ALGO_H, SIGNAL_H]
    for f in header_files:
        p = Path(f"{REPO}/{f}")
        content = p.read_text()
        has_pragma = "#pragma once" in content
        has_guard = "#ifndef" in content and "#define" in content and "#endif" in content
        assert has_pragma or has_guard, f"{f} missing pragma once or include guards"


# ---------------------------------------------------------------------------
# Behavioral (fail_to_pass, pr_diff) -- compile and run C++ pattern validation
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_cpp_pattern_compiles():
    """Compile and run a standalone C++ program that validates the weak
    callback null-guard, locked container, and memory-cost-accounting patterns
    used in the fix.  This proves the fix approach is sound."""
    r = _run_cpp(r"""
#include <cassert>
#include <iostream>
#include <memory>
#include <mutex>
#include <vector>
#include <cstdint>

struct CallbackData {
    virtual ~CallbackData() = default;
    virtual void call() = 0;
};

struct WeakCallbackRef {
    CallbackData* ptr = nullptr;
    CallbackData* callback() { return ptr; }
    void visitJSFunction() { }
};

struct AbortAlgorithm {
    WeakCallbackRef* m_data;
    int handleEvent() {
        auto* cb = m_data->callback();
        if (!cb) return -1;
        cb->call();
        return 0;
    }
    void visitJSFunction() { m_data->visitJSFunction(); }
};

template<typename T>
struct LockedContainer {
    std::mutex m_lock;
    std::vector<std::pair<uint32_t, T>> m_items;
    void append(uint32_t id, T val) {
        std::lock_guard<std::mutex> g(m_lock);
        m_items.push_back({id, val});
    }
    bool removeFirstMatching(uint32_t id) {
        std::lock_guard<std::mutex> g(m_lock);
        for (auto it = m_items.begin(); it != m_items.end(); ++it)
            if (it->first == id) { m_items.erase(it); return true; }
        return false;
    }
    size_t sizeInBytes() const {
        return m_items.size() * sizeof(std::pair<uint32_t, T>);
    }
};

struct ConcreteCB : CallbackData {
    bool called = false;
    void call() override { called = true; }
};

int main() {
    WeakCallbackRef null_ref;
    AbortAlgorithm algo_null{&null_ref};
    assert(algo_null.handleEvent() == -1);

    ConcreteCB cb;
    WeakCallbackRef live_ref;
    live_ref.ptr = &cb;
    AbortAlgorithm algo_live{&live_ref};
    assert(algo_live.handleEvent() == 0);
    assert(cb.called);

    live_ref.ptr = nullptr;
    assert(algo_live.handleEvent() == -1);

    LockedContainer<int> c;
    c.append(1, 10);
    c.append(2, 20);
    assert(c.sizeInBytes() == 2 * sizeof(std::pair<uint32_t, int>));
    assert(c.removeFirstMatching(1));
    assert(!c.removeFirstMatching(99));
    assert(c.sizeInBytes() == 1 * sizeof(std::pair<uint32_t, int>));

    algo_live.visitJSFunction();

    std::cout << "ALL_TESTS_PASSED" << std::endl;
    return 0;
}
""")
    assert r.returncode == 0, f"C++ pattern test failed: {r.stderr}"
    assert "ALL_TESTS_PASSED" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- structural checks via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_weak_ref_replaces_strong():
    """JSAbortAlgorithm must not use JSCallbackDataStrong; a weak callback
    mechanism must be present in both .cpp and .h, used in member/constructor."""
    r = _check(r"""
cpp = read_stripped("src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp")
h   = read_stripped("src/bun.js/bindings/webcore/JSAbortAlgorithm.h")

for label, text in [(".cpp", cpp), (".h", h)]:
    if re.search(r"\bJSCallbackDataStrong\b", text):
        sys.exit(f"FAIL: JSCallbackDataStrong still in {label}")

weak = [r"\bJSCallbackDataWeak\b", r"\bWeakPtr\b", r"\bWeak<",
        r"\bweakCallback\b", r"\bJSWeakValue\b"]
if not any(re.search(p, cpp) or re.search(p, h) for p in weak):
    sys.exit("FAIL: no weak callback mechanism found")

combined = cpp + "\n" + h
if not re.search(r"(?:m_data|new\s+JSCallbackDataWeak|JSCallbackDataWeak\s*\*\s*m_)", combined):
    sys.exit("FAIL: weak type not used in member/constructor context")
print("PASS")
""")
    assert r.returncode == 0, f"Weak ref check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_gc_visitor_in_abort_algorithm():
    """JSAbortAlgorithm must have a GC visitor method that delegates to m_data."""
    r = _check(r"""
header = read_stripped("src/bun.js/bindings/webcore/JSAbortAlgorithm.h")
cpp    = read_stripped("src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp")

if not re.search(r"(?:void|template)\s+.*(?:visit|trace|mark)\w*\s*\([^)]*(?:Visitor|Slot)",
                 header, re.IGNORECASE):
    sys.exit("FAIL: no visitor declaration in JSAbortAlgorithm.h")

body = extract_fn_body(
    cpp,
    r"JSAbortAlgorithm::\w*(?:visit|trace|mark)\w*\s*\([^)]*(?:Visitor|Slot)[^)]*\)",
)
if body is None:
    sys.exit("FAIL: no visitor method implementation in JSAbortAlgorithm.cpp")
if not re.search(r"m_data\s*->\s*\w*(?:visit|trace|mark)", body, re.IGNORECASE):
    sys.exit("FAIL: visitor does not delegate to m_data")
print("PASS")
""")
    assert r.returncode == 0, f"GC visitor check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_handle_event_null_guard():
    """handleEvent must guard against a GC-collected weak callback (null check)."""
    r = _check(r"""
cpp  = read_stripped("src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp")
body = extract_fn_body(cpp, r"JSAbortAlgorithm::handleEvent")
if body is None:
    sys.exit("FAIL: handleEvent method not found")

guards = [
    r"!\s*\w*callback",
    r"callback\w*\s*==\s*nullptr",
    r"nullptr\s*==\s*\w*callback",
    r"!\s*m_data",
    r"callback\w*\.has_value",
    r"if\s*\(\s*!\s*\w*callback",
]
if not any(re.search(g, body, re.IGNORECASE) for g in guards):
    sys.exit("FAIL: no null/validity guard in handleEvent")

code_lines = [l.strip() for l in body.split("\n")
              if l.strip() and l.strip() not in ("{", "}")]
if len(code_lines) < 3:
    sys.exit("FAIL: handleEvent body is trivial (stub)")
print("PASS")
""")
    assert r.returncode == 0, f"Null guard check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_abort_signal_typed_container():
    """AbortSignal must store abort algorithms in a GC-visible typed container
    (separate from type-erased m_algorithms) with visitor declared and implemented."""
    r = _check(r"""
header = read_stripped("src/bun.js/bindings/webcore/AbortSignal.h")
cpp    = read_stripped("src/bun.js/bindings/webcore/AbortSignal.cpp")

container_patterns = [
    r"(?:Vector|HashMap|Deque|std::vector|std::unordered_map|std::map|std::deque|std::list)\s*<[^>]*AbortAlgorithm",
    r"(?:Vector|HashMap|Deque|std::vector)\s*<[^>]*Ref\s*<\s*AbortAlgorithm",
]
if not any(re.search(p, header) for p in container_patterns):
    sys.exit("FAIL: no typed AbortAlgorithm container in AbortSignal.h")

visitor_decl_patterns = [
    r"(?:visit|trace|mark)\w*(?:Abort|Algorithm|Callback)\w*\s*\(",
    r"template\s*<\s*typename\s+\w+\s*>\s*void\s+\w*(?:visit|trace)\w*",
]
if not any(re.search(p, header, re.IGNORECASE) for p in visitor_decl_patterns):
    sys.exit("FAIL: no visitor declaration in AbortSignal.h")

if not re.search(r"AbortSignal::\w*(?:visit|trace)\w*(?:Abort|Algorithm|Callback)",
                 cpp, re.IGNORECASE):
    sys.exit("FAIL: no visitor implementation in AbortSignal.cpp")
print("PASS")
""")
    assert r.returncode == 0, f"Typed container check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_thread_safety():
    """Abort algorithm storage must be synchronized -- lock member + >= 2 lock usages."""
    r = _check(r"""
header = read_stripped("src/bun.js/bindings/webcore/AbortSignal.h")
cpp    = read_stripped("src/bun.js/bindings/webcore/AbortSignal.cpp")

lock_member_patterns = [
    r"\b(?:Lock|Mutex|std::mutex|std::shared_mutex|RecursiveLock|SpinLock)\b\s+m_\w*",
    r"m_\w*(?:Lock|Mutex|lock|mutex)\b",
    r"WTF_GUARDED_BY_LOCK",
    r"\bstd::atomic\b.*m_\w*",
]
if not any(re.search(p, header) for p in lock_member_patterns):
    sys.exit("FAIL: no lock/mutex member in AbortSignal.h")

lock_usage_patterns = [
    r"\bLocker\b", r"\block_guard\b", r"\bunique_lock\b",
    r"\bscoped_lock\b", r"\.lock\(\)", r"\.acquire\(\)",
    r"\bLockHolder\b", r"\bAutoLocker\b",
]
lock_uses = sum(len(re.findall(p, cpp)) for p in lock_usage_patterns)
if lock_uses < 2:
    sys.exit(f"FAIL: only {lock_uses} lock usage(s) in AbortSignal.cpp, need >= 2")
print("PASS")
""")
    assert r.returncode == 0, f"Thread safety check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_gc_visitor_walks_algorithms():
    """JSAbortSignal's GC visitor must call through to AbortSignal's algorithm
    visitor to keep weak callbacks alive."""
    r = _check(r"""
custom = read_stripped("src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp")

body = extract_fn_body(
    custom,
    r"(?:visitAdditionalChildren|visitChildren|visitOutputConstraints|trace)\w*"
    r"\s*\([^)]*(?:Visitor|Slot)[^)]*\)",
)
if body is None:
    sys.exit("FAIL: no GC visitor method in JSAbortSignalCustom.cpp")

calls_algo_visitor = re.search(
    r"(?:visit|trace|mark)\w*(?:Abort|Algorithm|Callback)", body, re.IGNORECASE)
direct_iteration = re.search(
    r"for\s*\(.*(?:abort|algorithm)", body, re.IGNORECASE)
if not (calls_algo_visitor or direct_iteration):
    sys.exit("FAIL: GC visitor does not walk abort algorithms")
print("PASS")
""")
    assert r.returncode == 0, f"GC visitor walk check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_typed_storage_path():
    """addAbortAlgorithmToSignal must store AbortAlgorithm in the new typed
    container, NOT erase it into a lambda via the old addAlgorithm() path."""
    r = _check(r"""
cpp  = read_stripped("src/bun.js/bindings/webcore/AbortSignal.cpp")
body = extract_fn_body(cpp, r"addAbortAlgorithmToSignal")
if body is None:
    sys.exit("FAIL: addAbortAlgorithmToSignal not found")

if re.search(r"\b(?<!Abort)addAlgorithm\s*\(", body):
    sys.exit("FAIL: still calls old addAlgorithm (type erasure)")

if not re.search(r"(?:append|push_back|emplace_back|emplace|insert|add)\s*\(", body):
    sys.exit("FAIL: no container insertion found")

code_lines = [l.strip() for l in body.split("\n")
              if l.strip() and l.strip() not in ("{", "}")]
if len(code_lines) < 3:
    sys.exit("FAIL: addAbortAlgorithmToSignal body is trivial")
print("PASS")
""")
    assert r.returncode == 0, f"Typed storage check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_remove_uses_new_container():
    """removeAbortAlgorithmFromSignal must operate on the new typed container
    with proper locking, NOT delegate to the old removeAlgorithm()."""
    r = _check(r"""
cpp  = read_stripped("src/bun.js/bindings/webcore/AbortSignal.cpp")
body = extract_fn_body(cpp, r"removeAbortAlgorithmFromSignal")
if body is None:
    sys.exit("FAIL: removeAbortAlgorithmFromSignal not found")

if re.search(r"\b(?<!Abort)removeAlgorithm\s*\(", body):
    sys.exit("FAIL: still calls old removeAlgorithm")

lock_patterns = [r"\bLocker\b", r"\block_guard\b", r"\bunique_lock\b",
                 r"\bscoped_lock\b", r"\.lock\(\)", r"\bLockHolder\b"]
if not any(re.search(p, body) for p in lock_patterns):
    sys.exit("FAIL: no lock usage in removeAbortAlgorithmFromSignal")

if not re.search(r"(?:removeFirstMatching|remove_if|erase|removeAll)\s*\(", body):
    sys.exit("FAIL: no container removal in removeAbortAlgorithmFromSignal")
print("PASS")
""")
    assert r.returncode == 0, f"Remove container check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_memory_cost_includes_new_container():
    """memoryCost must account for the new abort algorithms container size."""
    r = _check(r"""
cpp  = read_stripped("src/bun.js/bindings/webcore/AbortSignal.cpp")
body = extract_fn_body(cpp, r"AbortSignal::memoryCost")
if body is None:
    sys.exit("FAIL: memoryCost not found")

if not re.search(r"m_abort\w*\s*\.\s*(?:sizeInBytes|size|capacity|byteSize)", body):
    sys.exit("FAIL: memoryCost does not account for new abort algorithms container")
print("PASS")
""")
    assert r.returncode == 0, f"Memory cost check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- from bindings AGENTS.md and test/AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass -- src/bun.js/bindings/v8/AGENTS.md:230 @ fe4a66e
def test_visit_children_for_gc_objects():
    """Custom heap objects holding GC references must implement visitChildren
    or equivalent visitor. Both JSAbortAlgorithm and AbortSignal must have
    visitor methods since they hold GC-managed references."""
    r = _check(r"""
algo_h   = read_stripped("src/bun.js/bindings/webcore/JSAbortAlgorithm.h")
signal_h = read_stripped("src/bun.js/bindings/webcore/AbortSignal.h")
custom   = read_stripped("src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp")

if not re.search(r"(?:visit|trace)\w*\s*\([^)]*(?:Visitor|Slot)", algo_h):
    sys.exit("FAIL: JSAbortAlgorithm.h missing visitor declaration for GC callback")

if not re.search(r"(?:visit|trace)\w*(?:Abort|Algorithm)\w*\s*\(", signal_h):
    sys.exit("FAIL: AbortSignal.h missing visitor for abort algorithm container")

if not re.search(r"(?:visit|trace)\w*(?:Abort|Algorithm)", custom, re.IGNORECASE):
    sys.exit("FAIL: JSAbortSignalCustom.cpp GC visitor not wired to algorithm visitor")
print("PASS")
""")
    assert r.returncode == 0, f"Visit children check failed: {r.stdout or r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass -- test/AGENTS.md:21 @ fe4a66e
def test_file_no_settimeout():
    """Regression test file must exist and must not use setTimeout.

    Rule: 'Do not write flaky tests. Never wait for time to pass in tests.'
    Source: test/AGENTS.md:21
    """
    p = Path(f"{REPO}/{TEST_FILE}")
    assert p.exists(), f"Regression test file {TEST_FILE} missing"
    content = p.read_text()
    assert "setTimeout" not in content, (
        "Test file uses setTimeout -- use Bun.sleep() or await a condition instead"
    )


# [agent_config] fail_to_pass -- test/AGENTS.md:218 @ fe4a66e
def test_file_module_scope_imports():
    """Regression test file must use module-scope static imports only,
    not dynamic import() calls inside test function bodies.

    Rule: 'Only use dynamic import or require when the test is specifically
    testing something related to dynamic import or require.'
    Source: test/AGENTS.md:218
    """
    p = Path(f"{REPO}/{TEST_FILE}")
    assert p.exists(), f"Regression test file {TEST_FILE} missing"
    content = p.read_text()
    import re
    assert not re.search(r"\bawait\s+import\s*\(", content), (
        "Test file uses dynamic import() -- use module-scope import statements instead"
    )
    assert not re.search(r"\brequire\s*\(", content), (
        "Test file uses require() -- use module-scope import statements instead"
    )
