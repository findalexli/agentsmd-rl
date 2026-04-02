"""
Task: opencode-markdown-streaming-jank
Repo: anomalyco/opencode @ 311ba4179a3c112a7e0cbbeae152a971284a3632

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
BASE_COMMIT = "311ba4179a3c112a7e0cbbeae152a971284a3632"
TIMELINE = f"{REPO}/packages/app/src/pages/session/message-timeline.tsx"
MARKDOWN = f"{REPO}/packages/ui/src/components/markdown.tsx"
MSGPART = f"{REPO}/packages/ui/src/components/message-part.tsx"

# Files modified by this fix
MODIFIED_FILES = [
    "packages/ui/src/components/markdown.tsx",
    "packages/ui/src/components/message-part.tsx",
    "packages/app/src/pages/session/message-timeline.tsx",
    "packages/app/src/app.tsx",
]


def _added_lines() -> list[str]:
    """Return added lines ('+' prefix stripped) from git diff against base commit."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--"] + MODIFIED_FILES,
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    return [
        l[1:]
        for l in r.stdout.splitlines()
        if l.startswith("+") and not l.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_files_exist():
    """All modified target files must exist and be non-empty."""
    for path in [TIMELINE, MARKDOWN, MSGPART]:
        p = Path(path)
        assert p.exists(), f"{path} does not exist"
        assert p.stat().st_size > 0, f"{path} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------
# Structural regex checks used below because these are SolidJS .tsx components
# that require a full browser DOM + SolidJS runtime to render/call.

# [pr_diff] fail_to_pass
def test_css_containment_conditional():
    """content-visibility must be conditional on active/streaming state, not unconditional."""
    src = Path(TIMELINE).read_text()
    lines = src.splitlines()

    cv_indices = [
        i for i, l in enumerate(lines)
        if "content-visibility" in l.lower() or "contentvisibility" in l.lower()
    ]

    if not cv_indices:
        return  # Removed entirely — valid fix (no containment = no jank)

    # Every occurrence must be inside a conditional expression
    conditional = re.compile(
        r"(active\s*\(\)|streaming\s*\(\)|isActive|isStreaming"
        r"|\?\s*undefined|\?\s*[\"'`]auto[\"'`]|&&\s*[\"'`]auto[\"'`])",
        re.I,
    )
    for idx in cv_indices:
        window = "\n".join(lines[max(0, idx - 3) : idx + 4])
        if conditional.search(window):
            return

    assert False, (
        "content-visibility appears unconditional — must be gated on active/streaming state"
    )


# [pr_diff] fail_to_pass
def test_contain_intrinsic_conditional():
    """contain-intrinsic-size must be conditional on active/streaming state or removed."""
    src = Path(TIMELINE).read_text()
    lines = src.splitlines()

    cis_indices = [
        i for i, l in enumerate(lines)
        if "contain-intrinsic-size" in l.lower() or "containintrinsicsize" in l.lower()
    ]

    if not cis_indices:
        return  # Removed entirely — valid fix

    conditional = re.compile(
        r"(active\s*\(\)|streaming\s*\(\)|isActive|isStreaming"
        r"|\?\s*undefined|\?\s*[\"'`]auto|&&\s*[\"'`]auto)",
        re.I,
    )
    for idx in cis_indices:
        window = "\n".join(lines[max(0, idx - 3) : idx + 4])
        if conditional.search(window):
            return

    assert False, (
        "contain-intrinsic-size appears unconditional — must be gated on active/streaming state"
    )


# [pr_diff] fail_to_pass
def test_markdown_streaming_prop():
    """Markdown component must accept a streaming-related prop or context."""
    # Structural check: SolidJS component needs full runtime + DOM to call
    src = Path(MARKDOWN).read_text()

    has_prop = bool(re.search(r"streaming\s*[\?:]", src))
    has_context = bool(
        re.search(r"(useContext|createContext|Provider).*streaming", src, re.I | re.S)
    )
    has_param = bool(re.search(r"(isStreaming|live|mode)\s*[\?:].*(?:boolean|string)", src))

    assert has_prop or has_context or has_param, (
        "Markdown component has no streaming awareness (no streaming prop/signal/context)"
    )


# [pr_diff] fail_to_pass
def test_streaming_state_propagated():
    """message-part.tsx must compute streaming state and pass it to Markdown."""
    src = Path(MSGPART).read_text()

    # Must compute streaming state (checking completed time, role, active flag)
    computes = bool(re.search(r"(streaming|isStreaming)\s*=\s*(createMemo|createSignal|\()", src))
    if not computes:
        computes = bool(re.search(r"\.time\.completed|isActive\b|\.completed\s*[!=]", src))
    assert computes, "No streaming state computation in message-part.tsx"

    # Must pass streaming to Markdown (as prop or via context/provider)
    passes = bool(re.search(r"<Markdown[^>]*(streaming|active|live)\s*[={]", src))
    if not passes:
        passes = bool(re.search(r"(Provider|Context|Store).*streaming", src, re.I | re.S))
    assert passes, "Streaming state not passed to Markdown component"


# [pr_diff] fail_to_pass
def test_fence_detection():
    """markdown.tsx must detect incomplete/unclosed code fences during streaming."""
    src = Path(MARKDOWN).read_text()
    code_lines = [l for l in src.splitlines() if l.strip() and not l.strip().startswith("//")]
    code = "\n".join(code_lines)

    # Must have a dedicated function/variable for detecting incomplete fences
    has_fn = bool(
        re.search(r"(incomplete|unclosed|openFence|fenceOpen|pendingFence)\s*[\(=:]", code)
    )
    # Or a regex/string match specifically testing for triple-backtick/tilde fences
    if not has_fn:
        has_fn = bool(
            re.search(r"(match|test|exec|search)\s*\(.*(`\{3|```|~\{3|~~~)", code)
        )
    # Or explicit backtick counting logic
    if not has_fn:
        has_fn = bool(
            re.search(r"(backtick|fence|tilde).*count|count.*(backtick|fence|tilde)", code, re.I)
        )

    assert has_fn, "No dedicated code fence detection logic found in markdown.tsx"


# [pr_diff] fail_to_pass
def test_block_splitting():
    """Markdown must split streaming content into stable completed blocks + in-progress tail."""
    src = Path(MARKDOWN).read_text()
    code_lines = [l for l in src.splitlines() if l.strip() and not l.strip().startswith("//")]
    code = "\n".join(code_lines)

    # Must have block/segment splitting logic
    has_splitting = bool(
        re.search(r"(blocks|segments|parts|chunks|sections)\s*[.(\[=]", code)
    )
    # Or slicing/splitting an array of tokens
    if not has_splitting:
        has_splitting = bool(
            re.search(r"(\.slice\s*\(|\.split\s*\().*(?:token|block|fence)", code, re.I)
        )
    # Or map over lexed tokens
    if not has_splitting:
        has_splitting = bool(re.search(r"lexer|tokenize|tokens\s*[.(\[]", code))

    assert has_splitting, (
        "No block splitting logic found — streaming content should be split "
        "into stable + in-progress parts"
    )

    # Must iterate/process blocks individually (map, forEach, Promise.all, join)
    has_per_block = bool(re.search(r"(\.map\s*\(|forEach|\.join\(|Promise\.all)", code))
    assert has_per_block, "No per-block processing found (expected map/join/Promise.all)"


# ---------------------------------------------------------------------------
# Anti-stub (pr_diff) — reject trivial implementations
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_markdown_not_stub():
    """markdown.tsx must have substantial streaming logic, not just a prop declaration."""
    src = Path(MARKDOWN).read_text()
    lines = [
        l for l in src.splitlines()
        if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")
    ]

    # Base file has ~165 code lines. A real fix adds 30+ lines of streaming logic.
    assert len(lines) >= 185, f"Only {len(lines)} code lines — likely stub (need >=185)"

    # Must have at least 3 of these implementation signals
    code = "\n".join(lines)
    signals = 0

    if re.search(r"(blocks|segments|parts|chunks)\s*[.(\[=]", code):
        signals += 1
    if re.search(r"(cache|memo|previous|latest|prior)\b", code, re.I):
        signals += 1
    if re.search(r"(incomplete|unclosed|openFence|fence)", code):
        signals += 1
    if re.search(r"streaming", code):
        signals += 1
    if re.search(r"(\.map\s*\(|Promise\.all|\.join\()", code):
        signals += 1

    assert signals >= 3, f"Likely stub ({signals}/3 minimum implementation signals)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 311ba4179a3c112a7e0cbbeae152a971284a3632
def test_no_any_type_in_diff():
    """Agent config: avoid using the `any` type (AGENTS.md:13)."""
    added = _added_lines()
    violations = [
        l.strip()
        for l in added
        if re.search(r":\s*any\b|as\s+any\b|<any>", l)
        and not l.strip().startswith("//")
        and not l.strip().startswith("*")
    ]
    assert not violations, f"Added lines use `any` type (AGENTS.md:13): {violations[:5]}"


# [agent_config] pass_to_pass — AGENTS.md:70 @ 311ba4179a3c112a7e0cbbeae152a971284a3632
def test_const_over_let_in_diff():
    """Agent config: prefer const over let (AGENTS.md:70)."""
    added = _added_lines()
    let_lines = [
        l.strip()
        for l in added
        if re.search(r"^\s*let\s+\w", l)
        and not l.strip().startswith("//")
    ]
    assert not let_lines, f"Added lines use `let` (prefer const, AGENTS.md:70): {let_lines[:5]}"
