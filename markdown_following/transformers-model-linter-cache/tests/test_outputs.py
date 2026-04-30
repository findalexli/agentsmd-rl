"""
Task: transformers-model-linter-cache
Repo: huggingface/transformers @ aa1c36f1a9f454e69c4eac83071ced235942c7ed
PR:   #44790

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

REPO = "/workspace/transformers"
LINTER = f"{REPO}/utils/check_modeling_structure.py"
BASE_COMMIT = "aa1c36f1a9f454e69c4eac83071ced235942c7ed"


def _extract_and_exec(
    filepath: str,
    func_names: list[str],
    const_names: list[str] | None = None,
) -> dict:
    """Extract top-level functions (and optionally constants) and exec them.

    Returns a namespace dict containing the executed functions.
    AST-only because: check_modeling_structure.py has heavy module-level
    code (TOML rule loading, rule auto-discovery, rich Console) that
    requires the full repo environment to import.
    """
    source = Path(filepath).read_text()
    tree = ast.parse(source, filename=filepath)
    const_names = set(const_names or [])

    imports = []
    consts = []
    funcs = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)
        elif isinstance(node, ast.Assign) and const_names:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in const_names:
                    consts.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in func_names:
                funcs.append(node)

    assert len(funcs) == len(func_names), (
        f"Expected to find {func_names}, found {[f.name for f in funcs]}"
    )

    new_tree = ast.Module(body=imports + consts + funcs, type_ignores=[])
    ast.fix_missing_locations(new_tree)
    code = compile(new_tree, filepath, "exec")

    ns: dict = {"__file__": filepath}
    exec(code, ns)
    return ns


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without syntax errors."""
    target = Path(LINTER)
    source = target.read_text()
    ast.parse(source, filename=str(target))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_content_hash():
    """Content hash function: deterministic, content-sensitive, order-insensitive."""
    ns = _extract_and_exec(LINTER, ["_content_hash"])
    _content_hash = ns["_content_hash"]

    # Deterministic across multiple calls
    for text, rules in [
        ("hello world", {"ruleA", "ruleB"}),
        ("", set()),
        ("x" * 10000, {"a", "b", "c", "d"}),
    ]:
        assert _content_hash(text, rules) == _content_hash(text, rules)

    # Different text -> different hash
    h1 = _content_hash("hello world", {"ruleA", "ruleB"})
    h2 = _content_hash("goodbye world", {"ruleA", "ruleB"})
    h3 = _content_hash("hello world!", {"ruleA", "ruleB"})
    assert h1 != h2, "Different text must produce different hash"
    assert h1 != h3, "Even small text changes must produce different hash"

    # Different rules -> different hash
    h4 = _content_hash("hello world", {"ruleA", "ruleC"})
    h5 = _content_hash("hello world", {"ruleA"})
    assert h1 != h4, "Different rules must produce different hash"
    assert h1 != h5, "Subset of rules must produce different hash"

    # Rule order insensitive (set semantics)
    h6 = _content_hash("hello world", {"ruleB", "ruleA"})
    assert h1 == h6, f"Rule order must not matter: {h1} vs {h6}"

    # Returns hex string of reasonable length
    assert len(h1) >= 32, f"Expected hex string >= 32 chars, got {len(h1)}"
    assert all(c in "0123456789abcdef" for c in h1), "Must be a hex string"


# [pr_diff] fail_to_pass
def test_cache_save_load_round_trip():
    """Cache save/load: round-trip persistence and missing-file handling."""
    # Find the module-level Path constant that points to the .json cache file
    source = Path(LINTER).read_text()
    tree = ast.parse(source)
    cache_var = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    src_segment = ast.get_source_segment(source, node.value) or ""
                    if ".json" in src_segment and "cache" in src_segment.lower():
                        cache_var = target.id
    assert cache_var, "No cache path constant found in module"

    ns = _extract_and_exec(
        LINTER, ["_load_cache", "_save_cache"], const_names=[cache_var]
    )
    _load_cache = ns["_load_cache"]
    _save_cache = ns["_save_cache"]

    # Redirect to a temp file so tests don't pollute the repo
    tmp = Path(tempfile.mktemp(suffix=".json"))
    ns[cache_var] = tmp
    try:
        # Round-trip with multiple entries
        data = {"file_a.py": "abc123", "file_b.py": "def456", "file_c.py": "ghi789"}
        _save_cache(data)
        loaded = _load_cache()
        assert loaded == data, f"Round-trip failed: {loaded} != {data}"

        # Verify the file is valid JSON on disk
        raw = json.loads(tmp.read_text())
        assert raw == data, f"JSON on disk mismatch: {raw}"

        # Empty dict round-trip
        _save_cache({})
        loaded = _load_cache()
        assert loaded == {}, f"Empty dict round-trip failed: {loaded}"

        # Missing file returns empty dict (graceful handling)
        tmp.unlink()
        empty = _load_cache()
        assert empty == {}, f"Missing file should return empty dict, got {empty}"
    finally:
        if tmp.exists():
            tmp.unlink()


