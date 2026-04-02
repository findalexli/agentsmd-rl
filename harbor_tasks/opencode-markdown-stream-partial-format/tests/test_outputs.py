"""
Task: opencode-markdown-stream-partial-format
Repo: anomalyco/opencode @ 771525270a0c4d1394b3117e5842847a51caf72d
PR:   19403

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/opencode"
BASE_COMMIT = "771525270a0c4d1394b3117e5842847a51caf72d"


UI_PKG = f"{REPO}/packages/ui"


def _run_ts(code: str) -> str:
    """Run TypeScript code via bun inside packages/ui so deps resolve."""
    fd, path = tempfile.mkstemp(suffix=".ts", dir=UI_PKG)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run(
            ["bun", path],
            cwd=UI_PKG,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"bun failed:\n{r.stderr}\n{r.stdout}"
        return r.stdout.strip()
    finally:
        os.unlink(path)


def _stream_and_parse(markdown: str, live: bool) -> dict:
    """Call the stream function and parse the first block's HTML."""
    escaped = json.dumps(markdown)
    result = _run_ts(f'''
import {{ stream }} from "./src/components/markdown-stream"
import {{ marked }} from "marked"
const blocks = stream({escaped}, {str(live).lower()})
const allSrc = blocks.map(b => b.src).join("")
const html = await marked.parse(allSrc)
console.log(JSON.stringify({{
  html,
  blockCount: blocks.length,
  blocks: blocks.map(b => ({{ raw: b.raw, src: b.src, mode: b.mode }})),
}}))
''')
    return json.loads(result)


def _get_changed_lines() -> list[str]:
    """Return added lines in changed files under packages/ui/src/components/."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--", "packages/ui/src/components/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return [
        line[1:]  # strip leading +
        for line in r.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_syntax_check():
    """markdown.tsx must exist; markdown-stream.ts must be created by the fix."""
    tsx = Path(f"{REPO}/packages/ui/src/components/markdown.tsx")
    assert tsx.exists(), "markdown.tsx is missing"
    assert len(tsx.read_text()) > 100, "markdown.tsx appears truncated or empty"
    stream_ts = Path(f"{REPO}/packages/ui/src/components/markdown-stream.ts")
    assert stream_ts.exists(), "markdown-stream.ts not created — fix not applied"
    assert "export function stream" in stream_ts.read_text(), (
        "markdown-stream.ts does not export a `stream` function"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bold_emphasis_healed():
    """Unclosed ** markers are temporarily closed during streaming."""
    for text in ["hello **world", "some **bold text with spaces", "prefix **bold end"]:
        data = _stream_and_parse(text, live=True)
        assert "<strong>" in data["html"], (
            f"Bold emphasis not healed for: {text!r}\nHTML: {data['html']}"
        )


# [pr_diff] fail_to_pass
def test_backtick_code_healed():
    """Unclosed inline backtick is temporarily closed during streaming."""
    for text in ["say `code", "run `npm install", "use `bun test"]:
        data = _stream_and_parse(text, live=True)
        assert "<code>" in data["html"], (
            f"Backtick not healed for: {text!r}\nHTML: {data['html']}"
        )


# [pr_diff] fail_to_pass
def test_italic_emphasis_healed():
    """Unclosed * markers are temporarily closed during streaming."""
    for text in ["hello *italic", "this *is important", "prefix *styled word"]:
        data = _stream_and_parse(text, live=True)
        assert "<em>" in data["html"], (
            f"Italic emphasis not healed for: {text!r}\nHTML: {data['html']}"
        )


# [pr_diff] fail_to_pass
def test_underscore_bold_healed():
    """Unclosed __ markers are temporarily closed during streaming."""
    for text in ["hello __underline bold", "prefix __strong words", "start __end"]:
        data = _stream_and_parse(text, live=True)
        assert "<strong>" in data["html"], (
            f"Underscore bold not healed for: {text!r}\nHTML: {data['html']}"
        )


# [pr_diff] fail_to_pass
def test_incomplete_link_plain_text():
    """Partially streamed links render as plain text, not clickable markup."""
    for text in [
        "see [docs](https://example.com/gu",
        "click [here](http://",
        "visit [link](https://x.co",
    ]:
        data = _stream_and_parse(text, live=True)
        assert "<a " not in data["html"], (
            f"Incomplete link should not produce <a> tag for: {text!r}\nHTML: {data['html']}"
        )


# [pr_diff] fail_to_pass
def test_non_streaming_skips_healing():
    """When live=false, incomplete markers are NOT healed."""
    data = _stream_and_parse("hello **world", live=False)
    assert "<strong>" not in data["html"], (
        "Non-streaming mode should not heal incomplete bold markers"
    )
    data2 = _stream_and_parse("say `code", live=False)
    assert "<code>" not in data2["html"], (
        "Non-streaming mode should not heal incomplete backtick"
    )


# [pr_diff] fail_to_pass
def test_code_fence_splitting():
    """Trailing open code fence is split into a separate block from stable content."""
    data = _stream_and_parse("before\n\n```ts\nconst x = 1", live=True)
    assert data["blockCount"] >= 2, (
        f"Expected >=2 blocks for open code fence, got {data['blockCount']}"
    )
    all_raw = "".join(b["raw"] for b in data["blocks"])
    assert "before" in all_raw, "Content before fence missing"
    assert "const x = 1" in all_raw, "Code fence content missing"
    assert any("```" in b["raw"] for b in data["blocks"]), "No block contains the fence"


# ---------------------------------------------------------------------------
# Pass-to-pass -- regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_non_streaming_preserves_content():
    """Complete markdown renders correctly via marked (regression guard)."""
    result = _run_ts('''
import { marked } from "marked"
const cases = [
  "hello **world** and `code`",
  "# heading\\n\\nparagraph",
  "[link](https://example.com)",
]
for (const md of cases) {
  const html = await marked.parse(md)
  console.log(html)
}
''')
    assert "<strong>" in result, "Bold should render in complete markdown"
    assert "<code>" in result, "Code should render in complete markdown"
    assert "<a " in result, "Link should render in complete markdown"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:13 @ 771525270a0c4d1394b3117e5842847a51caf72d
def test_no_any_type():
    """No use of the `any` type in agent-changed files (AGENTS.md:13)."""
    added = _get_changed_lines()
    for line in added:
        code = line.split("//")[0]  # ignore comments
        assert ": any" not in code and "<any>" not in code and "as any" not in code, (
            f"Found `any` type annotation in changed code: {line.strip()}"
        )


# [agent_config] pass_to_pass -- AGENTS.md:12 @ 771525270a0c4d1394b3117e5842847a51caf72d
def test_no_try_catch():
    """No try/catch blocks in agent-changed files (AGENTS.md:12)."""
    added = _get_changed_lines()
    for line in added:
        stripped = line.strip()
        code = stripped.split("//")[0]  # ignore comments
        assert "try {" not in code and "try{" not in code, (
            f"Found try/catch in changed code: {stripped}"
        )


# [agent_config] pass_to_pass -- AGENTS.md:84 @ 771525270a0c4d1394b3117e5842847a51caf72d
def test_no_else_statements():
    """No else statements in agent-changed files (AGENTS.md:84)."""
    added = _get_changed_lines()
    for line in added:
        stripped = line.strip()
        code = stripped.split("//")[0]
        assert "} else" not in code and "} else{" not in code, (
            f"Found else statement in changed code: {stripped}"
        )
