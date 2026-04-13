"""Tests for TanStack/router PR #7037 - fix TS4023 by converting interface to type."""
import subprocess
import re
import sys
import os

REPO = "/workspace/router"


def test_react_router_interface_to_type():
    """ShouldBlockFnLocation should be a type, not interface (fail-to-pass)."""
    filepath = os.path.join(REPO, "packages/react-router/src/useBlocker.tsx")
    with open(filepath, "r") as f:
        content = f.read()

    assert "interface ShouldBlockFnLocation" not in content,         "ShouldBlockFnLocation is still declared as interface (expected type)"

    assert re.search(r"type ShouldBlockFnLocation\s*<[^>]+>\s*=\s*\{", content),         "ShouldBlockFnLocation should be declared as type with ="


def test_solid_router_interface_to_type():
    """ShouldBlockFnLocation should be a type, not interface (fail-to-pass)."""
    filepath = os.path.join(REPO, "packages/solid-router/src/useBlocker.tsx")
    with open(filepath, "r") as f:
        content = f.read()

    assert "interface ShouldBlockFnLocation" not in content,         "ShouldBlockFnLocation is still declared as interface (expected type)"

    assert re.search(r"type ShouldBlockFnLocation\s*<[^>]+>\s*=\s*\{", content),         "ShouldBlockFnLocation should be declared as type with ="


def test_vue_router_interface_to_type():
    """ShouldBlockFnLocation should be a type, not interface (fail-to-pass)."""
    filepath = os.path.join(REPO, "packages/vue-router/src/useBlocker.tsx")
    with open(filepath, "r") as f:
        content = f.read()

    assert "interface ShouldBlockFnLocation" not in content,         "ShouldBlockFnLocation is still declared as interface (expected type)"

    assert re.search(r"type ShouldBlockFnLocation\s*<[^>]+>\s*=\s*\{", content),         "ShouldBlockFnLocation should be declared as type with ="


def test_useblocker_type_export_regression():
    """Verify the TS4023 regression scenario is fixed (fail-to-pass)."""
    test_file = os.path.join(REPO, "packages/react-router/src/__ts4023_test__.ts")
    tsconfig_file = os.path.join(REPO, "packages/react-router/__ts4023_tsconfig__.json")

    test_content = """
import { useBlocker } from './useBlocker'

export const useCustomBlocker = () => {
  const blocker = useBlocker({ shouldBlockFn: () => true, withResolver: true })
  return { blocker }
}
"""

    tsconfig_content = """
{
  "extends": "./tsconfig.json",
  "include": ["src/__ts4023_test__.ts"]
}
"""

    try:
        with open(test_file, "w") as f:
            f.write(test_content)

        with open(tsconfig_file, "w") as f:
            f.write(tsconfig_content)

        result = subprocess.run(
            ["npx", "tsc", "--project", "__ts4023_tsconfig__.json", "--noEmit"],
            cwd=os.path.join(REPO, "packages/react-router"),
            capture_output=True,
            text=True,
            timeout=60
        )

        os.remove(test_file)
        os.remove(tsconfig_file)

        output = result.stdout + result.stderr
        if "TS4023" in output:
            assert False, "TS4023 error still present"

        assert result.returncode == 0, f"TypeScript compilation failed:\n{output}"
    except Exception:
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(tsconfig_file):
            os.remove(tsconfig_file)
        raise


