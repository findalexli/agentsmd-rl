"""Behavioral tests for ant-design#57027: replace `any` with `UploadRef`.

Strategy: place small TypeScript fixture files in the repo root that exercise
the type-system contract introduced by the fix, then run the project's
`tsc --noEmit` and inspect output for our fixture's filenames. Pre-existing
unrelated tsc errors are ignored — we only care whether our fixtures
specifically compile cleanly (or, for the negative test, error on the wrong
type).
"""
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/ant-design")
TSC_ENV = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=8192"}
TSC_TIMEOUT = 600


def _run_tsc():
    """Run the project's `tsc --noEmit`. Returns (exit_code, combined_output)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=TSC_TIMEOUT,
        env=TSC_ENV,
    )
    return r.returncode, r.stdout + r.stderr


def _errors_for(name: str, output: str):
    return [line for line in output.splitlines() if name in line]


@pytest.fixture
def uploadref_export_fixture():
    fixture = REPO / "_uploadref_export_check.tsx"
    fixture.write_text(
        "import type { UploadRef } from './components/upload';\n"
        "const _x: UploadRef<File> | null = null;\n"
        "export default _x;\n"
    )
    yield fixture
    fixture.unlink(missing_ok=True)


@pytest.fixture
def ref_narrow_fixture():
    fixture = REPO / "_ref_narrow_check.tsx"
    fixture.write_text(
        "import * as React from 'react';\n"
        "import Upload from './components/upload';\n"
        "\n"
        "declare const wrongRef: React.RefObject<string | null>;\n"
        "export const _bad = <Upload<File> ref={wrongRef} />;\n"
    )
    yield fixture
    fixture.unlink(missing_ok=True)


def test_uploadref_exported_from_index(uploadref_export_fixture):
    """UploadRef must be a public named export of components/upload/index.tsx.

    A fixture imports `UploadRef` from `./components/upload`. Before the fix,
    UploadRef is only defined in `components/upload/Upload.tsx` and is NOT
    re-exported from the index, so tsc reports TS2614 / TS2459 on the
    fixture's import line. After the fix, the fixture compiles cleanly.
    """
    _, out = _run_tsc()
    fixture_errors = _errors_for("_uploadref_export_check.tsx", out)
    assert not fixture_errors, (
        "components/upload/index.tsx must re-export the UploadRef type so "
        "consumers can do `import type { UploadRef } from 'antd/.../upload'`. "
        "tsc errors observed:\n" + "\n".join(fixture_errors)
    )


def test_compound_ref_narrowed_to_uploadref(ref_narrow_fixture):
    """The Upload compound component's ref type must be `UploadRef<U>` not `any`.

    A fixture passes a `RefObject<string | null>` to `<Upload<File> ref={...} />`.
    Before the fix, the compound component type uses `RefAttributes<any>`
    so any ref shape compiles. After the fix it uses
    `RefAttributes<UploadRef<U>>`, so the wrong-typed ref must be rejected
    with TS2322.
    """
    _, out = _run_tsc()
    fixture_lines = _errors_for("_ref_narrow_check.tsx", out)
    has_type_mismatch = any("TS2322" in line for line in fixture_lines)
    assert has_type_mismatch, (
        "Upload's compound type must reject ref objects whose inner type "
        "is not `UploadRef<U>`. Expected TS2322 on the fixture, got:\n"
        + ("\n".join(fixture_lines) if fixture_lines else "(no errors at all — ref still accepts any)")
    )


def test_no_new_tsc_errors_outside_known_baseline():
    """Project tsc must not regress: only the pre-existing watermark error
    is allowed; the agent's edits must not introduce any new tsc errors
    elsewhere in the codebase.
    """
    code, out = _run_tsc()
    error_lines = [
        line for line in out.splitlines()
        if "error TS" in line and "_uploadref_export_check.tsx" not in line
        and "_ref_narrow_check.tsx" not in line
    ]
    unexpected = [line for line in error_lines if "components/watermark/useWatermark.ts" not in line]
    assert not unexpected, (
        "Unexpected tsc errors introduced outside the known baseline:\n"
        + "\n".join(unexpected[:30])
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_lib_es_module_compile():
    """pass_to_pass | CI job 'test lib/es module' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_check_build_files():
    """pass_to_pass | CI job 'build' → step 'check build files'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut test:dekko'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'check build files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")