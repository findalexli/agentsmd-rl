"""
Task: vscode-changes-item-action-bar
Repo: microsoft/vscode @ d919f292bffcc695c5b23b12708c3a2ce3693f2a
PR:   306366

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TS_FILE = f"{REPO}/src/vs/sessions/contrib/changes/browser/changesView.ts"
CSS_FILE = f"{REPO}/src/vs/sessions/contrib/changes/browser/media/changesView.css"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """TypeScript must compile without errors after the fix."""
    # AST-only because: TypeScript, not Python
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_viewmodel_parameter_in_constructor():
    """ChangesTreeRenderer constructor must accept a viewModel parameter typed ChangesViewModel."""
    # AST-only because: TypeScript
    src = Path(TS_FILE).read_text()
    assert "private viewModel: ChangesViewModel" in src, (
        "ChangesTreeRenderer constructor is missing the 'private viewModel: ChangesViewModel' parameter. "
        "The renderer needs the viewModel to bind the version-mode context key."
    )


# [pr_diff] fail_to_pass
def test_viewmodel_passed_to_renderer():
    """createInstance must pass this.viewModel as the first argument to ChangesTreeRenderer."""
    # AST-only because: TypeScript
    src = Path(TS_FILE).read_text()
    assert "createInstance(ChangesTreeRenderer, this.viewModel," in src, (
        "ChangesTreeRenderer is not instantiated with this.viewModel as the first argument. "
        "Expected: createInstance(ChangesTreeRenderer, this.viewModel, ...)"
    )


# [pr_diff] fail_to_pass
def test_version_mode_context_key_binding():
    """bindContextKey must be called for changesVersionModeContextKey inside renderTemplate."""
    # AST-only because: TypeScript
    src = Path(TS_FILE).read_text()
    assert "bindContextKey(changesVersionModeContextKey" in src, (
        "Missing bindContextKey call for changesVersionModeContextKey. "
        "The renderer must bind the version-mode context key so menu contributions can react to mode changes."
    )
    assert "this.viewModel.versionModeObs.read(reader)" in src, (
        "Missing 'this.viewModel.versionModeObs.read(reader)' — "
        "the context key binding must read the version mode from the view model."
    )


# [pr_diff] fail_to_pass
def test_css_conditional_hide_diff_stats():
    """CSS must hide diff stats only when the action bar has actions, not unconditionally."""
    # AST-only because: CSS, not Python
    css = Path(CSS_FILE).read_text()

    # New conditional selector must be present
    assert ":has(.chat-collapsible-list-action-bar:not(.has-no-actions))" in css, (
        "CSS is missing the :has(:not(.has-no-actions)) selector. "
        "Diff stats should only be hidden when the toolbar actually has actions to display."
    )

    # Old unconditional selector must be removed
    assert ".monaco-list-row:hover .working-set-line-counts," not in css, (
        "Old unconditional CSS selector still present: "
        "'.monaco-list-row:hover .working-set-line-counts,' must be replaced with the conditional form."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / structure
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_class_structure_preserved():
    """ChangesTreeRenderer class structure and interface implementation must remain intact."""
    # AST-only because: TypeScript
    src = Path(TS_FILE).read_text()
    assert "class ChangesTreeRenderer" in src, "ChangesTreeRenderer class is missing"
    assert "TEMPLATE_ID" in src, "TEMPLATE_ID constant is missing from ChangesTreeRenderer"
    assert "ICompressibleTreeRenderer<ChangesTreeElement" in src, (
        "ChangesTreeRenderer no longer implements ICompressibleTreeRenderer<ChangesTreeElement"
    )


# ---------------------------------------------------------------------------
# Agent config (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:144 @ d919f292
def test_disposables_registered_immediately():
    """New bindContextKey call must be wrapped in templateDisposables.add() immediately."""
    # AST-only because: TypeScript
    # Rule: "You MUST deal with disposables by registering them immediately after creation for later disposal."
    src = Path(TS_FILE).read_text()
    assert "templateDisposables.add(bindContextKey(changesVersionModeContextKey" in src, (
        "The bindContextKey(changesVersionModeContextKey, ...) result is not registered to templateDisposables. "
        "Disposables must be registered immediately after creation to avoid leaks."
    )
