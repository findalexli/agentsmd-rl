"""
Task: bun-pipeto-abortsignal-leak
Repo: oven-sh/bun @ fe4a66e086bebd2c3c5a238effa801426d736278
PR:   28491

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a C++ task requiring the full Bun build system (Zig, JSC, CMake)
to compile and run. Tests must inspect source code structurally.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"

TEST_FILE = "test/js/web/streams/pipeTo-signal-leak.test.ts"

ALGO_CPP = "src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp"
ALGO_H = "src/bun.js/bindings/webcore/JSAbortAlgorithm.h"
SIGNAL_CPP = "src/bun.js/bindings/webcore/AbortSignal.cpp"
SIGNAL_H = "src/bun.js/bindings/webcore/AbortSignal.h"
CUSTOM_CPP = "src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp"


def strip_comments(src: str) -> str:
    """Strip C/C++ line and block comments to prevent comment-injection gaming."""
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


def read_stripped(relpath: str) -> str:
    return strip_comments(Path(f"{REPO}/{relpath}").read_text())


def extract_function_body(src: str, signature_pattern: str) -> str | None:
    """Extract the body of a C++ function matching signature_pattern."""
    m = re.search(signature_pattern, src)
    if not m:
        return None
    brace = src.find("{", m.end())
    if brace == -1:
        return None
    depth, end = 0, brace
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        if depth == 0:
            end = i
            break
    return src[brace : end + 1]


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — target files must exist
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_target_files_exist():
    """All five target source files must exist and be non-empty."""
    for f in [ALGO_CPP, ALGO_H, SIGNAL_CPP, SIGNAL_H, CUSTOM_CPP]:
        p = Path(f"{REPO}/{f}")
        assert p.exists() and p.stat().st_size > 0, f"{f} missing or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: break the strong ref cycle
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_weak_ref_replaces_strong():
    """JSAbortAlgorithm must not use JSCallbackDataStrong; a weak mechanism must
    be present in both .cpp and .h, used in a member or constructor context."""
    cpp = read_stripped(ALGO_CPP)
    header = read_stripped(ALGO_H)

    # Strong ref must be gone
    assert not re.search(r"\bJSCallbackDataStrong\b", cpp), \
        "JSCallbackDataStrong still in JSAbortAlgorithm.cpp"
    assert not re.search(r"\bJSCallbackDataStrong\b", header), \
        "JSCallbackDataStrong still in JSAbortAlgorithm.h"

    # Some weak/non-strong mechanism must be present
    weak_patterns = [
        r"\bJSCallbackDataWeak\b",
        r"\bWeakPtr\b",
        r"\bWeak<",
        r"\bweakCallback\b",
        r"\bJSWeakValue\b",
    ]
    has_weak_cpp = any(re.search(p, cpp) for p in weak_patterns)
    has_weak_h = any(re.search(p, header) for p in weak_patterns)
    assert has_weak_cpp or has_weak_h, "No weak callback mechanism found"

    # Anti-stub: weak type must be in member decl or constructor, not just floating
    combined = cpp + "\n" + header
    assert re.search(
        r"(?:m_data|new\s+JSCallbackDataWeak|new\s+WeakPtr|JSCallbackDataWeak\s*\*\s*m_)",
        combined,
    ), "Weak type not used in member/constructor context"


# [pr_diff] fail_to_pass
def test_gc_visitor_in_abort_algorithm():
    """JSAbortAlgorithm must have a GC visitor method that delegates to m_data's
    visitor (so the weak callback stays alive while reachable)."""
    cpp = read_stripped(ALGO_CPP)
    header = read_stripped(ALGO_H)

    # Header must declare a visitor/tracer method
    assert re.search(
        r"(?:void|template)\s+.*(?:visit|trace|mark)\w*\s*\([^)]*(?:Visitor|Slot)",
        header, re.IGNORECASE,
    ), "No visitor declaration in JSAbortAlgorithm.h"

    # CPP must define a visitor method that delegates to m_data
    body = extract_function_body(
        cpp,
        r"JSAbortAlgorithm::\w*(?:visit|trace|mark)\w*\s*\([^)]*(?:Visitor|Slot)[^)]*\)",
    )
    assert body is not None, "No visitor method implementation in JSAbortAlgorithm.cpp"
    assert re.search(
        r"m_data\s*->\s*\w*(?:visit|trace|mark)", body, re.IGNORECASE
    ), "Visitor method does not delegate to m_data"


# [pr_diff] fail_to_pass
def test_handle_event_null_guard():
    """handleEvent must guard against a GC-collected weak callback (null check)."""
    cpp = read_stripped(ALGO_CPP)
    body = extract_function_body(cpp, r"JSAbortAlgorithm::handleEvent")
    assert body is not None, "handleEvent method not found"

    guards = [
        r"!\s*\w*callback",
        r"callback\w*\s*==\s*nullptr",
        r"nullptr\s*==\s*\w*callback",
        r"!\s*m_data",
        r"callback\w*\.has_value",
        r"if\s*\(\s*!\s*\w*callback",
    ]
    assert any(re.search(g, body, re.IGNORECASE) for g in guards), \
        "No null/validity guard in handleEvent"

    # Anti-stub: body must have real logic (>= 3 non-empty code lines)
    code_lines = [
        l.strip() for l in body.split("\n")
        if l.strip() and l.strip() not in ("{", "}")
    ]
    assert len(code_lines) >= 3, "handleEvent body is trivial (stub)"


# [pr_diff] fail_to_pass
def test_abort_signal_typed_container():
    """AbortSignal must store abort algorithms in a GC-visible typed container
    (separate from type-erased m_algorithms) with a visitor declared and implemented."""
    header = read_stripped(SIGNAL_H)
    cpp = read_stripped(SIGNAL_CPP)

    # Header: typed container holding AbortAlgorithm refs
    container_patterns = [
        r"(?:Vector|HashMap|Deque|std::vector|std::unordered_map|std::map|std::deque|std::list)\s*<[^>]*AbortAlgorithm",
        r"(?:Vector|HashMap|Deque|std::vector)\s*<[^>]*Ref\s*<\s*AbortAlgorithm",
    ]
    assert any(re.search(p, header) for p in container_patterns), \
        "No typed AbortAlgorithm container in AbortSignal.h"

    # Header: visitor declaration
    visitor_decl_patterns = [
        r"(?:visit|trace|mark)\w*(?:Abort|Algorithm|Callback)\w*\s*\(",
        r"template\s*<\s*typename\s+\w+\s*>\s*void\s+\w*(?:visit|trace)\w*",
    ]
    assert any(re.search(p, header, re.IGNORECASE) for p in visitor_decl_patterns), \
        "No visitor declaration in AbortSignal.h"

    # CPP: visitor implementation
    assert re.search(
        r"AbortSignal::\w*(?:visit|trace)\w*(?:Abort|Algorithm|Callback)", cpp, re.IGNORECASE,
    ), "No visitor implementation in AbortSignal.cpp"


# [pr_diff] fail_to_pass
def test_thread_safety():
    """Abort algorithm storage must be synchronized — GC thread visits concurrently
    with main-thread mutations. Lock member + >= 2 lock usages required."""
    header = read_stripped(SIGNAL_H)
    cpp = read_stripped(SIGNAL_CPP)

    lock_member_patterns = [
        r"\b(?:Lock|Mutex|std::mutex|std::shared_mutex|RecursiveLock|SpinLock)\b\s+m_\w*",
        r"m_\w*(?:Lock|Mutex|lock|mutex)\b",
        r"WTF_GUARDED_BY_LOCK",
        r"\bstd::atomic\b.*m_\w*",
    ]
    assert any(re.search(p, header) for p in lock_member_patterns), \
        "No lock/mutex member in AbortSignal.h"

    lock_usage_patterns = [
        r"\bLocker\b", r"\block_guard\b", r"\bunique_lock\b",
        r"\bscoped_lock\b", r"\.lock\(\)", r"\.acquire\(\)",
        r"\bLockHolder\b", r"\bAutoLocker\b",
    ]
    lock_uses = sum(len(re.findall(p, cpp)) for p in lock_usage_patterns)
    assert lock_uses >= 2, f"Only {lock_uses} lock usage(s) in AbortSignal.cpp, need >= 2"


# [pr_diff] fail_to_pass
def test_gc_visitor_walks_algorithms():
    """JSAbortSignal's GC visitor (visitAdditionalChildren or similar) must call
    through to AbortSignal's algorithm visitor to keep weak callbacks alive."""
    custom = read_stripped(CUSTOM_CPP)

    body = extract_function_body(
        custom,
        r"(?:visitAdditionalChildren|visitChildren|visitOutputConstraints|trace)\w*"
        r"\s*\([^)]*(?:Visitor|Slot)[^)]*\)",
    )
    assert body is not None, "No GC visitor method in JSAbortSignalCustom.cpp"

    calls_algo_visitor = re.search(
        r"(?:visit|trace|mark)\w*(?:Abort|Algorithm|Callback)", body, re.IGNORECASE
    )
    direct_iteration = re.search(
        r"for\s*\(.*(?:abort|algorithm)", body, re.IGNORECASE
    )
    assert calls_algo_visitor or direct_iteration, \
        "GC visitor does not walk abort algorithms"