def test_react_router_types_compile():
    """TypeScript compilation passes for react-router (pass-to-pass)."""
    result = subprocess.run(
        ["npx", "tsc", "-p", "tsconfig.legacy.json", "--noEmit"],
        cwd=os.path.join(REPO, "packages/react-router"),
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"react-router type check failed:\n{result.stderr[-1000:]}"


def test_solid_router_types_compile():
    """TypeScript compilation passes for solid-router (pass-to-pass)."""
    result = subprocess.run(
        ["npx", "tsc", "-p", "tsconfig.legacy.json", "--noEmit"],
        cwd=os.path.join(REPO, "packages/solid-router"),
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"solid-router type check failed:\n{result.stderr[-1000:]}"


def test_vue_router_types_compile():
    """TypeScript compilation passes for vue-router (pass-to-pass)."""
    result = subprocess.run(
        ["npx", "tsc", "-p", "tsconfig.legacy.json", "--noEmit"],
        cwd=os.path.join(REPO, "packages/vue-router"),
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"vue-router type check failed:\n{result.stderr[-1000:]}"


def test_repo_react_router_unit_tests():
    """Repo's unit tests pass for react-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "vitest", "--run"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/react-router",
    )
    assert r.returncode == 0, f"react-router unit tests failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_unit_tests():
    """Repo's unit tests pass for solid-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "vitest", "--run"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/solid-router",
    )
    assert r.returncode == 0, f"solid-router unit tests failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_unit_tests():
    """Repo's unit tests pass for vue-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "vitest", "--run"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/packages/vue-router",
    )
    assert r.returncode == 0, f"vue-router unit tests failed:\n{r.stderr[-500:]}"


def test_repo_react_router_eslint():
    """Repo's ESLint passes for react-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "eslint", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/react-router",
    )
    assert r.returncode == 0, f"react-router eslint failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_eslint():
    """Repo's ESLint passes for solid-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "eslint", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/solid-router",
    )
    assert r.returncode == 0, f"solid-router eslint failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_eslint():
    """Repo's ESLint passes for vue-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "eslint", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/vue-router",
    )
    assert r.returncode == 0, f"vue-router eslint failed:\n{r.stderr[-500:]}"


def test_repo_react_router_publint():
    """Repo's package lint passes for react-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "publint", "--strict", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/react-router",
    )
    assert r.returncode == 0, f"react-router publint failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_publint():
    """Repo's package lint passes for solid-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "publint", "--strict", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/solid-router",
    )
    assert r.returncode == 0, f"solid-router publint failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_publint():
    """Repo's package lint passes for vue-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "publint", "--strict", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/vue-router",
    )
    assert r.returncode == 0, f"vue-router publint failed:\n{r.stderr[-500:]}"


def test_repo_react_router_attw():
    """Repo's type exports are valid for react-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "attw", "--ignore-rules", "no-resolution", "--pack", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/react-router",
    )
    assert r.returncode == 0, f"react-router attw failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_attw():
    """Repo's type exports are valid for solid-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "attw", "--ignore-rules", "no-resolution", "--pack", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/solid-router",
    )
    assert r.returncode == 0, f"solid-router attw failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_attw():
    """Repo's type exports are valid for vue-router (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "attw", "--ignore-rules", "no-resolution", "--pack", "."],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/packages/vue-router",
    )
    assert r.returncode == 0, f"vue-router attw failed:\n{r.stderr[-500:]}"


def test_repo_react_router_useblocker_tests():
    """Repo's useBlocker-specific tests pass for react-router (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tests/useBlocker.test.tsx"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/react-router",
    )
    assert r.returncode == 0, f"react-router useBlocker tests failed:\n{r.stderr[-500:]}"


def test_repo_react_router_blocker_tests():
    """Repo's blocker-specific tests pass for react-router (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tests/blocker.test.tsx"],
        capture_output=True, text=True, timeout=180, cwd=f"{REPO}/packages/react-router",
    )
    assert r.returncode == 0, f"react-router blocker tests failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_useblocker_tests():
    """Repo's useBlocker-specific tests pass for solid-router (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tests/useBlocker.test.tsx"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/solid-router",
    )
    assert r.returncode == 0, f"solid-router useBlocker tests failed:\n{r.stderr[-500:]}"


def test_repo_solid_router_blocker_tests():
    """Repo's blocker-specific tests pass for solid-router (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tests/blocker.test.tsx"],
        capture_output=True, text=True, timeout=180, cwd=f"{REPO}/packages/solid-router",
    )
    assert r.returncode == 0, f"solid-router blocker tests failed:\n{r.stderr[-500:]}"


def test_repo_vue_router_blocker_tests():
    """Repo's blocker-specific tests pass for vue-router (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tests/blocker.test.tsx"],
        capture_output=True, text=True, timeout=180, cwd=f"{REPO}/packages/vue-router",
    )
    assert r.returncode == 0, f"vue-router blocker tests failed:\n{r.stderr[-500:]}"


def test_repo_router_core_types_compile():
    """TypeScript compilation passes for router-core (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=180, cwd=f"{REPO}/packages/router-core",
    )
    assert r.returncode == 0, f"router-core type check failed:\n{r.stderr[-500:]}"


def test_repo_router_core_unit_tests():
    """Repo's unit tests pass for router-core (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/router-core",
    )
    assert r.returncode == 0, f"router-core unit tests failed:\n{r.stderr[-500:]}"
