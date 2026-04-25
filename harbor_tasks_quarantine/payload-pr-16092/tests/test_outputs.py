import subprocess
import os

REPO = "/workspace/payload"


def test_build_params_trash_true():
    """buildSearchParams includes trash=true when trash is true (fail-to-pass)."""
    r = subprocess.run(
        ["tsx", "-e", """
import { buildSearchParams } from './packages/sdk/src/utilities/buildSearchParams.ts';
const result = buildSearchParams({ trash: true });
if (!result.includes('trash=true')) {
  console.error('FAIL: trash=true not found in:', result);
  process.exit(1);
}
console.log('PASS:', result);
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"buildSearchParams(trash: true) failed:\n{r.stderr}\n{r.stdout}"


def test_build_params_trash_false():
    """buildSearchParams includes trash=false when trash is false (fail-to-pass)."""
    r = subprocess.run(
        ["tsx", "-e", """
import { buildSearchParams } from './packages/sdk/src/utilities/buildSearchParams.ts';
const result = buildSearchParams({ trash: false });
if (!result.includes('trash=false')) {
  console.error('FAIL: trash=false not found in:', result);
  process.exit(1);
}
console.log('PASS:', result);
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"buildSearchParams(trash: false) failed:\n{r.stderr}\n{r.stdout}"


def test_build_params_trash_absent():
    """buildSearchParams omits trash param when trash is absent (pass-to-pass)."""
    r = subprocess.run(
        ["tsx", "-e", """
import { buildSearchParams } from './packages/sdk/src/utilities/buildSearchParams.ts';
const result = buildSearchParams({ depth: 1 });
if (result.includes('trash')) {
  console.error('FAIL: trash should not be in:', result);
  process.exit(1);
}
console.log('PASS:', result);
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"buildSearchParams(without trash) failed:\n{r.stderr}\n{r.stdout}"


def test_build_params_trash_with_other_args():
    """buildSearchParams includes trash alongside other params (fail-to-pass)."""
    r = subprocess.run(
        ["tsx", "-e", """
import { buildSearchParams } from './packages/sdk/src/utilities/buildSearchParams.ts';
const result = buildSearchParams({ depth: 2, draft: true, trash: true, limit: 10 });
if (!result.includes('trash=true')) {
  console.error('FAIL: trash=true not found in:', result);
  process.exit(1);
}
if (!result.includes('depth=2')) {
  console.error('FAIL: depth=2 not found in:', result);
  process.exit(1);
}
if (!result.includes('draft=true')) {
  console.error('FAIL: draft=true not found in:', result);
  process.exit(1);
}
if (!result.includes('limit=10')) {
  console.error('FAIL: limit=10 not found in:', result);
  process.exit(1);
}
console.log('PASS:', result);
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"buildSearchParams(multiple args) failed:\n{r.stderr}\n{r.stdout}"


def test_repo_lint_sdk():
    """Repo's linter passes for SDK package (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/workspace/payload/packages/sdk",
    )
    assert r.returncode == 0, f"SDK lint failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "test:unit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/workspace/payload",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


def test_repo_typecheck():
    """Repo's type checking passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "test:types"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd="/workspace/payload",
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"
