"""
Task: bun-pipeTo-signal-leak
Repo: bun @ fe4a66e086bebd2c3c5a238effa801426d736278
PR: 28491

This fixes a memory leak in ReadableStream.pipeTo when called with an AbortSignal.
The leak was caused by a Strong reference cycle: AbortSignal -> JSAbortAlgorithm
-> Strong<callback> -> closure -> pipeState.signal -> JSAbortSignal -> Ref<AbortSignal>.

The fix switches JSAbortAlgorithm from JSCallbackDataStrong to JSCallbackDataWeak
and visits the weak callback from JSAbortSignal::visitAdditionalChildrenInGCThread.
"""

import subprocess
from pathlib import Path
import re

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cpp_syntax_valid():
    """Modified C++ files must have valid syntax (no unmatched braces)."""
    files = [
        f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp",
        f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.h",
        f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp",
        f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.h",
        f"{REPO}/src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp",
    ]
    for f in files:
        src = Path(f).read_text()
        # Basic brace balance check
        open_count = src.count("{")
        close_count = src.count("}")
        assert open_count == close_count, f"{f}: Unbalanced braces ({open_count} vs {close_count})"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsabortalgorithm_uses_weak_ref():
    """JSAbortAlgorithm must use JSCallbackDataWeak instead of JSCallbackDataStrong.

    This is the core fix: switching from Strong (creates GC root) to Weak
    (allows collection when signal wrapper is unreachable) breaks the cycle.
    """
    src = Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.h").read_text()
    # Check that m_data is declared as JSCallbackDataWeak*
    assert "JSCallbackDataWeak* m_data" in src, "JSAbortAlgorithm must use JSCallbackDataWeak* m_data"
    # Check that JSCallbackDataStrong is NOT used
    assert "JSCallbackDataStrong" not in src, "JSAbortAlgorithm must NOT use JSCallbackDataStrong"


# [pr_diff] fail_to_pass
def test_jsabortalgorithm_has_visit_js_function():
    """JSAbortAlgorithm must implement visitJSFunction for GC marking.

    The weak callback needs to be visited during GC so it's kept alive
    while the signal wrapper is reachable.
    """
    h_src = Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.h").read_text()
    cpp_src = Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp").read_text()

    # Header must declare visitJSFunction overrides
    assert "void visitJSFunction(JSC::AbstractSlotVisitor&) override" in h_src, \
        "Header must declare visitJSFunction(AbstractSlotVisitor)"
    assert "void visitJSFunction(JSC::SlotVisitor&) override" in h_src, \
        "Header must declare visitJSFunction(SlotVisitor)"

    # Implementation must exist in cpp
    assert "void JSAbortAlgorithm::visitJSFunction(JSC::AbstractSlotVisitor& visitor)" in cpp_src, \
        "Implementation must define visitJSFunction(AbstractSlotVisitor)"
    assert "void JSAbortAlgorithm::visitJSFunction(JSC::SlotVisitor& visitor)" in cpp_src, \
        "Implementation must define visitJSFunction(SlotVisitor)"


# [pr_diff] fail_to_pass
def test_abort_signal_has_abort_algorithms_vector():
    """AbortSignal must have m_abortAlgorithms vector and lock for GC visibility.

    The abort algorithms are stored separately from m_algorithms so the GC
    thread can visit the weak callbacks without holding complex lambdas.
    """
    h_src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.h").read_text()

    # Check for m_abortAlgorithms vector
    assert "m_abortAlgorithms" in h_src, "AbortSignal must have m_abortAlgorithms member"
    # Check for the lock
    assert "m_abortAlgorithmsLock" in h_src, "AbortSignal must have m_abortAlgorithmsLock"
    assert "wtf/Lock.h" in h_src, "Must include wtf/Lock.h"


# [pr_diff] fail_to_pass
def test_abort_signal_has_visit_abort_algorithms():
    """AbortSignal must implement visitAbortAlgorithms for GC thread visitation."""
    h_src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.h").read_text()
    cpp_src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp").read_text()

    # Header declaration
    assert "template<typename Visitor> void visitAbortAlgorithms(Visitor&)" in h_src, \
        "Header must declare visitAbortAlgorithms template method"

    # Implementation in cpp
    assert "void AbortSignal::visitAbortAlgorithms(Visitor& visitor)" in cpp_src, \
        "Implementation must define visitAbortAlgorithms"
    assert "pair.second->visitJSFunction(visitor)" in cpp_src, \
        "visitAbortAlgorithms must call visitJSFunction on each algorithm"


