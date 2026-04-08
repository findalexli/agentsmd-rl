"""
Task: openclaw-zsh-compdef-defer
Repo: openclaw/openclaw @ f32f7d0809b088e719ec2f5fcd81cb5fd087c5bb
PR:   56555

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = Path(REPO) / "src" / "cli" / "completion-cli.ts"

# Node.js script: extract the zsh completion registration section from TypeScript source.
# Reads the template string, substitutes ${rootCmd} -> openclaw, outputs the tail.
_EXTRACT_TAIL_JS = r"""
const fs = require('fs');
const src = fs.readFileSync('src/cli/completion-cli.ts', 'utf8');
const m = src.match(/const script = `\n([\s\S]*?)`;\s*\n\s*return script;/);
if (!m) { console.error('NO_TEMPLATE'); process.exit(1); }
let t = m[1].replace(/\$\{rootCmd\}/g, 'openclaw');
const lines = t.split('\n');
// Find the registration section: first line with register_completion or bare compdef
let start = -1;
for (let i = 0; i < lines.length; i++) {
  if (lines[i].includes('_openclaw_register_completion') ||
      /^\s*compdef\s+/.test(lines[i])) {
    start = i;
    break;
  }
}
if (start === -1) {
  // Fallback: any compdef not in a #compdef directive
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('compdef') && !lines[i].includes('#compdef')) {
      start = i;
      break;
    }
  }
}
if (start === -1) { console.error('NO_REGISTRATION'); process.exit(1); }
console.log(lines.slice(start).join('\n'));
"""


def _get_zsh_tail() -> str:
    """Execute Node.js to extract the zsh completion registration section."""
    r = subprocess.run(
        ["node", "-e", _EXTRACT_TAIL_JS],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js extraction failed: {r.stderr}"
    return r.stdout


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_typescript_file_valid():
    """completion-cli.ts exists and contains completion generation logic."""
    assert TARGET.exists(), f"{TARGET} not found"
    src = TARGET.read_text()
    assert "getCompletionScript" in src, "getCompletionScript function not found"
    assert len(src) > 200, "File appears truncated"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using Node.js subprocess execution
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_compdef_not_bare_at_toplevel():
    """compdef must be called inside a registration function, not bare at top level.

    Executes Node.js to extract the generated zsh script and verify compdef is
    wrapped inside a function, not a bare top-level call.
    """
    section = _get_zsh_tail()
    for line in section.splitlines():
        assert not re.match(r"^compdef\s+", line), (
            f"Found bare top-level compdef: {line.strip()!r}\n"
            "compdef must be inside a registration function"
        )
    assert "compdef" in section, "compdef call was removed entirely"


# [pr_diff] fail_to_pass
def test_compdef_availability_check():
    """Registration logic checks whether compdef is available before calling it.

    Executes Node.js to extract the generated script and verify it contains
    a compdef availability check (e.g. $+functions[compdef]).
    """
    section = _get_zsh_tail()
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
    """When compdef is unavailable, registration is deferred via precmd_functions.

    Executes Node.js to extract the generated script and verify precmd_functions
    is used to queue the registration for retry after compinit.
    """
    section = _get_zsh_tail()
    assert "precmd_functions" in section, (
        "precmd_functions not referenced — must queue deferred registration"
    )
    assert any(p in section for p in ["precmd_functions+=(", "precmd_functions+=("]), (
        "precmd_functions is mentioned but nothing is appended to it"
    )


# [pr_diff] fail_to_pass
def test_cleanup_after_successful_registration():
    """After compdef succeeds, hook removes itself from precmd_functions and undefines.

    Executes Node.js to extract the generated script and verify cleanup patterns
    (array removal and/or function undefinition).
    """
    section = _get_zsh_tail()
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
    """Repeated sourcing does not add duplicate entries to precmd_functions.

    Executes Node.js to extract the generated script and verify deduplication
    (membership check before appending to precmd_functions).
    """
    section = _get_zsh_tail()
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
    """Root completion function still defined and not a stub."""
    src = TARGET.read_text()
    assert "_root_completion" in src, "Root completion function definition was removed"
    assert "case" in src or "compadd" in src or "_arguments" in src, (
        "Completion function appears to be a stub — no case/compadd/_arguments found"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:102 @ f32f7d0809b088e719ec2f5fcd81cb5fd087c5bb
def test_no_explicit_any():
    """No explicit 'any' type annotations or type assertions in completion-cli.ts (CLAUDE.md rule).

    Checks for ': any' (type annotation) and 'as any' (type assertion) patterns
    in TypeScript code. Template string content (the zsh script) is excluded.
    """
    src = TARGET.read_text()
    violations = []
    in_template = False
    for i, line in enumerate(src.splitlines(), 1):
        backtick_count = line.count("`")
        if backtick_count % 2 == 1:
            in_template = not in_template
        if not in_template:
            if re.search(r":\s*any\b", line) or re.search(r"\bas\s+any\b", line):
                violations.append(f"completion-cli.ts:{i}: {line.strip()}")
    assert not violations, (
        "Found explicit 'any' types (CLAUDE.md: prefer strict typing; avoid any):\n"
        + "\n".join(violations)
    )


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
