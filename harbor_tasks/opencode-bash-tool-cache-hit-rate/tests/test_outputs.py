"""
Task: opencode-bash-tool-cache-hit-rate
Repo: anomalyco/opencode @ 48326e8d9ca5648b6ab1ee15f0374434be56c4d4
PR:   #19487

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"
BASH_TXT = Path(REPO) / "packages/opencode/src/tool/bash.txt"
BASH_TS = Path(REPO) / "packages/opencode/src/tool/bash.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """bash.ts and bash.txt must exist and be non-empty; bash.ts must parse."""
    assert BASH_TXT.exists() and BASH_TXT.stat().st_size > 0, "bash.txt missing or empty"
    assert BASH_TS.exists() and BASH_TS.stat().st_size > 0, "bash.ts missing or empty"
    r = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{BASH_TS}', 'utf8')"],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, f"bash.ts is not readable: {r.stderr.decode()}"


# [static] pass_to_pass
def test_not_stub():
    """bash.txt must be a substantial tool description (20+ lines, 100+ words)."""
    content = BASH_TXT.read_text()
    lines = content.strip().splitlines()
    words = content.split()
    assert len(lines) >= 20, f"bash.txt only has {len(lines)} lines, need 20+"
    assert len(words) >= 100, f"bash.txt only has {len(words)} words, need 100+"
    # Must mention several bash-tool concepts
    concepts = re.findall(
        r'command|output|execute|run|shell|timeout|workdir|truncat|parameter|exit',
        content, re.IGNORECASE,
    )
    unique = set(c.lower() for c in concepts)
    assert len(unique) >= 5, f"bash.txt mentions only {len(unique)} concepts, need 5+"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_directory_placeholder_in_template():
    """bash.txt must not contain ${directory} placeholder."""
    content = BASH_TXT.read_text()
    assert "${directory}" not in content, "bash.txt still contains ${directory} placeholder"


# [pr_diff] fail_to_pass
def test_template_static_after_substitutions():
    """After replacing maxLines/maxBytes, no ${...} placeholders should remain."""
    r = subprocess.run(
        ["node", "-e", f"""
        const fs = require('fs');
        const txt = fs.readFileSync('{BASH_TXT}', 'utf8');
        let result = txt.replaceAll('${{maxLines}}', '5000').replaceAll('${{maxBytes}}', '50000');
        const remaining = result.match(/\\$\\{{[^}}]+\\}}/g);
        if (remaining && remaining.length > 0) {{
            console.log('FAIL:' + remaining.join(','));
            process.exit(1);
        }}
        console.log('static');
        """],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, f"Template has dynamic placeholders: {r.stdout.decode().strip()}"


# [pr_diff] fail_to_pass
def test_ts_no_directory_injection():
    """bash.ts must not substitute directory into the tool description."""
    src = BASH_TS.read_text()
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if (".replace(" in line or ".replaceAll(" in line) and "directory" in line:
            # Exclude parameter .describe() calls
            if ".describe(" in line:
                continue
            raise AssertionError(
                f"bash.ts still substitutes directory into description: {line.strip()}"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_describes_directory_behavior():
    """bash.txt must still describe the default working directory behavior."""
    content = BASH_TXT.read_text()
    assert re.search(
        r'working.?directory|current.?directory|default.?directory|commands?.+run.+in',
        content, re.IGNORECASE,
    ), "bash.txt no longer describes default directory behavior"


# [pr_diff] pass_to_pass
def test_retains_global_placeholders():
    """bash.txt must still contain ${maxLines} and ${maxBytes} placeholders."""
    content = BASH_TXT.read_text()
    assert "${maxLines}" in content, "bash.txt missing ${maxLines} placeholder"
    assert "${maxBytes}" in content, "bash.txt missing ${maxBytes} placeholder"


# [pr_diff] pass_to_pass
def test_preserves_guidance_sections():
    """bash.txt must retain key guidance: quoting, tool preference, timeout/truncation."""
    content = BASH_TXT.read_text()
    sections = 0
    if re.search(r'quot(e|ing)|double.?quote', content, re.IGNORECASE):
        sections += 1
    if re.search(
        r'specialized.?tool|dedicated.?tool|instead.*(grep|cat|find)|DO NOT use.*(reading|writing|editing|searching)',
        content, re.IGNORECASE,
    ):
        sections += 1
    if re.search(r'timeout|time.?out|truncat', content, re.IGNORECASE):
        sections += 1
    assert sections >= 2, f"bash.txt missing key guidance ({sections}/3 sections found)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 48326e8d
def test_no_any_type():
    """bash.ts must not use the `any` type annotation."""
    src = BASH_TS.read_text()
    matches = re.findall(r':\s*any\b', src)
    assert len(matches) == 0, f"Found {len(matches)} `any` type annotations in bash.ts"


# [static] pass_to_pass
def test_bashtool_export_preserved():
    """BashTool must still be exported from bash.ts."""
    src = BASH_TS.read_text()
    assert "BashTool" in src, "BashTool export missing from bash.ts"