# [pr_diff] fail_to_pass
def test_typed_storage_path():
    """addAbortAlgorithmToSignal must store AbortAlgorithm in the new typed
    container, NOT erase it into a lambda via the old addAlgorithm() path."""
    cpp = read_stripped(SIGNAL_CPP)
    body = extract_function_body(cpp, r"addAbortAlgorithmToSignal")
    assert body is not None, "addAbortAlgorithmToSignal not found"

    # Must NOT call the old addAlgorithm (which type-erases)
    assert not re.search(r"\b(?<!Abort)addAlgorithm\s*\(", body), \
        "Still calls old addAlgorithm (type erasure)"

    # Must store into a container
    assert re.search(
        r"(?:append|push_back|emplace_back|emplace|insert|add)\s*\(", body
    ), "No container insertion found in addAbortAlgorithmToSignal"

    # Anti-stub: body must be non-trivial
    code_lines = [
        l.strip() for l in body.split("\n")
        if l.strip() and l.strip() not in ("{", "}")
    ]
    assert len(code_lines) >= 3, "addAbortAlgorithmToSignal body is trivial"


# [pr_diff] fail_to_pass
def test_remove_uses_new_container():
    """removeAbortAlgorithmFromSignal must operate on the new typed container
    with proper locking, NOT delegate to the old removeAlgorithm() path."""
    cpp = read_stripped(SIGNAL_CPP)
    body = extract_function_body(cpp, r"removeAbortAlgorithmFromSignal")
    assert body is not None, "removeAbortAlgorithmFromSignal not found"

    # Must NOT call the old removeAlgorithm (which operates on type-erased m_algorithms)
    assert not re.search(r"\b(?<!Abort)removeAlgorithm\s*\(", body), \
        "Still calls old removeAlgorithm"

    # Must have locking
    lock_patterns = [r"\bLocker\b", r"\block_guard\b", r"\bunique_lock\b",
                     r"\bscoped_lock\b", r"\.lock\(\)", r"\bLockHolder\b"]
    assert any(re.search(p, body) for p in lock_patterns), \
        "No lock usage in removeAbortAlgorithmFromSignal"

    # Must remove from a container
    assert re.search(
        r"(?:removeFirstMatching|remove_if|erase|removeAll)\s*\(", body
    ), "No container removal in removeAbortAlgorithmFromSignal"


