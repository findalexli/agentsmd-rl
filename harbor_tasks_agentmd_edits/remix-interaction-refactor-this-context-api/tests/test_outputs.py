"""
Task: remix-interaction-refactor-this-context-api
Repo: remix-run/remix @ 90016e313b24a05c5862a853a3b518290d9017ba
PR:   10823

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"
INTERACTION_SRC = Path(REPO) / "packages/interaction/src/lib/interaction.ts"
INDEX_SRC = Path(REPO) / "packages/interaction/src/index.ts"
README = Path(REPO) / "packages/interaction/README.md"
CHANGELOG = Path(REPO) / "packages/interaction/CHANGELOG.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — typecheck
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typecheck():
    """TypeScript compilation passes for the interaction package."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/interaction", "run", "typecheck"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"TypeScript typecheck failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core API refactor
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interaction_interface_exported():
    """Interaction type must be exported from the package index."""
    content = INDEX_SRC.read_text()
    assert "type Interaction" in content, (
        "Interaction type should be exported from index.ts"
    )


# [pr_diff] fail_to_pass
def test_container_options_exported():
    """ContainerOptions type must be exported from the package index."""
    content = INDEX_SRC.read_text()
    assert "ContainerOptions" in content, (
        "ContainerOptions type should be exported from index.ts"
    )


# [pr_diff] fail_to_pass
def test_capture_listenWith_removed():
    """capture() and listenWith() helpers must be removed from exports."""
    content = INDEX_SRC.read_text()
    # These value exports should no longer exist
    assert "listenWith" not in content, (
        "listenWith should not be exported from index.ts"
    )
    # Check capture is not a value export (the word may appear in comments)
    lines = content.splitlines()
    export_lines = [l.strip().rstrip(",") for l in lines]
    for line in export_lines:
        if line == "capture":
            raise AssertionError("capture should not be exported as a value from index.ts")


# [pr_diff] fail_to_pass
def test_interaction_handle_class():
    """InteractionHandle class should exist implementing the Interaction interface."""
    content = INTERACTION_SRC.read_text()
    assert "class InteractionHandle" in content, (
        "InteractionHandle class not found in interaction.ts"
    )
    assert "implements Interaction" in content, (
        "InteractionHandle should implement the Interaction interface"
    )


# [pr_diff] fail_to_pass
def test_on_function_simplified():
    """on() function should not have an AbortSignal overload."""
    content = INTERACTION_SRC.read_text()
    # Find the on() function section - look for export function on
    # The old code had multiple overloads including signal: AbortSignal
    in_on_section = False
    on_lines = []
    for line in content.splitlines():
        if "export function on" in line:
            in_on_section = True
        if in_on_section:
            on_lines.append(line)
            # End at the closing brace of the function
            if line.strip() == "}" and len(on_lines) > 2:
                break
    on_section = "\n".join(on_lines)
    assert "AbortSignal" not in on_section, (
        "on() function should not accept AbortSignal parameter"
    )
    assert "signalOrListeners" not in on_section, (
        "on() should not have the signal-or-listeners overload logic"
    )


# [pr_diff] fail_to_pass
def test_create_container_accepts_options():
    """createContainer should accept ContainerOptions, not bare AbortSignal."""
    content = INTERACTION_SRC.read_text()
    assert "options?: ContainerOptions" in content or "options: ContainerOptions" in content, (
        "createContainer should accept ContainerOptions parameter"
    )


# [pr_diff] fail_to_pass
def test_on_error_handler():
    """Container should support onError callback for listener error handling."""
    content = INTERACTION_SRC.read_text()
    assert "onError" in content, (
        "interaction.ts should have onError handler support"
    )
    # Verify it's in the ContainerOptions type
    assert "onError?" in content or "onError:" in content, (
        "onError should be declared in ContainerOptions"
    )


# [pr_diff] fail_to_pass
def test_interactions_use_this_context():
    """Interaction setup functions in submodules should use this: Interaction."""
    for submodule in ["form.ts", "keys.ts", "popover.ts", "press.ts"]:
        path = Path(REPO) / "packages/interaction/src/lib/interactions" / submodule
        content = path.read_text()
        assert "this: Interaction" in content, (
            f"{submodule}: interaction setup should use 'this: Interaction' parameter"
        )
        assert "this.target" in content, (
            f"{submodule}: should use this.target instead of target parameter"
        )
        assert "this.on(" in content, (
            f"{submodule}: should use this.on() for event binding"
        )


# ---------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_removes_old_api():
    """README should not reference removed capture()/listenWith() helpers."""
    content = README.read_text()
    assert "capture((event)" not in content, (
        "README should not show old capture() helper syntax"
    )
    assert "listenWith(" not in content, (
        "README should not reference listenWith() helper"
    )
    # Old on() signal overload should be removed from docs
    assert "on(button, controller.signal," not in content, (
        "README should not show old on(target, signal, ...) overload"
    )


# [pr_diff] fail_to_pass
def test_readme_documents_new_api():
    """README should document the new Interaction context and descriptor API."""
    content = README.read_text()
    # New this-context interaction pattern
    assert "this.target" in content or "this: Interaction" in content, (
        "README should document the new Interaction this-context pattern"
    )
    # New descriptor syntax
    assert "capture: true" in content, (
        "README should show inline descriptor objects with capture: true"
    )


# [agent_config] fail_to_pass — AGENTS.md:24-25 @ base commit
def test_changelog_unreleased_section():
    """CHANGELOG must use '## Unreleased' heading per AGENTS.md formatting rules."""
    content = CHANGELOG.read_text()
    assert "## Unreleased" in content, (
        "CHANGELOG should have '## Unreleased' section per AGENTS.md line 25"
    )
    assert "BREAKING CHANGE" in content, (
        "Unreleased section should document the breaking API changes"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — agent config compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:18 @ base commit
def test_import_type_syntax():
    """Type imports must use 'import type' syntax per AGENTS.md style rules."""
    content = INDEX_SRC.read_text()
    # Every type export should use 'type' keyword
    for line in content.splitlines():
        stripped = line.strip().rstrip(",")
        # Lines that export types like Dispatched, EventListeners, etc.
        # should have the 'type' keyword
        if stripped in ("Dispatched", "EventListeners", "EventsContainer",
                        "InteractionSetup", "TypedEventTarget",
                        "Interaction", "ContainerOptions"):
            raise AssertionError(
                f"'{stripped}' should be exported with 'type' keyword: "
                f"'type {stripped}' per AGENTS.md line 18"
            )


# [agent_config] pass_to_pass — AGENTS.md:18 @ base commit
def test_ts_extensions_in_imports():
    """Import paths must include .ts extensions per AGENTS.md style rules."""
    content = INDEX_SRC.read_text()
    for line in content.splitlines():
        if "from '" in line or 'from "' in line:
            # Local imports should end with .ts
            if "./" in line or "../" in line:
                assert ".ts" in line, (
                    f"Import should use .ts extension per AGENTS.md: {line.strip()}"
                )
