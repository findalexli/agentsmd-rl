"""
Tests for the kotlin-tooling-core deprecated API removal task.

PR: JetBrains/kotlin#5809 — KT-80448: Remove deprecated extras APIs and associated tests.

F2P tests verify that deprecated code has been removed.
P2P tests verify the module still compiles and its tests pass.
"""

import os
import subprocess
import glob
import pytest

REPO = os.environ.get("REPO", "/workspace/kotlin")
MAIN_SRC = f"{REPO}/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core"
TEST_SRC = f"{REPO}/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core"
LIB_DIR = os.environ.get("LIB_DIR", "/workspace/lib")
BUILD_DIR = f"{REPO}/build"

EXTRAS_PROPERTY_KT = f"{MAIN_SRC}/ExtrasProperty.kt"
EXTRAS_PROPERTY_TEST_KT = f"{TEST_SRC}/ExtrasPropertyTest.kt"


def _lib_cp():
    """Build explicit classpath from lib jars (avoid glob issues)."""
    jars = sorted(glob.glob(f"{LIB_DIR}/*.jar"))
    return ":".join(jars)


def read_file(path):
    with open(path, "r") as f:
        return f.read()


# ──────────────────────────────────────────────
# Fail-to-pass tests
# ──────────────────────────────────────────────

def test_deprecated_apis_section_removed():
    """The 'DEPRECATED APIs' comment section must be removed from ExtrasProperty.kt (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_KT)
    assert "DEPRECATED APIs" not in source, (
        "ExtrasProperty.kt still contains the 'DEPRECATED APIs' section. "
        "All deprecated functions and interfaces should be removed."
    )


def test_deprecated_functions_removed():
    """Deprecated functions (extrasReadProperty, extrasFactoryProperty, extrasNullableLazyProperty) must be removed (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_KT)
    deprecated_patterns = [
        "fun extrasReadProperty(",
        "fun extrasFactoryProperty(",
        "fun extrasNullableLazyProperty(",
    ]
    found = [p for p in deprecated_patterns if p in source]
    assert not found, f"ExtrasProperty.kt still contains deprecated functions: {found}"


def test_deprecated_interfaces_removed():
    """Deprecated interfaces (ExtrasReadOnlyProperty, ExtrasFactoryProperty, NullableExtrasLazyProperty) must be removed (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_KT)
    deprecated_interfaces = [
        "interface ExtrasReadOnlyProperty",
        "interface ExtrasFactoryProperty",
        "interface NullableExtrasLazyProperty",
    ]
    found = [p for p in deprecated_interfaces if p in source]
    assert not found, f"ExtrasProperty.kt still contains deprecated interfaces: {found}"


def test_deprecated_extensions_removed():
    """Deprecated extension properties (readProperty, factoryProperty, nullableLazyProperty on Extras.Key) must be removed (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_KT)
    deprecated_extensions = [
        "Extras.Key<T>.readProperty get()",
        "Extras.Key<T>.factoryProperty(",
        "Extras.Key<Optional<T>>.nullableLazyProperty(",
    ]
    found = [p for p in deprecated_extensions if p in source]
    assert not found, f"ExtrasProperty.kt still contains deprecated extension properties: {found}"


def test_java_util_import_removed():
    """The 'import java.util.*' line must be removed from ExtrasProperty.kt since Optional is no longer needed (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_KT)
    assert "import java.util.*" not in source, (
        "ExtrasProperty.kt still imports java.util.*, which was only needed by the deprecated APIs."
    )


def test_test_file_uses_readwrite_property():
    """ExtrasPropertyTest.kt should use readWriteProperty instead of deprecated readProperty (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_TEST_KT)
    assert "keyA.readProperty" not in source, (
        "ExtrasPropertyTest.kt still uses deprecated 'readProperty'. "
        "Should be migrated to 'readWriteProperty'."
    )
    assert "keyB.readProperty" not in source, (
        "ExtrasPropertyTest.kt still uses deprecated 'readProperty'. "
        "Should be migrated to 'readWriteProperty'."
    )


def test_test_file_uses_lazy_property():
    """ExtrasPropertyTest.kt should use lazyProperty instead of deprecated factoryProperty (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_TEST_KT)
    # Check for actual usage of the deprecated factoryProperty extension, not the test method name
    assert "keyList.factoryProperty" not in source, (
        "ExtrasPropertyTest.kt still uses deprecated 'factoryProperty' extension. "
        "Should be migrated to 'lazyProperty'."
    )


def test_no_deprecation_suppress_in_test():
    """The @Suppress('DEPRECATION_ERROR') annotation should be removed from ExtrasPropertyTest (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_TEST_KT)
    assert '@Suppress("DEPRECATION_ERROR")' not in source, (
        "ExtrasPropertyTest.kt still has @Suppress('DEPRECATION_ERROR'). "
        "This annotation should be removed since deprecated APIs are gone."
    )