# [pr_diff] fail_to_pass
def test_cli_cache_flag():
    """Script has a CLI flag to disable/bypass caching."""
    r = subprocess.run(
        ["python3", LINTER, "--help"],
        capture_output=True, text=True, timeout=30,
    )
    help_text = (r.stdout + r.stderr).lower()
    assert "cache" in help_text, "No cache-related option in --help output"


# [pr_diff] fail_to_pass
def test_makefile_typing_target():
    """Makefile has a 'typing' target that invokes the model linter."""
    r = subprocess.run(
        ["make", "-n", "typing"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"make -n typing failed: {r.stderr}"
    output = r.stdout + r.stderr
    assert "check_modeling_structure" in output, (
        "typing target must invoke check_modeling_structure"
    )


# [pr_diff] fail_to_pass
def test_redundant_targets_removed():
    """Legacy check-model-rules* targets no longer exist in Makefile."""
    for target in ["check-model-rules", "check-model-rules-pr", "check-model-rules-all"]:
        r = subprocess.run(
            ["make", "-n", target],
            cwd=REPO, capture_output=True, text=True, timeout=10,
        )
        assert r.returncode != 0, (
            f"Redundant target '{target}' still exists in Makefile"
        )


# [pr_diff] fail_to_pass
def test_check_repo_runs_linter():
    """check-repo target invokes check_modeling_structure without error-ignore prefix.

    In Make, a '-' prefix before a command means 'ignore errors'. The linter
    must run WITHOUT this prefix so violations are not silently swallowed.
    """
    # Behavioral: verify check-repo dry run includes the linter
    r = subprocess.run(
        ["make", "-n", "check-repo"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"make -n check-repo failed: {r.stderr}"
    assert "check_modeling_structure" in (r.stdout + r.stderr), (
        "check-repo target must invoke check_modeling_structure"
    )

    # Structural: parse Makefile to verify EVERY invocation of the linter
    # in check-repo is strict (no '-' error-ignore prefix).
    makefile = Path(f"{REPO}/Makefile").read_text()
    in_target = False
    linter_lines = []
    for line in makefile.split("\n"):
        if line.startswith("check-repo"):
            in_target = True
            continue
        if in_target:
            if line and not line[0].isspace() and not line.startswith("#"):
                break  # next target
            if "check_modeling_structure" in line:
                linter_lines.append(line)

    assert linter_lines, "check-repo must invoke check_modeling_structure"
    for line in linter_lines:
        stripped = line.strip()
        assert not stripped.startswith("-"), (
            f"check-repo runs check_modeling_structure with error-ignore "
            f"prefix (-): {stripped!r}; violations would be silently swallowed"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_parse_args_backward_compat():
    """Existing CLI flags (--list-rules, --no-progress, --changed-only) still work."""
    for flag_set, check in [
        (["--list-rules"], "list_rules"),
        (["--no-progress"], "no_progress"),
        (["--changed-only", "--base-ref", "main"], "changed_only"),
    ]:
        r = subprocess.run(
            ["python3", "-c", textwrap.dedent(f"""\
                import sys
                sys.path.insert(0, "{REPO}/utils")
                sys.argv = ["check_modeling_structure.py"] + {flag_set!r}
                from check_modeling_structure import parse_args
                args = parse_args()
                assert getattr(args, "{check}") is True or getattr(args, "{check}") == {flag_set[-1]!r}
            """)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"CLI flag {flag_set} failed: {r.stderr}"
        )


# ---------------------------------------------------------------------------
# Structural checks (pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gitignore_excludes_cache():
    """.gitignore excludes the model linter cache file."""
    # Find the cache path constant in the linter module
    source = Path(LINTER).read_text()
    tree = ast.parse(source)
    cache_var = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    src_segment = ast.get_source_segment(source, node.value) or ""
                    if ".json" in src_segment and "cache" in src_segment.lower():
                        cache_var = target.id
    assert cache_var, "No cache path constant found in module"

    # Extract and evaluate the constant to get the actual cache file path
    ns = _extract_and_exec(LINTER, [], const_names=[cache_var])
    cache_path = ns[cache_var]
    cache_rel = os.path.relpath(str(cache_path), REPO)

    # Behavioral: verify git actually ignores this path
    r = subprocess.run(
        ["git", "check-ignore", "-q", cache_rel],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"Cache file '{cache_rel}' is not excluded by .gitignore"
    )


# [pr_diff] fail_to_pass
def test_agents_md_references_typing():
    """.ai/AGENTS.md references 'make typing'."""
    agents_path = Path(f"{REPO}/.ai/AGENTS.md")
    assert agents_path.exists(), ".ai/AGENTS.md not found"
    content = agents_path.read_text()
    assert "make typing" in content, ".ai/AGENTS.md should reference 'make typing'"


# [pr_diff] fail_to_pass
def test_skill_md_references_typing():
    """.ai/skills/add-or-fix-type-checking/SKILL.md references 'make typing'."""
    skill_path = Path(f"{REPO}/.ai/skills/add-or-fix-type-checking/SKILL.md")
    assert skill_path.exists(), "SKILL.md not found"
    content = skill_path.read_text()
    assert "make typing" in content, "SKILL.md should reference 'make typing'"


# [pr_diff] fail_to_pass
def test_pr_checks_docs_reference_typing():
    """docs/source/en/pr_checks.md documents the 'make typing' target."""
    doc_path = Path(f"{REPO}/docs/source/en/pr_checks.md")
    assert doc_path.exists(), "pr_checks.md not found"
    content = doc_path.read_text()
    assert "make typing" in content, "pr_checks.md should document 'make typing'"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- .ai/AGENTS.md:2 @ aa1c36f1a9f454e69c4eac83071ced235942c7ed
def test_ruff_lint():
    """ruff lint passes on the modified linter file."""
    r = subprocess.run(
        ["ruff", "check", "--select=E,W,F", "--ignore=E501", "--no-fix", LINTER],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [agent_config] pass_to_pass -- .ai/skills/add-or-fix-type-checking/SKILL.md:185-186 @ aa1c36f1a9f454e69c4eac83071ced235942c7ed
def test_no_bare_type_ignore():
    """No bare '# type: ignore' without specific error code in modified file."""
    import re

    src = Path(LINTER).read_text()
    bare = re.findall(r"#\s*type:\s*ignore(?!\[)", src)
    assert len(bare) == 0, (
        f"Found {len(bare)} bare '# type: ignore' without error code. "
        "Use '# type: ignore[specific-error]' instead."
    )

# ---------------------------------------------------------------------------
# Repo-derived (repo_tests) -- actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_modeling_linter_help():
    """Model structure linter --help works (pass_to_pass)."""
    r = subprocess.run(
        ["python3", f"{REPO}/utils/check_modeling_structure.py", "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Linter --help failed:\n{r.stderr}"
    assert "--list-rules" in r.stdout, "Expected --list-rules in help output"


# [repo_tests] pass_to_pass
def test_repo_modeling_linter_list_rules():
    """Model structure linter --list-rules works and shows TRF rules (pass_to_pass)."""
    r = subprocess.run(
        ["python3", f"{REPO}/utils/check_modeling_structure.py", "--list-rules"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Linter --list-rules failed:\n{r.stderr}"
    output = r.stdout + r.stderr
    assert "TRF001" in output, "Expected TRF001 rule in output"
    assert "TRF002" in output, "Expected TRF002 rule in output"


# [repo_tests] pass_to_pass
def test_repo_ruff_utils():
    """Ruff lint on utils/check_modeling_structure.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--select=E,W,F", "--ignore=E501", "--no-fix",
         f"{REPO}/utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_make_check_repo_dryrun():
    """Makefile 'check-repo' target exists and references check_modeling_structure (pass_to_pass)."""
    r = subprocess.run(
        ["make", "-n", "check-repo"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"make -n check-repo failed:\n{r.stderr}"
    output = r.stdout + r.stderr
    assert "check_modeling_structure" in output, (
        "check-repo target must invoke check_modeling_structure"
    )


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Ruff format check passes on the modified linter file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", LINTER],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_linter_runs_on_models():
    """Model structure linter runs successfully on all modeling files (pass_to_pass)."""
    r = subprocess.run(
        ["python3", f"{REPO}/utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    # Linter returns 0 if no violations, 1 if violations found - both are "success" for running
    assert r.returncode in [0, 1], f"Linter failed to run: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_make_style_dryrun():
    """Makefile 'style' target exists and references expected commands (pass_to_pass)."""
    r = subprocess.run(
        ["make", "-n", "style"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"make -n style failed:\n{r.stderr}"
    output = r.stdout + r.stderr
    assert "ruff" in output, "style target must invoke ruff"


# [repo_tests] pass_to_pass
def test_repo_linter_core_trf001():
    """Core TRF001 rule functionality works via direct import (pass_to_pass)."""
    # Avoid f-string issues by constructing code as a raw string with format
    code_script = '''
import sys
sys.path.insert(0, "'''+REPO+'''/utils")
import check_modeling_structure as cms
from pathlib import Path

# Test TRF001 - valid case
source = """class FooPreTrainedModel(PreTrainedModel):
    config_class = FooConfig"""
file_path = Path("src/transformers/models/foo/modeling_foo.py")
violations = cms.analyze_file(file_path, source, enabled_rules={cms.TRF001})
trf001 = [v for v in violations if v.rule_id == cms.TRF001]
assert trf001 == [], f"Expected no TRF001 violations, got {trf001}"

# Test TRF001 - invalid case
source2 = """class FooPreTrainedModel(PreTrainedModel):
    config_class = BarConfig"""
violations2 = cms.analyze_file(file_path, source2, enabled_rules={cms.TRF001})
trf001_invalid = [v for v in violations2 if v.rule_id == cms.TRF001]
assert len(trf001_invalid) == 1, f"Expected 1 TRF001 violation, got {len(trf001_invalid)}"

print("TRF001 core functionality: PASSED")
'''
    r = subprocess.run(
        ["python3", "-c", code_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TRF001 test failed:\n{r.stderr}"
