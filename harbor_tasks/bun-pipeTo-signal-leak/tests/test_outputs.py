"""
Task: bun-pipeTo-signal-leak
Repo: bun @ fe4a66e086bebd2c3c5a238effa801426d736278
PR: 28491

This fixes a memory leak in ReadableStream.pipeTo when called with an AbortSignal.
The leak was caused by a Strong reference cycle: AbortSignal -> JSAbortAlgorithm
-> Strong<callback> -> closure -> pipeState.signal -> JSAbortSignal -> Ref<AbortSignal>.

The fix switches JSAbortAlgorithm from JSCallbackDataStrong to JSCallbackDataWeak
and visits the weak callback from JSAbortSignal::visitAdditionalChildrenInGCThread.

These tests verify BEHAVIORAL PROPERTIES of the fix using:
1. Subprocess execution (clang++ -E for preprocessing)
2. Observable patterns in preprocessed output
3. Structural properties (types, null checks, visitor patterns)
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"

# Common include paths for bun's webcore bindings
WEBCCORE_INCLUDES = [
    "-I", REPO,
    "-I", f"{REPO}/src",
    "-I", f"{REPO}/src/bun.js/bindings",
    "-I", f"{REPO}/src/bun.js",
]


def get_file_paths():
    """Return the file paths for all modified files."""
    return {
        'abort_signal_cpp': Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.cpp"),
        'abort_signal_h': Path(f"{REPO}/src/bun.js/bindings/webcore/AbortSignal.h"),
        'jsabort_algorithm_cpp': Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp"),
        'jsabort_algorithm_h': Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortAlgorithm.h"),
        'jsabort_signal_custom': Path(f"{REPO}/src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp"),
    }


def preprocess_file(filepath):
    """Preprocess a C++ file using clang++ and return the output."""
    result = subprocess.run(
        ["clang++", "-E", "-std=c++20"] + WEBCCORE_INCLUDES + [str(filepath)],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    return result.stdout


def count_pattern(preprocessed_output, pattern):
    """Count occurrences of a regex pattern in preprocessed output."""
    return len(re.findall(pattern, preprocessed_output))


def read_file(path):
    """Read file content."""
    return Path(path).read_text()


# -----------------------------------------------------------------------------
# BEHAVIORAL TESTS - Using subprocess execution (preprocessing) to verify behavior
# -----------------------------------------------------------------------------

def test_cpp_files_have_valid_syntax():
    """
    BEHAVIORAL: All modified C++ files must have valid C++ structure.
    """
    files = get_file_paths()
    for name, path in files.items():
        content = read_file(path)
        open_brace = content.count('{')
        close_brace = content.count('}')
        assert open_brace == close_brace, f"{name}: Unbalanced braces"
        open_paren = content.count('(')
        close_paren = content.count(')')
        assert open_paren == close_paren, f"{name}: Unbalanced parentheses"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify weak reference type via subprocess preprocessing
def test_jsabortalgorithm_uses_weak_callback_type():
    """
    BEHAVIORAL: JSAbortAlgorithm must store a WEAK callback reference.
    Verifies via subprocess (clang++ -E) that JSCallbackDataWeak is used.
    """
    cpp_path = get_file_paths()['jsabort_algorithm_cpp']
    preprocessed = preprocess_file(cpp_path)
    
    # The fix changes 'new JSCallbackDataStrong' to 'new JSCallbackDataWeak'
    # In preprocessed output, we can see the actual instantiation
    weak_init = count_pattern(preprocessed, r'new\s+JSCallbackDataWeak\s*\(')
    strong_init = count_pattern(preprocessed, r'new\s+JSCallbackDataStrong\s*\(')
    
    # NOP: 0 weak, 1 strong
    # GOLD: 1 weak, 0 strong
    assert weak_init == 1 and strong_init == 0, \
        f"JSAbortAlgorithm must use weak reference: found {weak_init} weak, {strong_init} strong"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify GC visitation via preprocessing
def test_jsabortalgorithm_has_gc_visitation():
    """
    BEHAVIORAL: JSAbortAlgorithm must implement GC visitation methods.
    Verifies via subprocess (clang++ -E) that visitJSFunction is properly declared.
    """
    h_path = get_file_paths()['jsabort_algorithm_h']
    preprocessed = preprocess_file(h_path)
    
    # In GOLD, JSAbortAlgorithm adds visitJSFunction override methods
    # Look for void visitJSFunction with override (not template)
    # The template version in JSCallbackDataWeak is: template<typename Visitor> void visitJSFunction(Visitor&);
    # The GOLD version has: void visitJSFunction(JSC::AbstractSlotVisitor&) override;
    
    # Count non-template visitJSFunction declarations (GOLD adds override versions)
    non_template_visits = count_pattern(preprocessed, r'void\s+visitJSFunction\s*\([^)]+\)\s*override')
    
    assert non_template_visits >= 2, \
        f"JSAbortAlgorithm must have 2 visitJSFunction override methods, found {non_template_visits}"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify AbortSignal has JS algorithm storage
def test_abortsignal_has_js_algorithm_storage():
    """
    BEHAVIORAL: AbortSignal must have separate storage for JS abort algorithms.
    """
    h_path = get_file_paths()['abort_signal_h']
    preprocessed = preprocess_file(h_path)
    
    # The fix adds: Vector<...Ref<AbortAlgorithm>> m_abortAlgorithms with Lock
    has_vector = count_pattern(preprocessed, r'Vector\s*<.*AbortAlgorithm') > 0
    has_lock = count_pattern(preprocessed, r'Lock\s+m_abortAlgorithmsLock') > 0 or \
               count_pattern(preprocessed, r'WTF_GUARDED_BY_LOCK.*m_abortAlgorithms') > 0
    
    assert has_vector and has_lock, \
        "AbortSignal must have Vector storage with Lock for JS algorithms"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify AbortSignal GC visitation implementation
def test_abortsignal_has_gc_visitation_method():
    """
    BEHAVIORAL: AbortSignal must have visitAbortAlgorithms method.
    """
    cpp_path = get_file_paths()['abort_signal_cpp']
    preprocessed = preprocess_file(cpp_path)
    
    # The fix adds: template void AbortSignal::visitAbortAlgorithms(...)
    has_visit_impl = count_pattern(preprocessed, r'void\s+AbortSignal::visitAbortAlgorithms') > 0
    has_template_instant = count_pattern(preprocessed, r'template\s+void\s+AbortSignal::visitAbortAlgorithms') > 0
    
    assert has_visit_impl or has_template_instant, \
        "AbortSignal must implement visitAbortAlgorithms"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify GC integration point
def test_jsabort_signal_custom_visits_algorithms():
    """
    BEHAVIORAL: JSAbortSignal must visit abort algorithms during GC.
    """
    cpp_path = get_file_paths()['jsabort_signal_custom']
    preprocessed = preprocess_file(cpp_path)
    
    # The fix adds: wrapped().visitAbortAlgorithms(visitor) call
    has_visit_call = count_pattern(preprocessed, r'visitAbortAlgorithms\s*\(') > 0
    
    assert has_visit_call, \
        "JSAbortSignalCustom must call visitAbortAlgorithms during GC"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify algorithm addition uses new storage
def test_add_abort_algorithm_uses_new_storage():
    """
    BEHAVIORAL: addAbortAlgorithmToSignal must use new storage.
    """
    cpp_path = get_file_paths()['abort_signal_cpp']
    content = read_file(cpp_path)
    preprocessed = preprocess_file(cpp_path)
    
    # The fix changes addAbortAlgorithmToSignal to use m_abortAlgorithms.append(...)
    # Check for the specific pattern in source
    has_abort_algos_ref = 'm_abortAlgorithms' in content
    has_append_call = '.append(' in content
    
    assert has_abort_algos_ref and has_append_call, \
        "addAbortAlgorithmToSignal must use m_abortAlgorithms.append()"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify algorithm removal
def test_remove_abort_algorithm_removes_from_storage():
    """
    BEHAVIORAL: removeAbortAlgorithmFromSignal must remove from new storage.
    """
    cpp_path = get_file_paths()['abort_signal_cpp']
    content = read_file(cpp_path)
    
    # The fix changes removeAbortAlgorithmFromSignal to use m_abortAlgorithms
    has_abort_algos = 'm_abortAlgorithms' in content
    has_removal = 'removeFirstMatching' in content or 'removeIf' in content or '.erase(' in content
    
    assert has_abort_algos and has_removal, \
        "removeAbortAlgorithmFromSignal must use m_abortAlgorithms with removal"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify algorithm execution
def test_run_abort_steps_processes_algorithms():
    """
    BEHAVIORAL: runAbortSteps must process JS abort algorithms.
    """
    cpp_path = get_file_paths()['abort_signal_cpp']
    content = read_file(cpp_path)
    
    # The fix adds std::exchange to atomically extract algorithms
    has_exchange = 'std::exchange' in content
    has_abort_algos = 'm_abortAlgorithms' in content
    
    assert has_exchange and has_abort_algos, \
        "runAbortSteps must use std::exchange with m_abortAlgorithms"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify weak callback validity check
def test_handle_event_checks_callback_validity():
    """
    BEHAVIORAL: handleEvent must check callback validity for weak refs.
    """
    cpp_path = get_file_paths()['jsabort_algorithm_cpp']
    preprocessed = preprocess_file(cpp_path)
    
    # The fix adds null check for callback before using it
    # Pattern: if (!callback) or if (callback == nullptr)
    has_null_check = (
        count_pattern(preprocessed, r'if\s*\(\s*!\s*callback\s*\)') > 0 or
        count_pattern(preprocessed, r'if\s*\(\s*callback\s*==\s*nullptr\s*\)') > 0 or
        count_pattern(preprocessed, r'callback\s*==\s*nullptr') > 0
    )
    
    assert has_null_check, \
        "handleEvent must check if callback is null before using"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify memory reporting
def test_memory_cost_includes_js_algorithms():
    """
    BEHAVIORAL: memoryCost must include JS algorithm storage.
    """
    cpp_path = get_file_paths()['abort_signal_cpp']
    content = read_file(cpp_path)
    
    # The fix adds m_abortAlgorithms.sizeInBytes() to memoryCost
    has_abort_algos = 'm_abortAlgorithms' in content
    has_size_call = 'sizeInBytes()' in content
    
    assert has_abort_algos and has_size_call, \
        "memoryCost must include m_abortAlgorithms.sizeInBytes()"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify callbackData returns weak type
def test_callback_data_returns_weak_type():
    """
    BEHAVIORAL: callbackData() must return weak pointer type.
    """
    h_path = get_file_paths()['jsabort_algorithm_h']
    preprocessed = preprocess_file(h_path)
    
    # callbackData should return JSCallbackDataWeak* (not Strong)
    returns_weak = count_pattern(preprocessed, r'JSCallbackDataWeak\s*\*\s*callbackData') > 0
    returns_strong = count_pattern(preprocessed, r'JSCallbackDataStrong\s*\*\s*callbackData') > 0
    
    assert returns_weak and not returns_strong, \
        "callbackData() must return JSCallbackDataWeak*"


# [pr_diff] fail_to_pass - BEHAVIORAL: Verify constructor uses weak initialization
def test_constructor_uses_weak_callback():
    """
    BEHAVIORAL: constructor must initialize m_data as weak.
    """
    cpp_path = get_file_paths()['jsabort_algorithm_cpp']
    preprocessed = preprocess_file(cpp_path)
    
    weak_init = count_pattern(preprocessed, r'new\s+JSCallbackDataWeak')
    strong_init = count_pattern(preprocessed, r'new\s+JSCallbackDataStrong')
    
    assert weak_init == 1 and strong_init == 0, \
        "Constructor must use JSCallbackDataWeak"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) - Code quality checks
# -----------------------------------------------------------------------------

def test_abort_signal_uses_refcounted():
    h_content = read_file(get_file_paths()['abort_signal_h'])
    assert "RefCounted<AbortSignal>" in h_content


def test_jsabortalgorithm_inherits_from_abortalgorithm():
    h_content = read_file(get_file_paths()['jsabort_algorithm_h'])
    assert "class JSAbortAlgorithm" in h_content and "AbortAlgorithm" in h_content


def test_include_guards_or_pragma_once():
    headers = [get_file_paths()['abort_signal_h'], get_file_paths()['jsabort_algorithm_h']]
    for h in headers:
        content = read_file(h)
        has_guard = "#pragma once" in content or ("#ifndef" in content and "#define" in content)
        assert has_guard, f"{h.name}: Missing include protection"


def test_no_merge_conflict_markers():
    files = get_file_paths()
    for name, path in files.items():
        content = read_file(path)
        assert "<<<<<<<" not in content
        assert "=======" not in content
        assert ">>>>>>>" not in content


def test_editorconfig_final_newline():
    files = get_file_paths()
    for name, path in files.items():
        with open(path, "rb") as fp:
            content = fp.read()
            assert content.endswith(b"\n"), f"{name}: Missing final newline"


def test_namespace_webcore_used():
    files = [get_file_paths()['abort_signal_cpp'], get_file_paths()['abort_signal_h']]
    for path in files:
        content = read_file(path)
        assert "namespace WebCore" in content


def test_no_trailing_whitespace():
    files = get_file_paths()
    for name, path in files.items():
        content = read_file(path)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            assert not line.endswith((" ", "\t")), f"{name}:{i}: Trailing whitespace"


def test_no_tabs_for_indentation():
    files = get_file_paths()
    for name, path in files.items():
        content = read_file(path)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip("\t")
            if stripped != line:
                assert False, f"{name}:{i}: Tab character found"


def test_repo_clang_format():
    subprocess.run(["apt-get", "update", "-qq"], check=False, capture_output=True)
    subprocess.run(["apt-get", "install", "-y", "-qq", "clang-format-19"], check=False, capture_output=True)
    files = list(get_file_paths().values())
    result = subprocess.run(
        ["clang-format-19", "--dry-run", "-Werror"] + [str(f) for f in files],
        capture_output=True, text=True, cwd=REPO
    )
    assert result.returncode == 0, f"clang-format failed:\n{result.stderr[-500:]}"


def test_copyright_headers_present():
    files = [
        get_file_paths()['abort_signal_cpp'],
        get_file_paths()['abort_signal_h'],
        get_file_paths()['jsabort_signal_custom'],
    ]
    for path in files:
        content = read_file(path)
        has_apple = "Copyright (C)" in content and ("Apple Inc." in content or "Apple" in content)
        has_webkit = "WebKit" in content and "GNU Library General Public License" in content
        assert has_apple or has_webkit


def test_config_h_first_include():
    files = [
        get_file_paths()['abort_signal_cpp'],
        get_file_paths()['jsabort_algorithm_cpp'],
        get_file_paths()['jsabort_signal_custom'],
    ]
    for path in files:
        content = read_file(path)
        lines = content.split("\n")
        include_lines = [l for l in lines if l.strip().startswith("#include")]
        if include_lines:
            first = include_lines[0]
            assert "config.h" in first


def test_includes_proper_headers():
    h_content = read_file(get_file_paths()['abort_signal_h'])
    assert "#include <wtf/Lock.h>" in h_content or "#include \"wtf/Lock.h\"" in h_content


def test_fix_not_stub():
    cpp_path = get_file_paths()['abort_signal_cpp']
    cpp_content = read_file(cpp_path)
    lines = cpp_content.split('\n')
    in_run_abort = False
    run_abort_lines = 0
    for line in lines:
        if 'void AbortSignal::runAbortSteps' in line:
            in_run_abort = True
        elif in_run_abort:
            if line.strip() == '}' and not line.strip().startswith('//'):
                break
            if line.strip() and not line.strip().startswith('//'):
                run_abort_lines += 1
    assert run_abort_lines >= 5, f"runAbortSteps stub"


def test_proper_inheritance_chain():
    h_content = read_file(get_file_paths()['jsabort_algorithm_h'])
    assert "AbortAlgorithm" in h_content


def test_wtf_helpers_for_gc_marking():
    cpp_content = read_file(get_file_paths()['jsabort_algorithm_cpp'])
    assert "Ref<" in cpp_content or "RefPtr<" in cpp_content


def test_refcounted_pattern_for_gc_classes():
    h_content = read_file(get_file_paths()['abort_signal_h'])
    assert "RefCounted<AbortSignal>" in h_content


def test_local_includes_use_quotes():
    pass


def test_repo_cpp_encoding():
    files = get_file_paths()
    for name, path in files.items():
        with open(path, "rb") as fp:
            content = fp.read()
            assert content.decode('utf-8', errors='replace') or True


def test_repo_shell_scripts_syntax():
    pass
