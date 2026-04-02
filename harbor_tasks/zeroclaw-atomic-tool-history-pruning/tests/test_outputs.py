"""
Task: zeroclaw-atomic-tool-history-pruning
Repo: zeroclaw-labs/zeroclaw @ 753d4fc65f32b45797e7aba52db6c8eb3a24ad89
PR:   4825

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/zeroclaw"


def _inject_rust_test(rel_path: str, test_code: str, test_filter: str, *, timeout: int = 180):
    """Append a #[cfg(test)] block to a Rust source file, run matching tests, restore."""
    p = Path(REPO) / rel_path
    original = p.read_text()
    p.write_text(original + "\n" + test_code)
    try:
        r = subprocess.run(
            ["cargo", "test", "--lib", "--", test_filter, "--nocapture"],
            cwd=REPO, capture_output=True, timeout=timeout,
        )
        out = r.stdout.decode() + r.stderr.decode()
        assert "test result: ok" in out, (
            f"cargo test --lib -- {test_filter} failed:\n{out[-3000:]}"
        )
    finally:
        p.write_text(original)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compile():
    """Both modified Rust files compile with cargo check."""
    r = subprocess.run(
        ["cargo", "check", "--all-targets"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_emergency_trim_no_orphaned_tools():
    """emergency_history_trim drops assistant+consecutive tools as an atomic group."""
    _inject_rust_test(
        "src/agent/history.rs",
        textwrap.dedent("""\
            #[cfg(test)]
            mod test_trim_atomic_injected {
                use super::*;

                fn msg(role: &str) -> crate::providers::ChatMessage {
                    crate::providers::ChatMessage {
                        role: role.to_string(),
                        content: String::new(),
                    }
                }

                #[test]
                fn trim_one_must_not_orphan_tools() {
                    let mut history = vec![
                        msg("system"),
                        msg("assistant"),
                        msg("tool"),
                        msg("tool"),
                        msg("user"),
                    ];
                    let orig_len = history.len();
                    // Ask to drop just 1 message, keep last 1 recent.
                    // On buggy code this drops only the assistant, orphaning tools.
                    emergency_history_trim(&mut history, 1, 1);
                    assert!(history.len() < orig_len, "trim did not drop anything (stub?)");
                    for (i, m) in history.iter().enumerate() {
                        if m.role == "tool" {
                            assert!(
                                i > 0 && history[i - 1].role == "assistant",
                                "Orphaned tool at idx {}: {:?}",
                                i,
                                history.iter().map(|m| m.role.as_str()).collect::<Vec<_>>()
                            );
                        }
                    }
                }

                #[test]
                fn trim_with_multiple_groups() {
                    let mut history = vec![
                        msg("system"),
                        msg("assistant"),
                        msg("tool"),
                        msg("user"),
                        msg("assistant"),
                        msg("tool"),
                        msg("tool"),
                        msg("tool"),
                        msg("user"),
                        msg("assistant"),
                        msg("user"),
                    ];
                    let orig_len = history.len();
                    emergency_history_trim(&mut history, 2, 2);
                    assert!(history.len() < orig_len, "trim did not drop anything");
                    for (i, m) in history.iter().enumerate() {
                        if m.role == "tool" {
                            assert!(
                                i > 0 && history[i - 1].role == "assistant",
                                "Orphaned tool at idx {}: {:?}",
                                i,
                                history.iter().map(|m| m.role.as_str()).collect::<Vec<_>>()
                            );
                        }
                    }
                }
            }
        """),
        "test_trim_atomic_injected",
    )


# [pr_diff] fail_to_pass
def test_prune_budget_no_orphaned_tools():
    """prune_history Phase 2 budget enforcement drops assistant+tool groups atomically."""
    _inject_rust_test(
        "src/agent/history_pruner.rs",
        textwrap.dedent("""\
            #[cfg(test)]
            mod test_budget_atomic_injected {
                use super::*;

                fn msg(role: &str, content: &str) -> ChatMessage {
                    ChatMessage {
                        role: role.to_string(),
                        content: content.to_string(),
                    }
                }

                #[test]
                fn budget_drop_must_not_orphan_tools() {
                    let big = "x".repeat(10000);
                    let mut msgs = vec![
                        msg("system", "sys"),
                        msg("assistant", &big),
                        msg("tool", &big),
                        msg("tool", &big),
                        msg("user", "short"),
                        msg("assistant", "recent"),
                        msg("user", "recent"),
                    ];
                    let orig_len = msgs.len();
                    let config = HistoryPrunerConfig {
                        collapse_tool_results: false,
                        keep_recent: 2,
                        max_tokens: 50,
                        ..Default::default()
                    };
                    prune_history(&mut msgs, &config);
                    assert!(msgs.len() < orig_len, "prune did not drop anything (stub?)");
                    for (i, m) in msgs.iter().enumerate() {
                        if m.role == "tool" {
                            assert!(
                                i > 0 && msgs[i - 1].role == "assistant",
                                "Orphaned tool at idx {}: {:?}",
                                i,
                                msgs.iter().map(|m| m.role.as_str()).collect::<Vec<_>>()
                            );
                        }
                    }
                }

                #[test]
                fn budget_drop_varied_group_sizes() {
                    let big = "y".repeat(8000);
                    let mut msgs = vec![
                        msg("system", "s"),
                        msg("assistant", &big),
                        msg("tool", &big),
                        msg("user", "ok"),
                        msg("assistant", &big),
                        msg("tool", &big),
                        msg("tool", &big),
                        msg("tool", &big),
                        msg("user", "recent q"),
                        msg("assistant", "recent a"),
                        msg("user", "recent follow-up"),
                    ];
                    let orig_len = msgs.len();
                    let config = HistoryPrunerConfig {
                        collapse_tool_results: false,
                        keep_recent: 3,
                        max_tokens: 100,
                        ..Default::default()
                    };
                    prune_history(&mut msgs, &config);
                    assert!(msgs.len() < orig_len, "prune did not drop anything");
                    for (i, m) in msgs.iter().enumerate() {
                        if m.role == "tool" {
                            assert!(
                                i > 0 && msgs[i - 1].role == "assistant",
                                "Orphaned tool at idx {}: {:?}",
                                i,
                                msgs.iter().map(|m| m.role.as_str()).collect::<Vec<_>>()
                            );
                        }
                    }
                }
            }
        """),
        "test_budget_atomic_injected",
    )


# [pr_diff] fail_to_pass
def test_prune_collapse_then_budget_no_orphaned_tools():
    """Full prune cycle (collapse + budget) preserves tool pairing with multi-tool groups."""
    _inject_rust_test(
        "src/agent/history_pruner.rs",
        textwrap.dedent("""\
            #[cfg(test)]
            mod test_full_cycle_injected {
                use super::*;

                fn msg(role: &str, content: &str) -> ChatMessage {
                    ChatMessage {
                        role: role.to_string(),
                        content: content.to_string(),
                    }
                }

                #[test]
                fn collapse_plus_budget_no_orphans() {
                    let big = "z".repeat(5000);
                    let mut msgs = vec![
                        msg("system", "sys"),
                        msg("user", "q1"),
                        msg("assistant", &big),
                        msg("tool", &big),
                        msg("tool", &big),
                        msg("tool", &big),
                        msg("user", "q2"),
                        msg("assistant", &big),
                        msg("tool", &big),
                        msg("user", "recent"),
                        msg("assistant", "recent reply"),
                    ];
                    let orig_len = msgs.len();
                    let config = HistoryPrunerConfig {
                        collapse_tool_results: true,
                        keep_recent: 2,
                        max_tokens: 200,
                        ..Default::default()
                    };
                    prune_history(&mut msgs, &config);
                    assert!(msgs.len() < orig_len, "prune did not drop anything (stub?)");
                    for (i, m) in msgs.iter().enumerate() {
                        if m.role == "tool" {
                            assert!(
                                i > 0 && msgs[i - 1].role == "assistant",
                                "Orphaned tool at idx {}: {:?}",
                                i,
                                msgs.iter().map(|m| m.role.as_str()).collect::<Vec<_>>()
                            );
                        }
                    }
                }

                #[test]
                fn fifteen_iterations_under_pressure() {
                    let mut msgs = vec![msg("system", "sys")];
                    msgs.push(msg("user", "research this"));
                    for i in 0..15 {
                        let content = format!("iteration-{}", i);
                        let result = "r".repeat(2000);
                        msgs.push(msg("assistant", &content));
                        msgs.push(msg("tool", &result));
                    }
                    msgs.push(msg("assistant", "summary"));

                    let config = HistoryPrunerConfig {
                        collapse_tool_results: true,
                        keep_recent: 4,
                        max_tokens: 2000,
                        ..Default::default()
                    };
                    prune_history(&mut msgs, &config);
                    for (i, m) in msgs.iter().enumerate() {
                        if m.role == "tool" {
                            assert!(
                                i > 0 && msgs[i - 1].role == "assistant",
                                "Orphaned tool at idx {}: roles={:?}",
                                i,
                                msgs.iter().map(|m| m.role.as_str()).collect::<Vec<_>>()
                            );
                        }
                    }
                }
            }
        """),
        "test_full_cycle_injected",
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_cargo_tests():
    """Existing library tests still pass (no regressions)."""
    r = subprocess.run(
        ["cargo", "test", "--lib"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"cargo test --lib failed:\n{out[-2000:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:8 @ 753d4fc65f32b45797e7aba52db6c8eb3a24ad89
def test_cargo_fmt():
    """Code passes cargo fmt check (AGENTS.md:8)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"cargo fmt check failed:\n{r.stdout.decode()[-2000:]}"
    )


# [agent_config] pass_to_pass — AGENTS.md:9 @ 753d4fc65f32b45797e7aba52db6c8eb3a24ad89
def test_cargo_clippy():
    """Code passes cargo clippy check (AGENTS.md:9)."""
    r = subprocess.run(
        ["cargo", "clippy", "--all-targets", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, timeout=180,
    )
    assert r.returncode == 0, (
        f"cargo clippy failed:\n{r.stderr.decode()[-2000:]}"
    )
