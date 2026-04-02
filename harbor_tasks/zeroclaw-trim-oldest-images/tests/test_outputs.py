"""
Task: zeroclaw-trim-oldest-images
Repo: zeroclaw-labs/zeroclaw @ 3e02e68ec0e26b2c43593c40d660e2298c8cb332
PR:   4912

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/zeroclaw"
TARGET = Path(REPO) / "src" / "multimodal.rs"


# ---------------------------------------------------------------------------
# Injected Rust tests — behaviorally verify trim_old_images by calling it
# with real inputs inside the module (only way to reach a private fn).
# ---------------------------------------------------------------------------

RUST_TEST_MODULE = r'''
#[cfg(test)]
mod harbor_bhv {
    // Explicit imports — `use super::*` only pulls pub items; private fns
    // and non-pub `use` imports (ChatMessage) require named imports.
    use crate::providers::ChatMessage;
    use super::{compose_multimodal_message, parse_image_markers, trim_old_images};

    fn img_content(text: &str, n: usize) -> String {
        let uris: Vec<String> = (0..n)
            .map(|i| format!("data:image/png;base64,AAAA{i}"))
            .collect();
        compose_multimodal_message(text, &uris)
    }

    fn user_msg(content: &str) -> ChatMessage {
        ChatMessage {
            role: "user".to_string(),
            content: content.to_string(),
        }
    }

    fn asst_msg(content: &str) -> ChatMessage {
        ChatMessage {
            role: "assistant".to_string(),
            content: content.to_string(),
        }
    }

    fn image_count(msgs: &[ChatMessage]) -> Vec<usize> {
        msgs.iter()
            .map(|m| parse_image_markers(&m.content).1.len())
            .collect()
    }

    #[test]
    fn no_error_on_excess() {
        // 6 images, max 2 → must trim, not error
        let msgs = vec![
            user_msg(&img_content("a", 3)),
            user_msg(&img_content("b", 3)),
        ];
        let result = trim_old_images(&msgs, 2);
        let total: usize = image_count(&result).iter().sum();
        assert!(total <= 2, "expected <= 2 images after trim, got {total}");
    }

    #[test]
    fn trims_oldest_first() {
        // 3 messages × 2 images = 6, max 3 → strip oldest and middle
        let msgs = vec![
            user_msg(&img_content("oldest", 2)),
            user_msg(&img_content("middle", 2)),
            user_msg(&img_content("newest", 2)),
        ];
        let result = trim_old_images(&msgs, 3);
        let counts = image_count(&result);
        assert_eq!(counts[0], 0, "oldest must lose all images");
        assert_eq!(counts[2], 2, "newest must keep images");
    }

    #[test]
    fn trims_oldest_first_varied() {
        // 4 messages with varying image counts, max 4
        let msgs = vec![
            user_msg(&img_content("m0", 3)),
            user_msg(&img_content("m1", 1)),
            user_msg(&img_content("m2", 2)),
            user_msg(&img_content("m3", 2)),
        ];
        // total=8, max=4 → drop 4: strip m0 (3 dropped), strip m1 (1 dropped) → done
        let result = trim_old_images(&msgs, 4);
        let counts = image_count(&result);
        assert_eq!(counts[0], 0, "m0 must be stripped");
        assert_eq!(counts[1], 0, "m1 must be stripped");
        assert_eq!(counts[2], 2, "m2 must keep images");
        assert_eq!(counts[3], 2, "m3 must keep images");
    }

    #[test]
    fn preserves_text_content() {
        let msgs = vec![
            user_msg(&img_content("important payload", 2)),
            user_msg(&img_content("keep me", 1)),
        ];
        let result = trim_old_images(&msgs, 1);
        assert!(
            result[0].content.contains("important payload"),
            "text must survive trimming, got: {:?}",
            result[0].content
        );
    }

    #[test]
    fn preserves_text_varied() {
        // Different text lengths
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
    }

    #[test]
    fn placeholder_for_image_only() {
        let msgs = vec![
            user_msg(&img_content("", 2)),
            user_msg(&img_content("text", 1)),
        ];
        let result = trim_old_images(&msgs, 1);
        assert!(
            result[0].content.to_lowercase().contains("image removed"),
            "image-only message needs placeholder, got: {:?}",
            result[0].content
        );
    }

    #[test]
    fn skips_assistant_messages() {
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
    }

    #[test]
    fn noop_when_within_limit() {
        let msgs = vec![
            user_msg(&img_content("a", 1)),
            user_msg(&img_content("b", 1)),
        ];
        let result = trim_old_images(&msgs, 10);
        let total: usize = image_count(&result).iter().sum();
        assert_eq!(total, 2, "no images should be removed when under limit");
    }

    #[test]
    fn noop_exactly_at_limit() {
        let msgs = vec![
            user_msg(&img_content("x", 2)),
            user_msg(&img_content("y", 3)),
        ];
        let result = trim_old_images(&msgs, 5);
        let total: usize = image_count(&result).iter().sum();
        assert_eq!(total, 5, "no trim when exactly at limit");
    }

    #[test]
    fn single_message_over_limit() {
        // One message with 5 images, max 2 → still trim that message
        let msgs = vec![
            user_msg(&img_content("solo", 5)),
        ];
        let result = trim_old_images(&msgs, 2);
        let total: usize = image_count(&result).iter().sum();
        assert!(total <= 2, "single message must be trimmed too, got {total}");
    }
}
'''


@pytest.fixture(scope="module")
def rust_behavioral():
    """Inject behavioral Rust tests into multimodal.rs, run cargo test, restore."""
    src = TARGET.read_text()
    TARGET.write_text(src + "\n" + RUST_TEST_MODULE)
    try:
        r = subprocess.run(
            ["cargo", "test", "harbor_bhv", "--", "--test-threads=1"],
            cwd=REPO,
            capture_output=True,
            timeout=180,
        )
        combined = r.stdout.decode(errors="replace") + "\n" + r.stderr.decode(errors="replace")
        return combined
    finally:
        TARGET.write_text(src)


def _assert_rust_test(output: str, test_name: str, msg: str):
    """Check that a specific injected Rust test passed."""
    # cargo test output: "test harbor_bhv::name ... ok"
    assert f"harbor_bhv::{test_name} ... ok" in output, (
        f"{msg}\n--- cargo test output (last 3000 chars) ---\n{output[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Code must compile with cargo check."""
    r = subprocess.run(
        ["cargo", "check"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode(errors='replace')[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via injected Rust code
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_hard_error_on_excess_images(rust_behavioral):
    """Must not return TooManyImages — trims oldest images instead."""
    _assert_rust_test(
        rust_behavioral, "no_error_on_excess",
        "Excess images should be trimmed, not rejected with an error",
    )


# [pr_diff] fail_to_pass
def test_trim_targets_oldest_user_messages(rust_behavioral):
    """Trim removes images from oldest user messages first, skips assistant."""
    _assert_rust_test(
        rust_behavioral, "trims_oldest_first",
        "Must remove images from oldest messages first",
    )
    _assert_rust_test(
        rust_behavioral, "trims_oldest_first_varied",
        "Must remove images from oldest messages first (varied counts)",
    )
    _assert_rust_test(
        rust_behavioral, "skips_assistant_messages",
        "Must not modify assistant messages during trim",
    )


# [pr_diff] fail_to_pass
def test_preserves_text_with_placeholder(rust_behavioral):
    """Trimmed messages keep text; image-only messages get placeholder."""
    _assert_rust_test(
        rust_behavioral, "preserves_text_content",
        "Text content must survive image trimming",
    )
    _assert_rust_test(
        rust_behavioral, "preserves_text_varied",
        "Text of varying lengths must survive trimming",
    )
    _assert_rust_test(
        rust_behavioral, "placeholder_for_image_only",
        "Image-only messages need '[image removed …]' placeholder",
    )


# [pr_diff] fail_to_pass
def test_trim_within_limit_noop(rust_behavioral):
    """When under the limit, no images should be removed."""
    _assert_rust_test(
        rust_behavioral, "noop_when_within_limit",
        "Should not trim images when count is within max_images",
    )
    _assert_rust_test(
        rust_behavioral, "noop_exactly_at_limit",
        "Should not trim when image count exactly equals the limit",
    )


# [pr_diff] fail_to_pass
def test_single_message_trim(rust_behavioral):
    """A single user message exceeding the limit must still be handled."""
    _assert_rust_test(
        rust_behavioral, "single_message_over_limit",
        "Single message with excess images must be trimmed",
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_prepare_messages_not_stub():
    """prepare_messages_for_provider has real logic, not a stub."""
    src = TARGET.read_text()
    # AST-only because: Rust cannot be imported from Python; public API is async+network
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
