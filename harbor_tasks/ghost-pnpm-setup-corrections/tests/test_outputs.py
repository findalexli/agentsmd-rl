"""Tests for ghost-pnpm-setup-corrections task."""

from __future__ import annotations

import os
import re
import subprocess
import tomllib
from pathlib import Path

REPO = Path("/workspace/Ghost")


# ---------------------------------------------------------------------------
# fail_to_pass — assertions about the corrected setup commands.
# ---------------------------------------------------------------------------

def test_codex_environment_uses_pnpm_run_setup() -> None:
    """The Codex environment's `[setup].script` must invoke `pnpm run setup`,
    not the bare `pnpm setup` (which is pnpm's built-in command, not Ghost's
    setup script). Verified by parsing the TOML and inspecting the field.
    """
    toml_path = REPO / ".codex/environments/environment.toml"
    with toml_path.open("rb") as f:
        data = tomllib.load(f)

    script = data["setup"]["script"].strip()
    assert "pnpm run setup" in script, (
        f"Expected `pnpm run setup` in [setup].script, got:\n{script!r}"
    )

    # The bare `pnpm setup` (no `run`) must not survive — match it as a
    # standalone token to avoid colliding with `pnpm run setup`.
    lines_without_run = [
        ln for ln in script.splitlines()
        if ln.strip() == "pnpm setup"
    ]
    assert not lines_without_run, (
        f"Found bare `pnpm setup` line in script: {lines_without_run}"
    )


def test_enforce_package_manager_message_uses_pnpm_run_setup() -> None:
    """Run the enforcement script with a non-pnpm user-agent and verify the
    error message it prints recommends `pnpm run setup`, not the broken
    `pnpm setup`. This actually executes the JavaScript file.
    """
    script = REPO / ".github/scripts/enforce-package-manager.js"
    env = {**os.environ, "npm_config_user_agent": "yarn/1.22.0 npm/? node/v20.0.0"}
    r = subprocess.run(
        ["node", str(script)],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert r.returncode == 1, f"Expected exit 1 for non-pnpm UA, got {r.returncode}"

    # The replacement table must point at `pnpm run setup`.
    assert "yarn setup   -> pnpm run setup" in r.stderr, (
        "Expected `yarn setup   -> pnpm run setup` in error message; got:\n"
        f"{r.stderr}"
    )

    # The broken old recommendation must be gone. Use a regex with a word
    # boundary so we don't false-match the prefix of `pnpm run setup`.
    assert not re.search(r"yarn setup\s+->\s+pnpm setup\b", r.stderr), (
        "Old replacement (`yarn setup -> pnpm setup` without `run`) is "
        "still present in the error message."
    )


def test_agents_md_dev_block_corepack_and_run_setup() -> None:
    """The root AGENTS.md `### Development` code block must teach agents to
    enable corepack first and then invoke `pnpm run setup`. The bare
    `pnpm setup` line must be gone from that block.
    """
    text = (REPO / "AGENTS.md").read_text()

    # The two required new lines.
    assert "corepack enable pnpm" in text, (
        "AGENTS.md must mention `corepack enable pnpm`."
    )
    assert "pnpm run setup" in text, (
        "AGENTS.md must mention `pnpm run setup`."
    )

    # The Development block specifically must contain both — find it and check.
    # The block follows `### Development` and is fenced ``` to ```.
    marker = "### Development"
    idx = text.find(marker)
    assert idx != -1, "AGENTS.md missing `### Development` heading."
    block_start = text.find("```", idx)
    block_end = text.find("```", block_start + 3)
    block = text[block_start:block_end]

    assert "corepack enable pnpm" in block, (
        f"AGENTS.md `### Development` block missing `corepack enable pnpm`:\n{block}"
    )
    assert "pnpm run setup" in block, (
        f"AGENTS.md `### Development` block missing `pnpm run setup`:\n{block}"
    )

    # Bare `pnpm setup` (no `run`) must not appear as a top-level instruction
    # line in the block.
    for line in block.splitlines():
        stripped = line.strip()
        # First column up to the comment — strip trailing comment for the test.
        cmd = stripped.split("#", 1)[0].strip()
        assert cmd != "pnpm setup", (
            f"AGENTS.md still contains bare `pnpm setup` instruction: {line!r}"
        )


def test_docs_readme_install_block_uses_corepack_and_run_setup() -> None:
    """`docs/README.md` Install/Setup block must teach `corepack enable pnpm`
    before `pnpm run setup`. The bare `pnpm setup` recommendation must
    be removed.
    """
    text = (REPO / "docs/README.md").read_text()

    assert "corepack enable pnpm" in text, (
        "docs/README.md must contain `corepack enable pnpm`."
    )
    assert "pnpm run setup" in text, (
        "docs/README.md must contain `pnpm run setup`."
    )

    # corepack must come before `pnpm run setup` (order matters — corepack
    # enables the right pnpm version BEFORE setup is invoked).
    cp = text.find("corepack enable pnpm")
    rs = text.find("pnpm run setup")
    assert cp != -1 and rs != -1
    assert cp < rs, (
        "In docs/README.md, `corepack enable pnpm` must appear before "
        "`pnpm run setup`."
    )

    # The bare `pnpm setup` (alone on a line, no `run`) must not appear
    # as a setup recommendation.
    bare_lines = [
        ln for ln in text.splitlines()
        if ln.strip() == "pnpm setup"
    ]
    assert not bare_lines, (
        f"docs/README.md still recommends bare `pnpm setup`: {bare_lines}"
    )


def test_e2e_readme_prereqs_mentions_corepack() -> None:
    """`e2e/README.md` Prerequisites section must explain that pnpm is managed
    via corepack — not list pnpm as a separate prerequisite to install.
    """
    text = (REPO / "e2e/README.md").read_text()

    assert "corepack" in text.lower(), (
        "e2e/README.md must mention corepack in its prerequisites."
    )

    # The old prerequisite line must be gone.
    assert "- Node.js and pnpm installed" not in text, (
        "e2e/README.md still lists `Node.js and pnpm installed` — should be "
        "replaced with a corepack-aware prerequisite."
    )


# ---------------------------------------------------------------------------
# pass_to_pass — the JS guard script must remain functional regardless.
# ---------------------------------------------------------------------------

def test_enforce_package_manager_exits_zero_for_pnpm_ua() -> None:
    """When invoked under a pnpm user-agent the guard script must exit 0,
    just like before the patch. Pre-existing repo behavior.
    """
    script = REPO / ".github/scripts/enforce-package-manager.js"
    env = {**os.environ, "npm_config_user_agent": "pnpm/8.0.0 npm/? node/v20.0.0"}
    r = subprocess.run(
        ["node", str(script)],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Guard script must exit 0 for pnpm UA, got {r.returncode}.\n"
        f"stderr: {r.stderr}"
    )


def test_codex_environment_toml_parses() -> None:
    """The Codex environment file must remain valid TOML. Pre-existing repo
    invariant — protects against agents writing malformed TOML.
    """
    toml_path = REPO / ".codex/environments/environment.toml"
    with toml_path.open("rb") as f:
        data = tomllib.load(f)
    assert data.get("name") == "Ghost"
    assert "setup" in data and "script" in data["setup"]
