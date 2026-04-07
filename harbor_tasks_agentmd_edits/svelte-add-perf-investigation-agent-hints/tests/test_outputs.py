"""
Task: svelte-add-perf-investigation-agent-hints
Repo: sveltejs/svelte @ c93e251654a3193f294d6a4171d4087b4cb2fb80
PR:   18047

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/svelte"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_profile_diff_usage_error():
    """profile-diff.mjs prints usage and exits 1 when called without arguments."""
    script = Path(REPO) / "benchmarking" / "compare" / "profile-diff.mjs"
    assert script.exists(), "benchmarking/compare/profile-diff.mjs must exist"
    r = subprocess.run(
        ["node", str(script)],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 1, f"Expected exit code 1, got {r.returncode}"
    assert "Usage" in r.stderr, f"Expected usage message in stderr, got: {r.stderr}"


# [pr_diff] fail_to_pass
def test_profile_diff_missing_candidate():
    """profile-diff.mjs exits 1 when only benchmark and base branch are given."""
    script = Path(REPO) / "benchmarking" / "compare" / "profile-diff.mjs"
    assert script.exists(), "benchmarking/compare/profile-diff.mjs must exist"
    r = subprocess.run(
        ["node", str(script), "kairo_mux", "main"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 1, f"Expected exit code 1, got {r.returncode}"
    assert "Usage" in r.stderr, f"Expected usage in stderr, got: {r.stderr}"


# [pr_diff] fail_to_pass
def test_profile_diff_compares_profiles():
    """profile-diff.mjs reads cpuprofile files and outputs hotspot deltas."""
    script = Path(REPO) / "benchmarking" / "compare" / "profile-diff.mjs"
    assert script.exists(), "benchmarking/compare/profile-diff.mjs must exist"

    profiles_dir = Path(REPO) / "benchmarking" / "compare" / ".profiles"

    # Create mock cpuprofile data for base branch
    base_dir = profiles_dir / "main"
    base_dir.mkdir(parents=True, exist_ok=True)
    base_profile = {
        "nodes": [
            {"id": 1, "callFrame": {"functionName": "hotFunc", "url": "packages/svelte/src/runtime.js", "lineNumber": 10}},
            {"id": 2, "callFrame": {"functionName": "coldFunc", "url": "packages/svelte/src/utils.js", "lineNumber": 5}},
        ],
        "samples": [1, 1, 1, 2, 1, 1, 2, 1, 1, 1],
    }
    (base_dir / "test_bench.cpuprofile").write_text(json.dumps(base_profile))

    # Create mock cpuprofile data for candidate branch (hotFunc is hotter)
    cand_dir = profiles_dir / "feat"
    cand_dir.mkdir(parents=True, exist_ok=True)
    cand_profile = {
        "nodes": [
            {"id": 1, "callFrame": {"functionName": "hotFunc", "url": "packages/svelte/src/runtime.js", "lineNumber": 10}},
            {"id": 2, "callFrame": {"functionName": "coldFunc", "url": "packages/svelte/src/utils.js", "lineNumber": 5}},
        ],
        "samples": [1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
    }
    (cand_dir / "test_bench.cpuprofile").write_text(json.dumps(cand_profile))

    try:
        r = subprocess.run(
            ["node", str(script), "test_bench", "main", "feat"],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Script failed (rc={r.returncode}): {r.stderr}"
        assert "Benchmark: test_bench" in r.stdout, f"Missing benchmark header: {r.stdout}"
        assert "hotFunc" in r.stdout, f"Missing hotFunc in output: {r.stdout}"
        assert "coldFunc" in r.stdout, f"Missing coldFunc in output: {r.stdout}"
        assert "pp" in r.stdout, f"Missing 'pp' unit in output: {r.stdout}"
    finally:
        # Clean up mock data
        import shutil
        shutil.rmtree(profiles_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_references_skill():
    """AGENTS.md exists and references the performance-investigation skill."""
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.exists(), "AGENTS.md must be created at repository root"
    content = agents_md.read_text()
    assert "performance-investigation" in content, \
        "AGENTS.md should reference the performance-investigation skill"
    assert "CONTRIBUTING.md" in content, \
        "AGENTS.md should reference CONTRIBUTING.md for contribution guidelines"


# [pr_diff] fail_to_pass
def test_skill_md_has_frontmatter():
    """SKILL.md exists with proper YAML frontmatter including name and description."""
    skill_md = Path(REPO) / ".agents" / "skills" / "performance-investigation" / "SKILL.md"
    assert skill_md.exists(), ".agents/skills/performance-investigation/SKILL.md must exist"
    content = skill_md.read_text()
    # Check frontmatter delimiters
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have opening and closing --- for frontmatter"
    frontmatter = parts[1]
    assert "name:" in frontmatter, "Frontmatter must include 'name' field"
    assert "description:" in frontmatter, "Frontmatter must include 'description' field"
    assert "performance" in frontmatter.lower(), \
        "Frontmatter should reference performance investigation"


# [pr_diff] fail_to_pass
def test_skill_md_documents_benchmarking_workflow():
    """SKILL.md documents the bench:compare workflow and profile output locations."""
    skill_md = Path(REPO) / ".agents" / "skills" / "performance-investigation" / "SKILL.md"
    content = skill_md.read_text()
    assert "bench:compare" in content, \
        "SKILL.md should document the bench:compare command"
    assert ".profiles" in content or "cpuprofile" in content, \
        "SKILL.md should document CPU profile output locations"
    assert "profile-diff" in content, \
        "SKILL.md should reference the profile-diff utility script"