# [pr_diff] fail_to_pass
def test_memory_cost_includes_new_container():
    """memoryCost must account for the new abort algorithms container."""
    cpp = read_stripped(SIGNAL_CPP)
    body = extract_function_body(cpp, r"AbortSignal::memoryCost")
    assert body is not None, "memoryCost not found"

    # Must reference the new container (m_abortAlgorithms or similar)
    assert re.search(
        r"m_abort\w*\s*\.\s*(?:sizeInBytes|size|capacity|byteSize)", body
    ), "memoryCost does not account for new abort algorithms container"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — from .claude/skills and bindings AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — src/bun.js/bindings/v8/AGENTS.md:230 @ fe4a66e
def test_visit_children_for_gc_objects():
    """Custom heap objects holding GC references must implement visitChildren
    or equivalent visitor. Both JSAbortAlgorithm and AbortSignal must have
    visitor methods since they hold GC-managed references.

    Rule: 'Implement visitChildren() for custom heap objects'
    Source: src/bun.js/bindings/v8/AGENTS.md:230
    """
    # JSAbortAlgorithm: must have visitor for its weak callback
    algo_h = read_stripped(ALGO_H)
    assert re.search(
        r"(?:visit|trace)\w*\s*\([^)]*(?:Visitor|Slot)", algo_h
    ), "JSAbortAlgorithm.h missing visitor declaration for GC callback"

    # AbortSignal: must have visitor for its algorithm container
    signal_h = read_stripped(SIGNAL_H)
    assert re.search(
        r"(?:visit|trace)\w*(?:Abort|Algorithm)\w*\s*\(", signal_h
    ), "AbortSignal.h missing visitor for abort algorithm container"

    # JSAbortSignalCustom: visitor must be wired up in GC thread visitor
    custom = read_stripped(CUSTOM_CPP)
    assert re.search(
        r"(?:visit|trace)\w*(?:Abort|Algorithm)", custom, re.IGNORECASE
    ), "JSAbortSignalCustom.cpp GC visitor not wired to algorithm visitor"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — from test/AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — test/AGENTS.md:21 @ fe4a66e
def test_file_no_settimeout():
    """Regression test file must exist and must not use setTimeout.

    Rule: 'Do not write flaky tests. Never wait for time to pass in tests.'
    Source: test/AGENTS.md:21
    """
    p = Path(f"{REPO}/{TEST_FILE}")
    assert p.exists(), f"Regression test file {TEST_FILE} missing"
    content = p.read_text()
    assert not re.search(r"\bsetTimeout\b", content), (
        "Test file uses setTimeout — use Bun.sleep() or await a condition instead"
    )


# [agent_config] fail_to_pass — test/AGENTS.md:218 @ fe4a66e
def test_file_module_scope_imports():
    """Regression test file must use module-scope static imports only,
    not dynamic import() calls inside test function bodies.

    Rule: 'Only use dynamic import or require when the test is specifically
    testing something related to dynamic import or require. Otherwise, always
    use module-scope import statements.'
    Source: test/AGENTS.md:218
    """
    p = Path(f"{REPO}/{TEST_FILE}")
    assert p.exists(), f"Regression test file {TEST_FILE} missing"
    content = p.read_text()
    assert not re.search(r"\bawait\s+import\s*\(", content), (
        "Test file uses dynamic import() — use module-scope import statements instead"
    )
    assert not re.search(r"\brequire\s*\(", content), (
        "Test file uses require() — use module-scope import statements instead"
    )
