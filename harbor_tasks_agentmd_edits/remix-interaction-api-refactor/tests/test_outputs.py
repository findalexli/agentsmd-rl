"""
Task: remix-interaction-api-refactor
Repo: remix-run/remix @ 90016e313b24a05c5862a853a3b518290d9017ba
PR:   10823

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/remix"
PKG = f"{REPO}/packages/interaction"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """TypeScript files in packages/interaction must compile without errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=PKG,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_removed_exports():
    """capture and listenWith must NOT be exported from the package."""
    index_ts = Path(PKG) / "src" / "index.ts"
    content = index_ts.read_text()
    # Extract the export block (everything before 'from')
    export_block = content.split("from")[0] if "from" in content else content
    # capture and listenWith should not be in the export list
    assert not re.search(r"\bcapture\b", export_block), \
        "capture should be removed from exports"
    assert "listenWith" not in export_block, \
        "listenWith should be removed from exports"


# [pr_diff] fail_to_pass
def test_new_type_exports():
    """Interaction and ContainerOptions types must be exported."""
    index_ts = Path(PKG) / "src" / "index.ts"
    content = index_ts.read_text()
    assert "Interaction" in content, \
        "Interaction type should be exported from index.ts"
    assert "ContainerOptions" in content, \
        "ContainerOptions type should be exported from index.ts"


# [pr_diff] fail_to_pass
def test_interaction_interface():
    """Interaction interface must define target, signal, raise, and on members."""
    interaction_ts = Path(PKG) / "src" / "lib" / "interaction.ts"
    content = interaction_ts.read_text()

    # Check Interaction interface/type exists with required members
    assert re.search(r"(export\s+)?(interface|type)\s+Interaction\b", content), \
        "Interaction interface/type must be defined"

    # Extract the interface body
    match = re.search(
        r"(?:export\s+)?(?:interface|type)\s+Interaction\s*\{([\s\S]*?)\n\}",
        content,
    )
    assert match, "Could not find Interaction interface body"
    body = match.group(1)

    for member in ["target", "signal", "raise", "on"]:
        assert member in body, \
            f"Interaction interface must include '{member}' member"


# [pr_diff] fail_to_pass
def test_create_container_options_object():
    """createContainer must accept an options object, not a bare AbortSignal."""
    interaction_ts = Path(PKG) / "src" / "lib" / "interaction.ts"
    content = interaction_ts.read_text()

    # Find createContainer function signature
    match = re.search(
        r"export\s+function\s+createContainer[^{]+\{",
        content,
        re.DOTALL,
    )
    assert match, "createContainer function not found"
    sig = match.group(0)

    # Should accept options object, not bare signal
    assert "options" in sig.lower() or "ContainerOptions" in sig, \
        "createContainer should accept an options parameter (not bare signal)"
    # Should NOT have signal?: AbortSignal as direct parameter
    # (it's ok inside ContainerOptions)
    sig_lines = sig.split("\n")
    param_lines = [l for l in sig_lines if "signal" in l.lower()]
    for line in param_lines:
        assert "AbortSignal" not in line or "ContainerOptions" in content, \
            "createContainer should not take bare AbortSignal as parameter"


# [pr_diff] fail_to_pass
def test_on_no_signal_overload():
    """on() must not accept AbortSignal as second argument."""
    interaction_ts = Path(PKG) / "src" / "lib" / "interaction.ts"
    content = interaction_ts.read_text()

    # Find all on() function signatures/overloads
    on_sigs = re.findall(
        r"export\s+function\s+on[^{]*(?:\{|$)",
        content,
        re.MULTILINE,
    )
    assert len(on_sigs) >= 1, "on() function not found"

    for sig in on_sigs:
        assert "AbortSignal" not in sig, \
            f"on() should not accept AbortSignal parameter: {sig.strip()}"
        assert "signalOrListeners" not in sig, \
            "on() should not have signalOrListeners parameter"


# [pr_diff] fail_to_pass
def test_interaction_setup_this_context():
    """InteractionSetup type must use this: Interaction pattern."""
    interaction_ts = Path(PKG) / "src" / "lib" / "interaction.ts"
    content = interaction_ts.read_text()

    # Find InteractionSetup type
    match = re.search(r"type\s+InteractionSetup\s*=\s*([^\n]+)", content)
    assert match, "InteractionSetup type not found"
    typedef = match.group(1)
    assert "this" in typedef and "Interaction" in typedef, \
        f"InteractionSetup should use 'this: Interaction' pattern, got: {typedef}"


# [pr_diff] fail_to_pass
def test_onerror_support():
    """Containers must support onError handler for listener errors."""
    interaction_ts = Path(PKG) / "src" / "lib" / "interaction.ts"
    content = interaction_ts.read_text()

    # ContainerOptions or similar must include onError
    assert "onError" in content, \
        "onError handler must be defined somewhere in interaction.ts"

    # The createBinding or wrappedListener should use onError
    assert "catch" in content or ".catch(" in content, \
        "Error handling (try/catch or .catch) must be present for async listener errors"

    # Check that onError is in ContainerOptions or container creation
    assert re.search(r"onError.*(?:error|unknown)", content), \
        "onError should be typed to accept errors"