# [pr_diff] fail_to_pass
def test_js_abort_signal_visits_abort_algorithms():
    """JSAbortSignal::visitAdditionalChildrenInGCThread must call visitAbortAlgorithms.

    This connects the GC visitation chain: when the JS wrapper is visited,
    it visits the underlying AbortSignal's abort algorithms.
    """
    src = Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp").read_text()
    assert "visitAbortAlgorithms(visitor)" in src, \
        "JSAbortSignal::visitAdditionalChildrenInGCThread must call visitAbortAlgorithms"


# [pr_diff] fail_to_pass
def test_add_abort_algorithm_uses_new_vector():
    """addAbortAlgorithmToSignal must use m_abortAlgorithms instead of addAlgorithm.

    The fix changes from storing in the type-erased m_algorithms vector
    (which hides Ref<AbortAlgorithm> from GC) to the new m_abortAlgorithms.
    """
    src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp").read_text()

    # Check that addAbortAlgorithmToSignal uses m_abortAlgorithms
    assert "signal.m_abortAlgorithms.append" in src, \
        "addAbortAlgorithmToSignal must append to m_abortAlgorithms"
    # Check that it uses the lock
    assert "Locker locker { signal.m_abortAlgorithmsLock }" in src, \
        "addAbortAlgorithmToSignal must lock m_abortAlgorithmsLock"


# [pr_diff] fail_to_pass
def test_remove_abort_algorithm_uses_new_vector():
    """removeAbortAlgorithmFromSignal must remove from m_abortAlgorithms."""
    src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp").read_text()

    assert "signal.m_abortAlgorithms.removeFirstMatching" in src, \
        "removeAbortAlgorithmFromSignal must remove from m_abortAlgorithms"


# [pr_diff] fail_to_pass
def test_run_abort_steps_handles_new_vector():
    """runAbortSteps must process m_abortAlgorithms under lock."""
    src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp").read_text()

    assert "Locker locker { m_abortAlgorithmsLock }" in src, \
        "runAbortSteps must lock m_abortAlgorithmsLock"
    assert "abortAlgorithms = std::exchange(m_abortAlgorithms, {})" in src, \
        "runAbortSteps must extract m_abortAlgorithms under lock"


# [pr_diff] fail_to_pass
def test_handle_event_checks_callback_validity():
    """JSAbortAlgorithm::handleEvent must check callback validity before use.

    Since the callback is now Weak, it can be null if GC collected it.
    The fix adds a null check before dereferencing.
    """
    src = Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp").read_text()

    # Check for null callback check
    assert "if (!callback)" in src or "auto* callback = m_data->callback()" in src, \
        "handleEvent must check if callback is null (Weak ref may be collected)"
    assert "return CallbackResultType::UnableToExecute" in src, \
        "handleEvent must return UnableToExecute when callback is null"


# [pr_diff] fail_to_pass
def test_memory_cost_includes_abort_algorithms():
    """memoryCost must include m_abortAlgorithms size for accurate reporting."""
    src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp").read_text()

    assert "m_abortAlgorithms.sizeInBytes()" in src, \
        "memoryCost must include m_abortAlgorithms.sizeInBytes()"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_fix_not_stub():
    """The fix must not be a stub - verify substantial implementation exists."""
    cpp_src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp").read_text()

    # Check that visitAbortAlgorithms has the full implementation (not just empty braces)
    # The implementation should lock, iterate m_abortAlgorithms, and call visitJSFunction
    assert "void AbortSignal::visitAbortAlgorithms" in cpp_src, \
        "visitAbortAlgorithms must be implemented"
    impl_section = cpp_src.split("void AbortSignal::visitAbortAlgorithms")[1].split("template void AbortSignal::visitAbortAlgorithms")[0]
    assert "Locker locker" in impl_section and "m_abortAlgorithms" in impl_section, \
        "visitAbortAlgorithms must have substantial implementation with lock and vector access"

    # Check runAbortSteps has the new code
    run_steps = cpp_src.split("void AbortSignal::runAbortSteps()")[1].split("// 3. Fire an event")[0] if "void AbortSignal::runAbortSteps()" in cpp_src else ""
    assert "m_abortAlgorithms" in run_steps, "runAbortSteps must process m_abortAlgorithms"


# [static] pass_to_pass
def test_includes_proper_headers():
    """All necessary headers must be included."""
    h_src = Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.h").read_text()
    assert "wtf/Lock.h" in h_src, "Must include wtf/Lock.h for Lock class"