def test_nullable_lazy_property_test_removed():
    """The test for lazyNullableProperty should be removed since the API is gone (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_TEST_KT)
    assert "lazyNullableProperty" not in source, (
        "ExtrasPropertyTest.kt still references 'lazyNullableProperty'. "
        "The deprecated nullable lazy property test and its helpers should be removed."
    )


def test_scheduled_for_removal_removed():
    """All 'Scheduled for removal in Kotlin 2.3' deprecation annotations must be removed (fail_to_pass)."""
    source = read_file(EXTRAS_PROPERTY_KT)
    assert "Scheduled for removal in Kotlin 2.3" not in source, (
        "ExtrasProperty.kt still contains deprecation annotations targeting Kotlin 2.3 removal."
    )


# ──────────────────────────────────────────────
# Pass-to-pass tests
# ──────────────────────────────────────────────

def _compile_main():
    """Compile main Kotlin sources and return the subprocess result."""
    os.makedirs(BUILD_DIR, exist_ok=True)
    sources = sorted(glob.glob(f"{MAIN_SRC}/*.kt"))
    return subprocess.run(
        ["kotlinc", "-jvm-target", "17", "-no-reflect",
         "-d", f"{BUILD_DIR}/main.jar"] + sources,
        capture_output=True, text=True, timeout=120,
    )


def _compile_all():
    """Compile main sources and ExtrasPropertyTest.kt together (needed for internal access)."""
    os.makedirs(BUILD_DIR, exist_ok=True)
    main_sources = sorted(glob.glob(f"{MAIN_SRC}/*.kt"))
    test_source = f"{TEST_SRC}/ExtrasPropertyTest.kt"
    cp = _lib_cp()
    return subprocess.run(
        ["kotlinc", "-jvm-target", "17", "-no-reflect",
         "-cp", cp,
         "-d", f"{BUILD_DIR}/all.jar"]
        + main_sources + [test_source],
        capture_output=True, text=True, timeout=120,
    )


def _run_junit(test_class):
    """Run a JUnit test class and return the subprocess result."""
    cp = f"{BUILD_DIR}/all.jar:{_lib_cp()}"
    return subprocess.run(
        ["java", "-cp", cp, "org.junit.runner.JUnitCore", test_class],
        capture_output=True, text=True, timeout=120,
    )


def _ensure_compiled():
    """Compile main sources and ExtrasPropertyTest, raising on failure."""
    r = _compile_all()
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-2000:]}"


def test_main_sources_compile():
    """Main Kotlin sources compile successfully (pass_to_pass)."""
    r = _compile_main()
    assert r.returncode == 0, f"Main compilation failed:\n{r.stderr[-2000:]}"


def test_extras_property_test_compiles():
    """ExtrasPropertyTest.kt compiles successfully with main sources (pass_to_pass)."""
    r = _compile_all()
    assert r.returncode == 0, f"Combined compilation failed:\n{r.stderr[-2000:]}"


def test_extras_property_tests_pass():
    """ExtrasPropertyTest passes (pass_to_pass)."""
    _ensure_compiled()
    r = _run_junit("org.jetbrains.kotlin.tooling.core.ExtrasPropertyTest")
    assert r.returncode == 0, (
        f"ExtrasPropertyTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def _compile_all_sources():
    """Compile all main and test source files together."""
    os.makedirs(BUILD_DIR, exist_ok=True)
    main_sources = sorted(glob.glob(f"{MAIN_SRC}/*.kt"))
    test_sources = sorted(glob.glob(f"{TEST_SRC}/*.kt"))
    cp = _lib_cp()
    return subprocess.run(
        ["kotlinc", "-jvm-target", "17", "-no-reflect",
         "-cp", cp,
         "-d", f"{BUILD_DIR}/full.jar"]
        + main_sources + test_sources,
        capture_output=True, text=True, timeout=180,
    )


def _ensure_full_compiled():
    """Compile all main + test sources, raising on failure."""
    r = _compile_all_sources()
    assert r.returncode == 0, f"Full compilation failed:\n{r.stderr[-2000:]}"


def _run_junit_class(test_class):
    """Run a JUnit test class from full.jar."""
    cp = f"{BUILD_DIR}/full.jar:{_lib_cp()}"
    return subprocess.run(
        ["java", "-cp", cp, "org.junit.runner.JUnitCore", test_class],
        capture_output=True, text=True, timeout=120,
    )


def test_all_sources_compile():
    """All main and test sources compile together (pass_to_pass)."""
    r = _compile_all_sources()
    assert r.returncode == 0, f"Full compilation failed:\n{r.stderr[-2000:]}"


def test_extras_tests_pass():
    """ExtrasTest passes (pass_to_pass)."""
    _ensure_full_compiled()
    r = _run_junit_class("org.jetbrains.kotlin.tooling.core.ExtrasTest")
    assert r.returncode == 0, (
        f"ExtrasTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_extras_serializable_tests_pass():
    """ExtrasSerializableTest passes (pass_to_pass)."""
    _ensure_full_compiled()
    r = _run_junit_class("org.jetbrains.kotlin.tooling.core.ExtrasSerializableTest")
    assert r.returncode == 0, (
        f"ExtrasSerializableTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_extras_key_stable_string_tests_pass():
    """ExtrasKeyStableStringTest passes (pass_to_pass)."""
    _ensure_full_compiled()
    r = _run_junit_class("org.jetbrains.kotlin.tooling.core.ExtrasKeyStableStringTest")
    assert r.returncode == 0, (
        f"ExtrasKeyStableStringTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_closure_tests_pass():
    """ClosureTest passes (pass_to_pass)."""
    _ensure_full_compiled()
    r = _run_junit_class("org.jetbrains.kotlin.tooling.core.ClosureTest")
    assert r.returncode == 0, (
        f"ClosureTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_type_tests_pass():
    """TypeTest passes (pass_to_pass)."""
    _ensure_full_compiled()
    r = _run_junit_class("org.jetbrains.kotlin.tooling.core.TypeTest")
    assert r.returncode == 0, (
        f"TypeTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_interner_tests_pass():
    """InternerTest passes (pass_to_pass)."""
    _ensure_full_compiled()
    r = _run_junit_class("org.jetbrains.kotlin.tooling.core.InternerTest")
    assert r.returncode == 0, (
        f"InternerTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_kotlin_tooling_version_tests_pass():
    """KotlinToolingVersionTest passes (pass_to_pass)."""
    _ensure_full_compiled()
    r = _run_junit_class("org.jetbrains.kotlin.tooling.core.KotlinToolingVersionTest")
    assert r.returncode == 0, (
        f"KotlinToolingVersionTest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )
