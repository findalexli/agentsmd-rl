"""
Task: mimir-add-splitfile-claude-code-skill
Repo: grafana/mimir @ 0de2c7d947b81573a2c13bf4b931f9a2a04891ec
PR:   14847

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/mimir"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_verify_tool_compiles():
    """The split-file-verify Go tool must compile without errors."""
    tool_dir = Path(REPO) / "tools" / "split-file-verify"
    assert tool_dir.exists(), "tools/split-file-verify directory must exist"
    main_go = tool_dir / "main.go"
    assert main_go.exists(), "tools/split-file-verify/main.go must exist"

    result = subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Go build failed:\n{result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for the verify tool
# ---------------------------------------------------------------------------

def test_verify_tool_extracts_func_decls():
    """The verify tool correctly extracts function declarations from Go files."""
    # Build the tool first
    subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Create a test Go file with known declarations
    test_file = Path("/tmp/test_decls.go")
    test_file.write_text("""\
package main

func hello() {
    println("hello")
}

func world() {
    println("world")
}
""")

    result = subprocess.run(
        ["/tmp/split-file-verify", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Tool failed:\n{result.stderr}"

    lines = result.stdout.strip().split("\n")
    names = [line.split("\t")[0] for line in lines]
    assert "hello" in names, "Should extract 'hello' function"
    assert "world" in names, "Should extract 'world' function"
    assert len(lines) == 2, f"Should find exactly 2 declarations, got {len(lines)}"


def test_verify_tool_extracts_methods():
    """The verify tool correctly formats method names with receiver type."""
    subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    test_file = Path("/tmp/test_methods.go")
    test_file.write_text("""\
package main

type Server struct{}

func (s *Server) Start() {
    println("start")
}

func (s *Server) Stop() {
    println("stop")
}
""")

    result = subprocess.run(
        ["/tmp/split-file-verify", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Tool failed:\n{result.stderr}"

    lines = result.stdout.strip().split("\n")
    names = [line.split("\t")[0] for line in lines]
    # Methods should include receiver type
    assert "(Server).Start" in names, f"Should format method as (Server).Start, got {names}"
    assert "(Server).Stop" in names, f"Should format method as (Server).Stop, got {names}"


def test_verify_tool_extracts_types():
    """The verify tool extracts type declarations."""
    subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    test_file = Path("/tmp/test_types.go")
    test_file.write_text("""\
package main

type Config struct {
    Name string
    Port int
}

type Handler interface {
    Handle()
}
""")

    result = subprocess.run(
        ["/tmp/split-file-verify", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Tool failed:\n{result.stderr}"

    lines = result.stdout.strip().split("\n")
    names = [line.split("\t")[0] for line in lines]
    assert "type Config" in names, f"Should extract 'type Config', got {names}"
    assert "type Handler" in names, f"Should extract 'type Handler', got {names}"


def test_verify_tool_produces_consistent_hashes():
    """Same source content in different files must produce identical hashes."""
    subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    content = """\
package main

func doWork() int {
    return 42
}
"""
    Path("/tmp/hash_a.go").write_text(content)
    Path("/tmp/hash_b.go").write_text(content)

    result_a = subprocess.run(
        ["/tmp/split-file-verify", "/tmp/hash_a.go"],
        capture_output=True, text=True, timeout=30,
    )
    result_b = subprocess.run(
        ["/tmp/split-file-verify", "/tmp/hash_b.go"],
        capture_output=True, text=True, timeout=30,
    )

    assert result_a.returncode == 0
    assert result_b.returncode == 0

    hash_a = result_a.stdout.strip().split("\t")[1]
    hash_b = result_b.stdout.strip().split("\t")[1]
    assert hash_a == hash_b, f"Same content should produce same hash: {hash_a} != {hash_b}"


def test_verify_tool_sorted_output():
    """Output must be sorted by declaration name."""
    subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    test_file = Path("/tmp/test_sort.go")
    test_file.write_text("""\
package main

