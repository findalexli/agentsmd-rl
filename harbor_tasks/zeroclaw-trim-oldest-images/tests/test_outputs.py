"""
Task: zeroclaw-trim-oldest-images
Repo: zeroclaw-labs/zeroclaw @ 3e02e68ec0e26b2c43593c40d660e2298c8cb332
PR:   4912

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The full crate does not compile at this commit (unrelated breakage in 16+ files).
We extract the pure functions under test into a standalone Rust binary and
verify behavior without cargo.
"""

import re
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = "/workspace/zeroclaw"
TARGET = Path(REPO) / "src" / "multimodal.rs"


# ---------------------------------------------------------------------------
# Helpers — extract Rust functions and build standalone test binary
# ---------------------------------------------------------------------------

def _extract_rust_fn(source: str, fn_name: str) -> str:
    """Extract a function from Rust source by brace-matching.

    Returns the full text from `fn name(` through the closing `}`, or empty
    string if the function is not found.
    """
    # Match pub/private fn
    pattern = rf"(?:pub\s+)?fn\s+{re.escape(fn_name)}\s*\("
    m = re.search(pattern, source)
    if not m:
        return ""
    start = m.start()
    # Walk forward to the opening brace
    idx = source.index("{", m.end())
    depth = 1
    idx += 1
    while depth > 0 and idx < len(source):
        ch = source[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        idx += 1
    return source[start:idx]


def _extract_const(source: str, name: str) -> str:
    """Extract a const declaration line."""
    for line in source.splitlines():
        if f"const {name}" in line:
            return line.strip()
    return ""


def _build_standalone_test(src: str) -> str:
    """Build and run a standalone Rust binary exercising trim_old_images.

    Returns the combined stdout+stderr of the test binary, or raises if
    the function cannot be extracted (i.e. not yet implemented).
    """
    parse_fn = _extract_rust_fn(src, "parse_image_markers")
    compose_fn = _extract_rust_fn(src, "compose_multimodal_message")
    trim_fn = _extract_rust_fn(src, "trim_old_images")
    marker_const = _extract_const(src, "IMAGE_MARKER_PREFIX")

    assert parse_fn, "parse_image_markers not found in source"
    assert compose_fn, "compose_multimodal_message not found in source"
    assert trim_fn, "trim_old_images not found in source"
    assert marker_const, "IMAGE_MARKER_PREFIX const not found"

    # Strip pub modifiers — standalone binary doesn't need them
    parse_fn = re.sub(r"^pub\s+", "", parse_fn)
    compose_fn = re.sub(r"^pub\s+", "", compose_fn)
    trim_fn = re.sub(r"^pub\s+", "", trim_fn)

    standalone = textwrap.dedent(f"""\
        use std::collections::HashSet;

        #[derive(Debug, Clone)]
        struct ChatMessage {{
            role: String,
            content: String,
        }}

        {marker_const}

        {parse_fn}

        {compose_fn}

        {trim_fn}

        // ---- test helpers ----

        fn img_content(text: &str, n: usize) -> String {{
            let uris: Vec<String> = (0..n)
                .map(|i| format!("data:image/png;base64,AAAA{{i}}"))
                .collect();
            compose_multimodal_message(text, &uris)
        }}

        fn user_msg(content: &str) -> ChatMessage {{
            ChatMessage {{ role: "user".to_string(), content: content.to_string() }}
        }}

        fn asst_msg(content: &str) -> ChatMessage {{
            ChatMessage {{ role: "assistant".to_string(), content: content.to_string() }}
        }}

        fn image_count(msgs: &[ChatMessage]) -> Vec<usize> {{
            msgs.iter().map(|m| parse_image_markers(&m.content).1.len()).collect()
        }}

        // ---- tests ----

        fn main() {{
            test_no_error_on_excess();
            test_trims_oldest_first();
            test_trims_oldest_first_varied();
            test_preserves_text_content();
            test_preserves_text_varied();
            test_placeholder_for_image_only();
            test_skips_assistant_messages();
            test_noop_when_within_limit();
            test_noop_exactly_at_limit();
            test_single_message_over_limit();
            println!("ALL_TESTS_PASSED");
        }}

        fn test_no_error_on_excess() {{
            let msgs = vec![
                user_msg(&img_content("a", 3)),
                user_msg(&img_content("b", 3)),
            ];
            let result = trim_old_images(&msgs, 2);
            let total: usize = image_count(&result).iter().sum();
            assert!(total <= 2, "expected <= 2 images after trim, got {{total}}");
            println!("PASS: no_error_on_excess");
        }}

        fn test_trims_oldest_first() {{
            let msgs = vec![
                user_msg(&img_content("oldest", 2)),
                user_msg(&img_content("middle", 2)),
                user_msg(&img_content("newest", 2)),
            ];
            let result = trim_old_images(&msgs, 3);
            let counts = image_count(&result);
            assert_eq!(counts[0], 0, "oldest must lose all images");
            assert_eq!(counts[2], 2, "newest must keep images");
            println!("PASS: trims_oldest_first");
        }}

        fn test_trims_oldest_first_varied() {{
            let msgs = vec![
                user_msg(&img_content("m0", 3)),
                user_msg(&img_content("m1", 1)),
                user_msg(&img_content("m2", 2)),
                user_msg(&img_content("m3", 2)),
            ];
            // total=8, max=4: drop m0 (3), drop m1 (1) = 4 dropped
            let result = trim_old_images(&msgs, 4);
            let counts = image_count(&result);
            assert_eq!(counts[0], 0, "m0 must be stripped");
            assert_eq!(counts[1], 0, "m1 must be stripped");
            assert_eq!(counts[2], 2, "m2 must keep images");
            assert_eq!(counts[3], 2, "m3 must keep images");
            println!("PASS: trims_oldest_first_varied");
        }}

        fn test_preserves_text_content() {{
            let msgs = vec![
                user_msg(&img_content("important payload", 2)),
                user_msg(&img_content("keep me", 1)),
            ];
            let result = trim_old_images(&msgs, 1);
            assert!(
                result[0].content.contains("important payload"),
                "text must survive trimming, got: {{:?}}",
                result[0].content
            );
            println!("PASS: preserves_text_content");
        }}

        fn test_preserves_text_varied() {{
            let msgs = vec![
                user_msg(&img_content("short", 1)),
                user_msg(&img_content("a longer description of the user request", 1)),
                user_msg(&img_content("final", 1)),
            ];
            let result = trim_old_images(&msgs, 1);
            assert!(result[0].content.contains("short"), "short text lost");
            assert!(
                result[1].content.contains("a longer description"),
                "long text lost"
            );
            println!("PASS: preserves_text_varied");
        }}

        fn test_placeholder_for_image_only() {{
            let msgs = vec![
                user_msg(&img_content("", 2)),
                user_msg(&img_content("text", 1)),
            ];
            let result = trim_old_images(&msgs, 1);
            assert!(
                result[0].content.to_lowercase().contains("image removed"),
                "image-only message needs placeholder, got: {{:?}}",
                result[0].content
            );
            println!("PASS: placeholder_for_image_only");
        }}

        fn test_skips_assistant_messages() {{
            let ac = img_content("assistant img", 2);
            let msgs = vec![
                asst_msg(&ac),
                user_msg(&img_content("u1", 2)),
                user_msg(&img_content("u2", 2)),
            ];
            let result = trim_old_images(&msgs, 2);
            assert_eq!(
                result[0].content, ac,
                "assistant messages must be untouched"
            );
            println!("PASS: skips_assistant_messages");
        }}

        fn test_noop_when_within_limit() {{
            let msgs = vec![
                user_msg(&img_content("a", 1)),
                user_msg(&img_content("b", 1)),
            ];
            let result = trim_old_images(&msgs, 10);
            let total: usize = image_count(&result).iter().sum();
            assert_eq!(total, 2, "no images should be removed when under limit");
            println!("PASS: noop_when_within_limit");
        }}

        fn test_noop_exactly_at_limit() {{
            let msgs = vec![
                user_msg(&img_content("x", 2)),
                user_msg(&img_content("y", 3)),
            ];
            let result = trim_old_images(&msgs, 5);
            let total: usize = image_count(&result).iter().sum();
            assert_eq!(total, 5, "no trim when exactly at limit");
            println!("PASS: noop_exactly_at_limit");
        }}

        fn test_single_message_over_limit() {{
            let msgs = vec![
                user_msg(&img_content("solo", 5)),
            ];
            let result = trim_old_images(&msgs, 2);
            let total: usize = image_count(&result).iter().sum();
            assert!(total <= 2, "single message must be trimmed too, got {{total}}");
            println!("PASS: single_message_over_limit");
        }}
    """)

    test_rs = Path("/tmp/harbor_trim_test.rs")
    test_rs.write_text(standalone)

    # Compile
    r = subprocess.run(
        ["rustc", "--edition", "2021", "-o", "/tmp/harbor_trim_test", str(test_rs)],
        capture_output=True,
        timeout=30,
    )
    if r.returncode != 0:
        return f"COMPILE_FAILED\n{r.stderr.decode(errors='replace')}"

    # Run
    r = subprocess.run(
        ["/tmp/harbor_trim_test"],
        capture_output=True,
        timeout=10,
    )
    return r.stdout.decode(errors="replace") + "\n" + r.stderr.decode(errors="replace")


# ---------------------------------------------------------------------------
# Module-scoped fixture: build once, share across all behavioral tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rust_behavioral():
    """Extract pure functions from multimodal.rs, compile standalone, run tests."""
    src = TARGET.read_text()
    return _build_standalone_test(src)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """multimodal.rs must be parseable Rust (syntax check via rustfmt)."""
    # Full crate has pre-existing breakage in unrelated files; check only multimodal.rs
    r = subprocess.run(
        ["rustfmt", "--check", str(TARGET)],
        capture_output=True,
        timeout=30,
    )
    # rustfmt --check returns 0 if formatted, 1 if not — we accept both
    # (we only care it parses). returncode == 2 means parse error.
    assert r.returncode != 2, (
        f"multimodal.rs has syntax errors:\n"
        f"{r.stderr.decode(errors='replace')[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via standalone Rust binary
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_hard_error_on_excess_images(rust_behavioral):
    """Must not return TooManyImages error — trims oldest images instead."""
    output = rust_behavioral
    assert "COMPILE_FAILED" not in output, (
        f"Standalone test failed to compile (trim_old_images may not exist):\n"
        f"{output[-2000:]}"
    )
    assert "PASS: no_error_on_excess" in output, (
        f"Excess images should be trimmed, not rejected:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_trim_targets_oldest_user_messages(rust_behavioral):
    """Trim removes images from oldest user messages first, skips assistant messages."""
    output = rust_behavioral
    assert "COMPILE_FAILED" not in output, f"Compile failed:\n{output[-2000:]}"
    assert "PASS: trims_oldest_first" in output, (
        f"Must remove images from oldest messages first:\n{output[-2000:]}"
    )
    assert "PASS: trims_oldest_first_varied" in output, (
        f"Must remove images from oldest messages first (varied):\n{output[-2000:]}"
    )
    assert "PASS: skips_assistant_messages" in output, (
        f"Must not modify assistant messages:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_preserves_text_with_placeholder(rust_behavioral):
    """Trimmed messages keep text; image-only messages get placeholder."""
    output = rust_behavioral
    assert "COMPILE_FAILED" not in output, f"Compile failed:\n{output[-2000:]}"
    assert "PASS: preserves_text_content" in output, (
        f"Text must survive trimming:\n{output[-2000:]}"
    )
    assert "PASS: preserves_text_varied" in output, (
        f"Varied text must survive trimming:\n{output[-2000:]}"
    )
    assert "PASS: placeholder_for_image_only" in output, (
        f"Image-only messages need placeholder:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_trim_within_limit_noop(rust_behavioral):
    """When under the limit, no images should be removed."""
    output = rust_behavioral
    assert "COMPILE_FAILED" not in output, f"Compile failed:\n{output[-2000:]}"
    assert "PASS: noop_when_within_limit" in output, (
        f"Should not trim when under limit:\n{output[-2000:]}"
    )
    assert "PASS: noop_exactly_at_limit" in output, (
        f"Should not trim when exactly at limit:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_single_message_trim(rust_behavioral):
    """A single user message exceeding the limit must still be handled."""
    output = rust_behavioral
    assert "COMPILE_FAILED" not in output, f"Compile failed:\n{output[-2000:]}"
    assert "PASS: single_message_over_limit" in output, (
        f"Single message with excess images must be trimmed:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_prepare_messages_not_stub():
    """prepare_messages_for_provider has real logic, not a stub."""
    src = TARGET.read_text()
    # AST-only because: Rust crate cannot compile at this commit due to unrelated breakage
    assert "fn prepare_messages_for_provider" in src, (
        "prepare_messages_for_provider function not found"
    )
    fn_start = src.index("fn prepare_messages_for_provider")
    fn_region = src[fn_start:fn_start + 2000]
    required = ["max_images", "ChatMessage", "PreparedMessages"]
    found = [kw for kw in required if kw in fn_region]
    assert len(found) >= 2, (
        f"prepare_messages_for_provider looks like a stub — "
        f"only found {found} of {required}"
    )
