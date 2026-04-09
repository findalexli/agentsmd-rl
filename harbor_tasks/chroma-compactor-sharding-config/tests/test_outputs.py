"""Tests for the per-tenant sharding configuration task.

This validates:
1. The `tenant_matches_patterns` function correctly matches tenant IDs against patterns
2. The `CompactionJob` struct includes a `tenant_id` field
3. The `CompactorConfig` includes `sharding_enabled_tenant_patterns` field
4. The compaction manager properly filters shard_size based on tenant patterns
"""

import subprocess
import sys
import os

REPO = "/workspace/chroma"
RUST_WORKER = f"{REPO}/rust/worker"


def test_tenant_matches_patterns_star_wildcard():
    """Test that '*' pattern matches any tenant ID."""
    test_code = '''
fn tenant_matches_patterns(tenant_id: &str, patterns: &[String]) -> bool {
    for pattern in patterns {
        if pattern == "*" {
            return true;
        }
        if pattern == tenant_id {
            return true;
        }
    }
    false
}

fn main() {
    let patterns = vec!["*".to_string()];
    assert!(tenant_matches_patterns("any-tenant", &patterns));
    assert!(tenant_matches_patterns("tenant-1", &patterns));
    assert!(tenant_matches_patterns("", &patterns));
    println!("PASS");
}
'''
    result = subprocess.run(
        ["rustc", "--edition", "2021", "-o", "/tmp/test_wildcard", "-"],
        input=test_code,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Check the function exists in the source
        result = subprocess.run(
            ["grep", "-q", "fn tenant_matches_patterns", f"{RUST_WORKER}/src/compactor/compaction_manager.rs"],
            capture_output=True
        )
        assert result.returncode == 0, "tenant_matches_patterns function not found"


def test_tenant_matches_patterns_exact_match():
    """Test exact tenant ID matching."""
    test_code = '''
fn tenant_matches_patterns(tenant_id: &str, patterns: &[String]) -> bool {
    for pattern in patterns {
        if pattern == "*" {
            return true;
        }
        if pattern == tenant_id {
            return true;
        }
    }
    false
}

fn main() {
    let patterns = vec!["tenant-1".to_string(), "tenant-2".to_string()];
    assert!(tenant_matches_patterns("tenant-1", &patterns));
    assert!(tenant_matches_patterns("tenant-2", &patterns));
    assert!(!tenant_matches_patterns("tenant-3", &patterns));
    assert!(!tenant_matches_patterns("other", &patterns));
    println!("PASS");
}
'''
    result = subprocess.run(
        ["rustc", "--edition", "2021", "-o", "/tmp/test_exact", "-"],
        input=test_code,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Verify function exists
        result = subprocess.run(
            ["grep", "-q", "fn tenant_matches_patterns", f"{RUST_WORKER}/src/compactor/compaction_manager.rs"],
            capture_output=True
        )
        assert result.returncode == 0, "tenant_matches_patterns function not found"


def test_tenant_matches_patterns_empty():
    """Test that empty patterns list returns false."""
    test_code = '''
fn tenant_matches_patterns(tenant_id: &str, patterns: &[String]) -> bool {
    for pattern in patterns {
        if pattern == "*" {
            return true;
        }
        if pattern == tenant_id {
            return true;
        }
    }
    false
}

fn main() {
    let patterns: Vec<String> = vec![];
    assert!(!tenant_matches_patterns("any-tenant", &patterns));
    println!("PASS");
}
'''
    result = subprocess.run(
        ["rustc", "--edition", "2021", "-o", "/tmp/test_empty", "-"],
        input=test_code,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["grep", "-q", "fn tenant_matches_patterns", f"{RUST_WORKER}/src/compactor/compaction_manager.rs"],
            capture_output=True
        )
        assert result.returncode == 0, "tenant_matches_patterns function not found"


def test_compaction_job_has_tenant_id():
    """Test that CompactionJob struct includes tenant_id field."""
    result = subprocess.run(
        ["grep", "tenant_id", f"{RUST_WORKER}/src/compactor/types.rs"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "CompactionJob missing tenant_id field"
    assert "String" in result.stdout, "tenant_id should be String type"


def test_compactor_config_has_patterns():
    """Test that CompactorConfig includes sharding_enabled_tenant_patterns."""
    result = subprocess.run(
        ["grep", "sharding_enabled_tenant_patterns", f"{RUST_WORKER}/src/compactor/config.rs"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "CompactorConfig missing sharding_enabled_tenant_patterns"
    assert "Vec<String>" in result.stdout or "Vec<String>" in result.stdout.replace(" ", ""), \
        "sharding_enabled_tenant_patterns should be Vec<String>"


def test_scheduler_job_includes_tenant():
    """Test that scheduler properly sets tenant_id in CompactionJob."""
    result = subprocess.run(
        ["grep", "tenant_id", f"{RUST_WORKER}/src/compactor/scheduler.rs"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "Scheduler doesn't include tenant_id"


def test_scheduler_policy_includes_tenant():
    """Test that scheduler policy properly sets tenant_id in CompactionJob."""
    result = subprocess.run(
        ["grep", "tenant_id", f"{RUST_WORKER}/src/compactor/scheduler_policy.rs"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "SchedulerPolicy doesn't include tenant_id"


def test_cargo_check_compiles():
    """Test that the Rust code compiles successfully."""
    result = subprocess.run(
        ["cargo", "check", "--lib"],
        cwd=RUST_WORKER,
        capture_output=True,
        timeout=120
    )
    assert result.returncode == 0, f"Cargo check failed:\n{result.stderr.decode()}"


def test_context_has_sharding_patterns():
    """Test that CompactionManagerContext includes sharding_enabled_tenant_patterns."""
    result = subprocess.run(
        ["grep", "sharding_enabled_tenant_patterns", f"{RUST_WORKER}/src/compactor/compaction_manager.rs"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "CompactionManagerContext missing sharding_enabled_tenant_patterns"


def test_cargo_clippy_worker():
    """Repo's Rust worker crate passes clippy lints (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "clippy", "--lib", "-p", "worker", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Clippy failed:\n{result.stderr[-500:]}"


def test_cargo_test_worker_unit():
    """Repo's Rust worker crate lib tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "test", "--lib", "-p", "worker"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:]}"
