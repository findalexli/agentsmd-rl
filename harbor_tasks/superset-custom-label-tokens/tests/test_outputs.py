"""
Tests verify that the agent has implemented custom label theme tokens
(labelPublished*, labelDraft*, labelDatasetPhysical*, labelDatasetVirtual*).

Strategy: copy gold test fixtures into the repo at the right paths, then run
jest on those files. The new test files exercise the new theme-token behavior;
they fail at base because the source doesn't reference the tokens, and pass
when the agent's implementation matches the gold patch.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/superset"
FRONTEND = f"{REPO}/superset-frontend"
LABEL_DIR = f"{FRONTEND}/packages/superset-ui-core/src/components/Label/reusable"
THEME_UTILS_DIR = f"{FRONTEND}/src/theme/utils"
GOLD_DIR = "/tests/gold_tests"

JEST_BIN = f"{FRONTEND}/node_modules/.bin/jest"


def _stage_gold_tests():
    """Copy gold test fixtures into the repo; idempotent."""
    shutil.copy(f"{GOLD_DIR}/DatasetTypeLabel.test.tsx",
                f"{LABEL_DIR}/DatasetTypeLabel.test.tsx")
    shutil.copy(f"{GOLD_DIR}/PublishedLabel.test.tsx",
                f"{LABEL_DIR}/PublishedLabel.test.tsx")
    shutil.copy(f"{GOLD_DIR}/testUtils.tsx",
                f"{LABEL_DIR}/testUtils.tsx")
    shutil.copy(f"{GOLD_DIR}/antdTokenNames_extra.test.ts",
                f"{THEME_UTILS_DIR}/antdTokenNames_extra.test.ts")


def _run_jest(test_path: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run jest on a specific test file from the frontend root."""
    env = os.environ.copy()
    env["NODE_ENV"] = "test"
    env["NODE_OPTIONS"] = "--max-old-space-size=8192"
    env["TZ"] = "America/New_York"
    rel = os.path.relpath(test_path, FRONTEND)
    return subprocess.run(
        [JEST_BIN, "--silent", "--no-coverage", "--runInBand", rel],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _stage_and_run(test_path: str, timeout: int = 600):
    _stage_gold_tests()
    r = _run_jest(test_path, timeout=timeout)
    return r


# ---------------- f2p tests ----------------

def test_published_label_tokens():
    """PublishedLabel uses labelPublished* / labelDraft* tokens (fail_to_pass)."""
    r = _stage_and_run(f"{LABEL_DIR}/PublishedLabel.test.tsx", timeout=600)
    assert r.returncode == 0, (
        f"PublishedLabel.test.tsx failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_dataset_type_label_tokens():
    """DatasetTypeLabel uses labelDatasetPhysical*/Virtual* tokens (fail_to_pass)."""
    r = _stage_and_run(f"{LABEL_DIR}/DatasetTypeLabel.test.tsx", timeout=600)
    assert r.returncode == 0, (
        f"DatasetTypeLabel.test.tsx failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_antd_token_names_recognize_label_tokens():
    """antdTokenNames recognizes the 16 new label tokens (fail_to_pass)."""
    r = _stage_and_run(
        f"{THEME_UTILS_DIR}/antdTokenNames_extra.test.ts", timeout=300
    )
    assert r.returncode == 0, (
        f"antdTokenNames_extra.test.ts failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_repo_antd_token_names_existing(  ):
    """Existing antdTokenNames.test.ts continues to pass (pass_to_pass).

    The PR adds new tokens to SUPERSET_CUSTOM_TOKENS but should not break
    the existing token-validation tests that were already in the repo.
    """
    test_path = f"{THEME_UTILS_DIR}/antdTokenNames.test.ts"
    r = _run_jest(test_path, timeout=300)
    assert r.returncode == 0, (
        f"Existing antdTokenNames.test.ts regressed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_types_ts_declares_label_tokens():
    """SupersetSpecificTokens interface declares the 16 new label tokens (fail_to_pass).

    This is a TypeScript declaration check: the agent must add these optional
    fields to the SupersetSpecificTokens interface for the tests to type-check.
    """
    types_path = Path(f"{FRONTEND}/packages/superset-core/src/theme/types.ts")
    content = types_path.read_text()
    expected_tokens = [
        "labelPublishedColor", "labelPublishedBg",
        "labelPublishedBorderColor", "labelPublishedIconColor",
        "labelDraftColor", "labelDraftBg",
        "labelDraftBorderColor", "labelDraftIconColor",
        "labelDatasetPhysicalColor", "labelDatasetPhysicalBg",
        "labelDatasetPhysicalBorderColor", "labelDatasetPhysicalIconColor",
        "labelDatasetVirtualColor", "labelDatasetVirtualBg",
        "labelDatasetVirtualBorderColor", "labelDatasetVirtualIconColor",
    ]
    # Check declarations appear within the SupersetSpecificTokens interface
    iface_idx = content.find("interface SupersetSpecificTokens")
    assert iface_idx >= 0, "SupersetSpecificTokens interface not found"
    iface_block = content[iface_idx:iface_idx + 5000]
    for t in expected_tokens:
        assert f"{t}?" in iface_block or f"{t}:" in iface_block, (
            f"Token {t} not declared in SupersetSpecificTokens interface"
        )
