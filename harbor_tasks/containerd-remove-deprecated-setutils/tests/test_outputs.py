"""
Test outputs for containerd#13031 - Remove deprecated setutils types.

This task verifies that:
1. The deprecated Int and String types are removed from setutils
2. The internal cast function is removed
3. The generic Set type continues to work correctly
4. The MergeStringSlices function in util/strings.go is updated to use the generic Set
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/containerd")
SETUTILS_DIR = REPO / "internal" / "cri" / "setutils"
UTIL_DIR = REPO / "internal" / "cri" / "util"

GO_ENV = {**subprocess.os.environ, "GOTOOLCHAIN": "auto"}


def test_int_type_removed():
    """Fail-to-pass: Int type should be removed from setutils package."""
    int_file = SETUTILS_DIR / "int.go"
    assert not int_file.exists(), f"int.go should be removed but still exists at {int_file}"


def test_string_type_removed():
    """Fail-to-pass: String type should be removed from setutils package."""
    string_file = SETUTILS_DIR / "string.go"
    assert not string_file.exists(), f"string.go should be removed but still exists at {string_file}"


def test_cast_function_removed():
    """Fail-to-pass: The cast helper function should be removed from set.go."""
    set_file = SETUTILS_DIR / "set.go"
    content = set_file.read_text()
    assert "func cast[T comparable]" not in content, "cast function should be removed from set.go"


def test_generic_set_still_compiles():
    """Pass-to-pass: Generic Set type should continue to work."""
    result = subprocess.run(
        ["go", "build", "./internal/cri/setutils"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=GO_ENV
    )
    assert result.returncode == 0, f"setutils package failed to build: {result.stderr}"


def test_merge_string_slices_behavior():
    """Fail-to-pass: MergeStringSlices should work correctly with generic Set."""
    # Create a Go test file inside the util package
    test_code = '''package util

import (
	"sort"
	"testing"
)

func TestMergeStringSlicesGold(t *testing.T) {
	// Test case 1: Basic merge with duplicates
	a := []string{"foo", "bar"}
	b := []string{"bar", "baz"}
	result := MergeStringSlices(a, b)
	sort.Strings(result)
	expected1 := []string{"bar", "baz", "foo"}
	if len(result) != len(expected1) {
		t.Fatalf("Test1: expected %v, got %v", expected1, result)
	}
	for i := range expected1 {
		if result[i] != expected1[i] {
			t.Fatalf("Test1: expected %v, got %v", expected1, result)
		}
	}

	// Test case 2: Empty first slice
	c := []string{}
	d := []string{"x", "y"}
	result2 := MergeStringSlices(c, d)
	if len(result2) != 2 {
		t.Fatalf("Test2: expected [x y], got %v", result2)
	}

	// Test case 3: Both empty
	result3 := MergeStringSlices([]string{}, []string{})
	if len(result3) != 0 {
		t.Fatalf("Test3: expected empty, got %v", result3)
	}

	// Test case 4: All duplicates
	e := []string{"a", "b", "c"}
	f := []string{"a", "b", "c"}
	result4 := MergeStringSlices(e, f)
	sort.Strings(result4)
	expected4 := []string{"a", "b", "c"}
	if len(result4) != len(expected4) {
		t.Fatalf("Test4: expected %v, got %v", expected4, result4)
	}
}
'''
    test_file = UTIL_DIR / "merge_gold_test.go"
    test_file.write_text(test_code)

    try:
        result = subprocess.run(
            ["go", "test", "./internal/cri/util/...", "-run", "TestMergeStringSlicesGold", "-v", "-count=1"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
            env=GO_ENV
        )
        assert result.returncode == 0, f"MergeStringSlices test failed:\n{result.stdout}\n{result.stderr}"
    finally:
        test_file.unlink(missing_ok=True)


def test_util_package_compiles():
    """Pass-to-pass: The util package should compile after the changes."""
    result = subprocess.run(
        ["go", "build", "./internal/cri/util"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=GO_ENV
    )
    assert result.returncode == 0, f"util package failed to build: {result.stderr}"


def test_repo_build_setutils():
    """Repo's setutils package builds (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./internal/cri/setutils"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"setutils build failed:\n{r.stderr[-500:]}"


def test_repo_build_util():
    """Repo's util package builds (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./internal/cri/util"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"util build failed:\n{r.stderr[-500:]}"


def test_repo_test_util():
    """Repo's util package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "./internal/cri/util/...", "-count=1"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"util tests failed:\n{r.stderr[-500:]}"


def test_repo_vet_cri():
    """Repo's CRI packages pass go vet (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./internal/cri/setutils/...", "./internal/cri/util/..."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-500:]}"


def test_repo_build_cri_all():
    """All CRI packages build together (pass_to_pass) — catches downstream import breakage."""
    r = subprocess.run(
        ["go", "build", "./internal/cri/..."],
        capture_output=True, text=True, timeout=180, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"CRI packages build failed:\n{r.stderr[-500:]}"


def test_repo_vet_cri_all():
    """All CRI packages pass go vet (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./internal/cri/..."],
        capture_output=True, text=True, timeout=180, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"go vet on all CRI packages failed:\n{r.stderr[-500:]}"


def test_repo_go_mod_verify():
    """Repo's go modules verify successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "mod", "verify"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"go mod verify failed:\n{r.stderr[-500:]}"


def test_repo_test_util_all():
    """Repo's util package tests all pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "./internal/cri/util/...", "-count=1", "-v"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env=GO_ENV
    )
    assert r.returncode == 0, f"util package tests failed:\n{r.stderr[-500:]}"


def test_deprecated_newstring_not_used():
    """Fail-to-pass: NewString function should not exist or be used."""
    result = subprocess.run(
        ["grep", "-r", "func NewString", "./internal/cri/setutils/"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0, "NewString function should not exist in setutils"

    result2 = subprocess.run(
        ["grep", "-r", "func NewInt", "./internal/cri/setutils/"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result2.returncode != 0, "NewInt function should not exist in setutils"


if __name__ == "__main__":
    # Run all tests manually for debugging
    import traceback
    tests = [
        test_int_type_removed,
        test_string_type_removed,
        test_cast_function_removed,
        test_generic_set_still_compiles,
        test_merge_string_slices_behavior,
        test_util_package_compiles,
        test_deprecated_newstring_not_used,
        test_repo_build_setutils,
        test_repo_build_util,
        test_repo_test_util,
        test_repo_vet_cri,
        test_repo_build_cri_all,
        test_repo_vet_cri_all,
        test_repo_go_mod_verify,
        test_repo_test_util_all,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