func zebra() {}
func alpha() {}
func middle() {}
""")

    result = subprocess.run(
        ["/tmp/split-file-verify", str(test_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0

    names = [line.split("\t")[0] for line in result.stdout.strip().split("\n")]
    assert names == sorted(names), f"Output should be sorted, got: {names}"


def test_verify_tool_multi_file():
    """The tool should accept multiple files and combine their declarations."""
    subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    Path("/tmp/multi_a.go").write_text("package main\n\nfunc fromA() {}\n")
    Path("/tmp/multi_b.go").write_text("package main\n\nfunc fromB() {}\n")

    result = subprocess.run(
        ["/tmp/split-file-verify", "/tmp/multi_a.go", "/tmp/multi_b.go"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0

    names = [line.split("\t")[0] for line in result.stdout.strip().split("\n")]
    assert "fromA" in names, "Should include declaration from first file"
    assert "fromB" in names, "Should include declaration from second file"


def test_verify_tool_no_args_shows_usage():
    """Running with no arguments prints usage and exits non-zero."""
    subprocess.run(
        ["go", "build", "-o", "/tmp/split-file-verify", "./tools/split-file-verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    result = subprocess.run(
        ["/tmp/split-file-verify"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0, "Should fail with no arguments"
    assert "Usage" in result.stderr, "Should print usage message"


# ---------------------------------------------------------------------------
# Config file update tests (config_edit) — SKILL.md must exist and be correct
# ---------------------------------------------------------------------------

def test_skill_md_exists():
    """SKILL.md file exists at the correct path."""
    skill_path = Path(REPO) / ".claude" / "skills" / "split-file" / "SKILL.md"
    assert skill_path.exists(), "SKILL.md must exist at .claude/skills/split-file/SKILL.md"


def test_skill_md_frontmatter():
    """SKILL.md has correct YAML frontmatter format."""
    skill_path = Path(REPO) / ".claude" / "skills" / "split-file" / "SKILL.md"
    assert skill_path.exists(), "SKILL.md must exist"

    content = skill_path.read_text()
    # Must have YAML frontmatter with name and description
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert "name:" in content.split("---")[1], "Frontmatter must include 'name' field"
    assert "split-file" in content.split("---")[1].lower(), "Skill name should be 'split-file'"
    assert "description:" in content.split("---")[1], "Frontmatter must include 'description' field"


def test_skill_md_git_rename_technique():
    """SKILL.md documents the git rename/rename conflict technique."""
    skill_path = Path(REPO) / ".claude" / "skills" / "split-file" / "SKILL.md"
    content = skill_path.read_text()

    assert "git mv" in content, "Should document git mv command for file renaming"
    assert "rename" in content, "Should mention rename technique"
    assert "history" in content or "follow" in content, \
        "Should mention preserving git history or git log --follow"
    assert "conflict" in content, \
        "Should mention the rename/rename conflict technique"


def test_skill_md_verify_tool():
    """SKILL.md references the split-file-verify tool."""
    skill_path = Path(REPO) / ".claude" / "skills" / "split-file" / "SKILL.md"
    content = skill_path.read_text()

    assert "split-file-verify" in content, \
        "Should reference the split-file-verify tool"
    assert "hash" in content.lower() or "sha256" in content.lower(), \
        "Should mention hash-based verification"
    assert "tsv" in content.lower() or "diff" in content.lower(), \
        "Should mention TSV output format or diff comparison"


def test_skill_md_workflow_phases():
    """SKILL.md describes a multi-phase workflow."""
    skill_path = Path(REPO) / ".claude" / "skills" / "split-file" / "SKILL.md"
    content = skill_path.read_text()

    assert "analyze" in content or "analysis" in content, \
        "Should have an analysis/planning phase"
    assert "split" in content, \
        "Should have a split phase"
    assert "verify" in content or "verification" in content, \
        "Should have a verification phase"


def test_skill_md_goimports_warning():
    """SKILL.md warns about goimports alias resolution issues."""
    skill_path = Path(REPO) / ".claude" / "skills" / "split-file" / "SKILL.md"
    content = skill_path.read_text()

    assert "goimports" in content, \
        "Should mention goimports for fixing imports after split"
    # Should warn about alias issues — a key gotcha from experience
    assert "alias" in content or "wrong package" in content or "resolv" in content, \
        "Should warn about goimports alias resolution issues"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI commands that should pass at base commit
# ---------------------------------------------------------------------------

def test_repo_tools_build():
    """All tools in the repo compile successfully (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./tools/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**subprocess.os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert result.returncode == 0, f"Tools build failed:\n{result.stderr}"


def test_repo_tools_vet():
    """Go vet passes on all tools (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./tools/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**subprocess.os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert result.returncode == 0, f"Go vet failed:\n{result.stderr}"


def test_repo_tools_test():
    """Unit tests for tools pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-short", "-count=1", "./tools/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**subprocess.os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert result.returncode == 0, f"Tools tests failed:\n{result.stderr}"


def test_repo_mod_tidy():
    """Go mod is tidy (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "tidy", "-diff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env={**subprocess.os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert result.returncode == 0, f"go mod tidy -diff failed:\n{result.stderr}"
