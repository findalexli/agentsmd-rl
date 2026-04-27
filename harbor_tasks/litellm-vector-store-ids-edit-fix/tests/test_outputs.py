"""
Tests for BerriAI/litellm#25133: fix(ui): don't inject vector_store_ids: []
when editing a model.

Bug: Editing a model without vector stores caused the edit form to inject
vector_store_ids: [] into the PATCH payload, breaking Anthropic calls.

Fix: Only include vector_store_ids when it has entries; delete the key
when the model never had vector stores.
"""

import os
import subprocess

REPO = "/workspace/litellm"
UI_DIR = os.path.join(REPO, "ui/litellm-dashboard")
COMPONENT_FILE = os.path.join(UI_DIR, "src/components/model_info_view.tsx")
TEST_FILE = os.path.join(UI_DIR, "src/components/model_info_view.test.tsx")


REGRESSION_TEST_BLOCK = """\

  it("should not include vector_store_ids in update payload when model has none", async () => {
    // Regression: editing a model without vector stores used to inject
    // vector_store_ids: [] into litellm_params, which then propagated to
    // inference requests and broke Anthropic calls.
    const user = userEvent.setup();
    render(<ModelInfoView {...DEFAULT_ADMIN_PROPS} />, { wrapper });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /edit settings/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /edit settings/i }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /save changes/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /save changes/i }));

    await waitFor(() => {
      expect(mockModelPatchUpdateCall).toHaveBeenCalled();
    });

    const updatePayload = mockModelPatchUpdateCall.mock.calls[0][1];
    expect(updatePayload.litellm_params).not.toHaveProperty("vector_store_ids");
  });
"""


def _ensure_regression_test():
    """Inject the regression test into the test file if not already present.

    At base commit the test does not exist; the gold patch adds it.
    When running NOP (no fix applied), we still need the test present
    so it can *fail* and prove the bug exists.
    """
    with open(TEST_FILE, "r") as f:
        content = f.read()

    marker = "should not include vector_store_ids in update payload when model has none"
    if marker in content:
        return  # Already present (gold patch was applied)

    # Insert before the wildcard-models test that follows in the original file
    anchor = '  it("should display health check model field for wildcard models"'
    idx = content.find(anchor)
    if idx == -1:
        raise RuntimeError(
            "Could not find insertion anchor "
            "'should display health check model field for wildcard models' "
            "in test file"
        )

    content = content[:idx] + REGRESSION_TEST_BLOCK + "\n" + content[idx:]

    with open(TEST_FILE, "w") as f:
        f.write(content)


def test_existing_model_info_view_tests():
    """All pre-existing model_info_view.test.tsx tests pass (pass_to_pass).

    Runs the full vitest suite for this component. At base commit there are
    34 tests; after the gold patch there are 35. All must pass.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "src/components/model_info_view.test.tsx"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=UI_DIR,
    )
    assert r.returncode == 0, (
        f"Vitest model_info_view tests failed:\n"
        f"STDOUT (last 3000 chars):\n{r.stdout[-3000:]}\n"
        f"STDERR (last 1000 chars):\n{r.stderr[-1000:]}"
    )


def test_vector_store_ids_not_in_update_payload():
    """Editing a model without vector stores must NOT inject vector_store_ids: []
    into the update payload (fail_to_pass).

    This test renders ModelInfoView with default props (no vector stores),
    clicks Edit Settings -> Save Changes, and asserts that the PATCH payload
    does NOT contain a vector_store_ids key in litellm_params.

    Fails on the base commit (form injects []) and passes after the fix.
    """
    _ensure_regression_test()

    r = subprocess.run(
        [
            "npx", "vitest", "run",
            "-t", "should not include vector_store_ids in update payload when model has none",
            "src/components/model_info_view.test.tsx",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=UI_DIR,
    )
    assert r.returncode == 0, (
        f"Regression test failed (vector_store_ids still injected):\n"
        f"STDOUT (last 3000 chars):\n{r.stdout[-3000:]}\n"
        f"STDERR (last 1000 chars):\n{r.stderr[-1000:]}"
    )
