"""
Task: openclaw-zsh-compdef-defer
Repo: openclaw/openclaw @ f32f7d0809b088e719ec2f5fcd81cb5fd087c5bb
PR:   56555

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = Path(REPO) / "src" / "cli" / "completion-cli.ts"


def _get_zsh_template_tail():
    """Extract the tail of the zsh template after generateZshSubcommands.

    This is the section where compdef registration logic lives.
    On the base commit it contains a bare `compdef` call.
    On the fix it contains the deferred registration pattern.
    """
    src = TARGET.read_text()
    match = re.search(
        r"\$\{generateZshSubcommands\([^)]+\)\}\s*\n(.*?)`;\s*\n\s*return",
        src,
        re.DOTALL,
    )
    assert match, "Could not locate zsh template tail in completion-cli.ts"
    return match.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_typescript_file_valid():
    """completion-cli.ts must exist and contain the completion generation logic."""
    src = TARGET.read_text()
    assert "getCompletionScript" in src, "getCompletionScript function not found"
    assert len(src) > 200, "File appears truncated or corrupted"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_compdef_not_bare_at_toplevel():
    """compdef must not be called bare at the top level of the zsh script.

    The base commit has `compdef _X_root_completion X` as a bare top-level
    statement. The fix must wrap it inside a function.
    """
    section = _get_zsh_template_tail()
    # A bare compdef is one at column 0 (no leading whitespace = top-level)
    for line in section.splitlines():
        assert not re.match(r"^compdef\s+", line), (
            f"Found bare top-level compdef call: {line.strip()!r}\n"
            "compdef must be inside a registration function"
        )
    # compdef must still exist somewhere (not just deleted)
    assert "compdef" in section, "compdef call was removed entirely instead of deferred"


# [pr_diff] fail_to_pass
def test_compdef_availability_check():
    """The registration logic must check whether compdef is available before calling it.

    Valid approaches: $+functions[compdef], whence, type, command -v.
    """
    section = _get_zsh_template_tail()
    checks = [
        "$+functions[compdef]",
        "whence compdef",
        "whence -w compdef",
        "type compdef",
        "command -v compdef",
    ]
    assert any(c in section for c in checks), (
        "No compdef availability check found — must verify compdef exists before calling.\n"
        f"Accepted patterns: {checks}"
    )


# [pr_diff] fail_to_pass
def test_precmd_hook_queues_deferred_registration():
    """When compdef is not yet available, registration must be deferred via precmd_functions.

    The registration function should be added to precmd_functions so it runs
    on the first prompt after compinit has been called.
    """
    section = _get_zsh_template_tail()
    assert "precmd_functions" in section, (
        "precmd_functions not referenced — must queue deferred registration"
    )
    # Verify something is actually added to the array
    add_patterns = ["precmd_functions+=(", "precmd_functions=("]
    assert any(p in section for p in add_patterns), (
        "precmd_functions is mentioned but nothing is appended to it"
    )


# [pr_diff] fail_to_pass
def test_cleanup_after_successful_registration():
    """After compdef succeeds, the hook must clean up after itself.

    This means removing the entry from precmd_functions and/or undefining
    the registration function so it does not run on every prompt forever.
    """
    section = _get_zsh_template_tail()
    cleanup_patterns = [
        "precmd_functions:#",      # zsh array element removal
        "unfunction",              # undefine function
        "unset -f",                # alternative undefine
    ]
    assert any(p in section for p in cleanup_patterns), (
        "No cleanup after registration — must remove hook from precmd_functions "
        "and/or undefine the registration function"
    )


# [pr_diff] fail_to_pass
def test_dedup_prevents_duplicate_hooks():
    """Repeated sourcing must not add duplicate entries to precmd_functions.

    The code must check membership before appending.
    """
    section = _get_zsh_template_tail()
    dedup_patterns = [
        "precmd_functions[(r)",    # zsh reverse subscript search
        "typeset -gaU",            # unique array flag
    ]
    assert any(p in section for p in dedup_patterns), (
        "No deduplication check — repeated sourcing could add duplicate precmd hooks"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_zsh_completion_function_intact():
    """The root completion function must still be defined (not removed by the fix)."""
    src = TARGET.read_text()
    assert "_root_completion" in src, "Root completion function definition was removed"
    # Anti-stub: the completion function should have real content
    assert "case" in src or "compadd" in src or "_arguments" in src, (
        "Completion function appears to be a stub — no case/compadd/_arguments found"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:104 @ f32f7d0809b088e719ec2f5fcd81cb5fd087c5bb
def test_no_ts_nocheck():
    """No @ts-nocheck or @ts-ignore in CLI source files (CLAUDE.md rule)."""
    cli_dir = Path(REPO) / "src" / "cli"
    if not cli_dir.exists():
        return
    violations = []
    for ts_file in cli_dir.glob("*.ts"):
        if ts_file.name.endswith((".test.ts", ".d.ts")):
            continue
        content = ts_file.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if "@ts-nocheck" in line or "@ts-ignore" in line:
                violations.append(f"{ts_file.name}:{i}: {line.strip()}")
    assert not violations, (
        "Found @ts-nocheck/@ts-ignore:\n" + "\n".join(violations)
    )