# [pr_diff] fail_to_pass
def test_descriptor_extends_options():
    """Descriptor interface must extend AddEventListenerOptions directly."""
    interaction_ts = Path(PKG) / "src" / "lib" / "interaction.ts"
    content = interaction_ts.read_text()

    # Find Descriptor interface
    match = re.search(r"interface\s+Descriptor<[^>]+>\s*(extends[^{]*)?\{", content)
    assert match, "Descriptor interface not found"

    extends_clause = match.group(1) or ""
    # Should extend AddEventListenerOptions (not have nested options property)
    assert "AddEventListenerOptions" in extends_clause, \
        f"Descriptor should extend AddEventListenerOptions, got: {match.group(0)}"

    # Check it has listener but NOT a nested options property
    desc_match = re.search(
        r"interface\s+Descriptor<[^>]+>[^{]*\{([^}]+)",
        content,
    )
    if desc_match:
        body = desc_match.group(1)
        assert "listener" in body, "Descriptor must have 'listener' member"
        # Should NOT have 'options: AddEventListenerOptions'
        assert not re.search(r"\boptions\s*:", body), \
            "Descriptor should not have nested 'options' property"


# [pr_diff] fail_to_pass
def test_builtin_interactions_use_this():
    """Built-in interactions (form, keys, popover, press) must use this context."""
    interactions_dir = Path(PKG) / "src" / "lib" / "interactions"
    for fname in ["form.ts", "keys.ts", "popover.ts", "press.ts"]:
        fpath = interactions_dir / fname
        content = fpath.read_text()
        # Should import Interaction type
        assert "Interaction" in content, \
            f"{fname} should import Interaction type"
        # Should use this: Interaction pattern in function signature
        assert "this: Interaction" in content or "this.target" in content, \
            f"{fname} should use this context pattern"
        # Should NOT use old (target, signal) pattern
        assert not re.search(
            r"function\s+\w+\(target:\s*EventTarget,\s*signal:\s*AbortSignal\)",
            content,
        ), f"{fname} should not use old (target, signal) pattern"


# ---------------------------------------------------------------------------
# Config file update checks (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
def test_readme_no_capture_listenwith():
    """README should not import capture or listenWith."""
    readme_md = Path(PKG) / "README.md"
    content = readme_md.read_text()

    # Should NOT show capture or listenWith as importable functions
    import_lines = [
        line for line in content.splitlines()
        if "import" in line and "from" in line and "interaction" in line.lower()
    ]
    for line in import_lines:
        assert "capture" not in line, \
            f"README should not import capture: {line.strip()}"
        assert "listenWith" not in line, \
            f"README should not import listenWith: {line.strip()}"

    # Should show descriptor object pattern
    assert "listener(event)" in content or "listener:" in content, \
        "README should document the new descriptor object pattern with 'listener' property"


# [config_edit] fail_to_pass
def test_readme_this_context():
    """README should show this: Interaction pattern for custom interactions."""
    readme_md = Path(PKG) / "README.md"
    content = readme_md.read_text()

    # Custom interaction example should use this context
    assert "this: Interaction" in content or "this.target" in content, \
        "README should show the Interaction context pattern (this.target, this.on, etc.)"
    assert "this.on(" in content or "this.on(this" in content, \
        "README should show this.on() usage in custom interaction example"


# [config_edit] fail_to_pass
def test_changelog_unreleased():
    """CHANGELOG should document breaking changes in Unreleased section."""
    changelog_md = Path(PKG) / "CHANGELOG.md"
    content = changelog_md.read_text()
    content_lower = content.lower()

    # Must have an Unreleased section
    assert "## unreleased" in content_lower, \
        "CHANGELOG.md should have an '## Unreleased' section"

    # Must mention breaking changes
    assert "breaking" in content_lower, \
        "CHANGELOG should document breaking changes"

    # Should mention key API changes
    assert "interaction" in content_lower, \
        "CHANGELOG should mention the Interaction API changes"
    assert "descriptor" in content_lower or "capture" in content_lower \
        or "listenWith" in content_lower.replace("listenwith", "listenWith"), \
        "CHANGELOG should mention descriptor/capture/listenWith changes"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_type_exports_use_type_keyword():
    """All type exports should use 'type' keyword per AGENTS.md."""
    index_ts = Path(PKG) / "src" / "index.ts"
    content = index_ts.read_text()

    # All type exports should use 'type' keyword
    type_names = ["Dispatched", "EventListeners", "EventsContainer",
                  "InteractionSetup", "TypedEventTarget", "Interaction",
                  "ContainerOptions"]
    for name in type_names:
        if name in content:
            # Check that it appears with 'type' prefix in the export
            assert re.search(rf"\btype\s+{name}\b", content), \
                f"'{name}' should be exported with 'export type' or 'type' prefix per AGENTS.md"


# [agent_config] pass_to_pass
def test_changelog_heading_format():
    """Changelog uses '## Unreleased' heading format per AGENTS.md."""
    changelog_md = Path(PKG) / "CHANGELOG.md"
    content = changelog_md.read_text()

    # If there's an unreleased section, it must use exact heading format
    if "unreleased" in content.lower():
        assert "## Unreleased" in content, \
            "AGENTS.md requires '## Unreleased' heading (not '## HEAD' or other variants)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's pnpm typecheck passes for interaction package (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/interaction", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Typecheck failed:\n{r.stdout}\n{r.stderr}"
    )


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's pnpm build passes for interaction package (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/interaction", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Build failed:\n{r.stdout}\n{r.stderr}"
    )


# [repo_tests] pass_to_pass
def test_repo_format():
    """Repo's prettier formatting check passes for interaction package (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{PKG}/src/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Format check failed:\n{r.stdout}\n{r.stderr}"
    )
