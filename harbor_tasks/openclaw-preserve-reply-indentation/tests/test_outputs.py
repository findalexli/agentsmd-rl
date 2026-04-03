"""
Task: openclaw-preserve-reply-indentation
Repo: openclaw/openclaw @ 0d0d46f5e95f6f003861be33b4b9c6e3b493ea15
PR:   55960

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = Path(f"{REPO}/src/utils/directive-tags.ts")


def _call_parse(input_text: str) -> dict:
    """Call parseInlineDirectives(input_text) via a temp tsx file, return {text, hasReplyTag}."""
    # Use a temp file in REPO so tsx resolves './src/utils/directive-tags' correctly.
    # tsx -e (eval) does not reliably resolve relative imports in tsx 4.x.
    script = (
        "import { parseInlineDirectives } from './src/utils/directive-tags';\n"
        "const r = parseInlineDirectives(process.env['TEST_INPUT'] ?? '');\n"
        "process.stdout.write(JSON.stringify({ text: r.text, hasReplyTag: r.hasReplyTag }));\n"
    )
    tmp = Path(REPO) / "_pytest_helper.ts"
    tmp.write_text(script)
    try:
        env = {**os.environ, "TEST_INPUT": input_text}
        r = subprocess.run(
            ["tsx", str(tmp)],
            cwd=REPO, capture_output=True, text=True, timeout=60, env=env,
        )
    finally:
        tmp.unlink(missing_ok=True)
    assert r.returncode == 0, f"tsx failed:\n{r.stderr}"
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_indentation_preserved_plain_text():
    """Leading indentation on plain text after a reply tag must survive stripping."""
    # Case 1: 4-space indent after tag on same line
    r1 = _call_parse("[[reply_to_current]]    indented text")
    assert r1["hasReplyTag"] is True
    assert "    indented text" in r1["text"], f"4-space indent lost: {r1['text']!r}"

    # Case 2: multi-line with varying indentation
    r2 = _call_parse("[[reply_to_current]]  line one\n      line two\n  line three")
    assert "  line one" in r2["text"], f"2-space indent lost: {r2['text']!r}"
    assert "      line two" in r2["text"], f"6-space indent lost: {r2['text']!r}"
    assert "  line three" in r2["text"], f"Trailing 2-space indent lost: {r2['text']!r}"

    # Case 3: tag on its own line, content lines indented
    r3 = _call_parse("[[reply_to_current]]\n        deep indent")
    assert "        deep indent" in r3["text"], f"8-space indent lost: {r3['text']!r}"


# [pr_diff] fail_to_pass
def test_code_block_indentation_preserved():
    """Fenced code block indentation must survive reply-tag stripping."""
    # Case 1: Python code block
    py_input = "[[reply_to_current]]\n```python\n    if True:\n        print('ok')\n```"
    r1 = _call_parse(py_input)
    assert r1["hasReplyTag"] is True
    assert "    if True:" in r1["text"], f"Python indent collapsed: {r1['text']!r}"
    assert "        print('ok')" in r1["text"], f"Nested indent collapsed: {r1['text']!r}"

    # Case 2: JavaScript code block with different nesting
    js_input = (
        "[[reply_to_current]]\n```js\nfunction foo() {\n"
        "  const x = 1;\n  if (x) {\n    return x;\n  }\n}\n```"
    )
    r2 = _call_parse(js_input)
    assert "  const x = 1;" in r2["text"], f"JS 2-space indent lost: {r2['text']!r}"
    assert "    return x;" in r2["text"], f"JS 4-space indent lost: {r2['text']!r}"

    # Case 3: Tab-indented code block
    tab_input = "[[reply_to_current]]\n```\n\tline one\n\t\tline two\n```"
    r3 = _call_parse(tab_input)
    assert "\tline one" in r3["text"], f"Tab indent lost: {r3['text']!r}"
    assert "\t\tline two" in r3["text"], f"Double-tab indent lost: {r3['text']!r}"


# [pr_diff] fail_to_pass
def test_yaml_indentation_preserved():
    """YAML-style nested indentation must survive reply-tag stripping."""
    # Case 1: standard YAML config
    r1 = _call_parse(
        "[[reply_to_current]]\nconfig:\n  database:\n    host: localhost\n    port: 5432"
    )
    assert r1["hasReplyTag"] is True
    assert "  database:" in r1["text"], f"2-space indent lost: {r1['text']!r}"
    assert "    host: localhost" in r1["text"], f"4-space indent lost: {r1['text']!r}"

    # Case 2: deeper nesting
    r2 = _call_parse(
        "[[reply_to_current]]\ntop:\n  mid:\n    deep:\n      value: 42"
    )
    assert "    deep:" in r2["text"], f"4-space lost: {r2['text']!r}"
    assert "      value: 42" in r2["text"], f"6-space lost: {r2['text']!r}"

    # Case 3: list items with indent
    r3 = _call_parse(
        "[[reply_to_current]]\nlist:\n  - item1\n  - item2\n    sub: val"
    )
    assert "  - item1" in r3["text"], f"List indent lost: {r3['text']!r}"
    assert "    sub: val" in r3["text"], f"Sub-item indent lost: {r3['text']!r}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + structural checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_basic_reply_tag_detection():
    """parseInlineDirectives must still detect and strip reply tags."""
    # Case 1: basic reply_to_current
    r1 = _call_parse("[[reply_to_current]] hello world")
    assert r1["hasReplyTag"] is True
    assert "hello world" in r1["text"]
    assert "[[" not in r1["text"]

    # Case 2: reply_to with explicit id
    r2 = _call_parse("[[reply_to: msg-123]] greetings")
    assert r2["hasReplyTag"] is True
    assert "greetings" in r2["text"]
    assert "[[" not in r2["text"]

    # Case 3: no tags at all — must not false-positive
    r3 = _call_parse("just plain text")
    assert r3["hasReplyTag"] is False
    assert r3["text"] == "just plain text"


# [pr_diff] pass_to_pass
def test_word_boundary_space_insertion():
    """When a reply tag sits between two non-whitespace chars, a space is inserted."""
    # Case 1: tag between two words
    r1 = _call_parse("see[[reply_to_current]]now")
    assert r1["hasReplyTag"] is True
    assert "see now" in r1["text"], f"Missing boundary space: {r1['text']!r}"

    # Case 2: tag at start (no left neighbor) — no spurious leading space
    r2 = _call_parse("[[reply_to_current]]text")
    assert "text" in r2["text"]
    assert not r2["text"].startswith(" "), f"Spurious leading space: {r2['text']!r}"

    # Case 3: tag at end — no trailing content
    r3 = _call_parse("word[[reply_to_current]]")
    assert r3["text"].rstrip() == "word", f"Unexpected trailing content: {r3['text']!r}"


# [pr_diff] pass_to_pass
def test_leading_blank_lines_stripped():
    """Leading blank lines introduced by tag removal are stripped."""
    r1 = _call_parse("[[reply_to_current]]\n\ntext after blanks")
    assert r1["hasReplyTag"] is True
    assert r1["text"] == "text after blanks", f"Blank lines not stripped: {r1['text']!r}"

    r2 = _call_parse("[[reply_to_current]]\n\n\n\nmulti blank lines")
    assert r2["text"] == "multi blank lines", f"Multiple blanks not stripped: {r2['text']!r}"


# [static] pass_to_pass
def test_file_not_stub():
    """directive-tags.ts must have real logic, not be a stub."""
    src = TARGET.read_text()
    assert "export" in src, "No exports found"
    assert "parseInlineDirectives" in src, "parseInlineDirectives missing"
    assert "normalizeDirectiveWhitespace" in src, "normalizeDirectiveWhitespace missing"
    assert len(src.splitlines()) > 50, "File too short to contain real logic"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:104 @ 0d0d46f5e95f6f003861be33b4b9c6e3b493ea15
def test_no_ts_nocheck():
    """Modified files must not contain @ts-nocheck or @ts-ignore."""
    src = TARGET.read_text()
    assert "@ts-nocheck" not in src, "File contains @ts-nocheck"
    assert "@ts-ignore" not in src, "File contains @ts-ignore"


# [agent_config] pass_to_pass — AGENTS.md:104 @ 0d0d46f5e95f6f003861be33b4b9c6e3b493ea15
def test_no_inline_lint_suppression():
    """Modified files must not contain inline lint suppression comments."""
    src = TARGET.read_text()
    for line in src.splitlines():
        lower = line.lower()
        assert "eslint-disable" not in lower, f"Lint suppression found: {line.strip()}"
        assert "oxlint-ignore" not in lower, f"Lint suppression found: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:102 @ 0d0d46f5e95f6f003861be33b4b9c6e3b493ea15
def test_no_any_type():
    """Prefer strict typing; avoid `any` as a type annotation."""
    import re
    src = TARGET.read_text()
    # Strip comments and string literals for accurate matching
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.split("//")[0]  # remove single-line comments
        if re.search(r':\s*any\b', stripped) or re.search(r'\bas\s+any\b', stripped):
            assert False, f"Line {i}: `any` type found: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:111 @ 0d0d46f5e95f6f003861be33b4b9c6e3b493ea15
def test_no_prototype_mutation():
    """Never share class behavior via prototype mutation."""
    src = TARGET.read_text()
    assert ".prototype" not in src, "Prototype mutation found in directive-tags.ts"


# [agent_config] pass_to_pass — AGENTS.md:106 @ 0d0d46f5e95f6f003861be33b4b9c6e3b493ea15
def test_no_dynamic_import():
    """Production utility files must not use dynamic await import() — use static imports only."""
    import re
    src = TARGET.read_text()
    # Dynamic imports in a utility module would violate the guardrail against
    # mixing static and dynamic imports of the same module in production paths.
    matches = [
        (i + 1, line.strip())
        for i, line in enumerate(src.splitlines())
        if re.search(r'\bawait\s+import\s*\(', line)
    ]
    assert not matches, (
        f"Dynamic import(s) found in directive-tags.ts: "
        + ", ".join(f"line {ln}: {txt}" for ln, txt in matches)
    )
