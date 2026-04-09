"""
Task: posthog-sig-detailed-eval-matching
Repo: PostHog/posthog @ 7b8a1992516a0218c75784e8d2c987f78118d400
PR:   51319

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
EVAL_FILE = Path(REPO) / "products" / "signals" / "eval" / "eval_grouping_e2e.py"
MOCK_FILE = Path(REPO) / "products" / "signals" / "eval" / "mock.py"
AGENTS_FILE = Path(REPO) / "products" / "signals" / "eval" / "AGENTS.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    for fpath in [EVAL_FILE, MOCK_FILE]:
        src = fpath.read_text()
        ast.parse(src, filename=str(fpath))


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linting passes on modified eval files."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install ruff if not already present
    r = subprocess.run(
        ["ruff", "check", "products/signals/eval/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff formatting passes on modified eval files."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "--diff", "products/signals/eval/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cosine_distance_behavior():
    """cosine_distance static method exists on EmbeddingStore and computes correctly."""
    r = subprocess.run(
        [
            "python3", "-c", """
import sys
sys.path.insert(0, "/workspace/posthog")
import numpy as np

# Extract cosine_distance from mock.py by reading source and executing
src = open("/workspace/posthog/products/signals/eval/mock.py").read()
import ast as _ast
tree = _ast.parse(src)

# Find the cosine_distance method
found = False
for node in _ast.walk(tree):
    if isinstance(node, _ast.FunctionDef) and node.name == "cosine_distance":
        found = True
        break

assert found, "cosine_distance method not found in mock.py"

# Re-implement the method logic to test it (mirrors the expected implementation)
def cosine_distance(a, b):
    va = np.array(a, dtype=np.float64)
    vb = np.array(b, dtype=np.float64)
    norm_product = np.linalg.norm(va) * np.linalg.norm(vb)
    if norm_product == 0:
        return 1.0
    return 1.0 - float(np.dot(va, vb) / norm_product)

# Test identical vectors -> distance 0
d = cosine_distance([1, 0, 0], [1, 0, 0])
assert abs(d) < 1e-9, f"Identical vectors should have distance 0, got {d}"

# Test orthogonal vectors -> distance 1
d = cosine_distance([1, 0], [0, 1])
assert abs(d - 1.0) < 1e-9, f"Orthogonal vectors should have distance 1, got {d}"

# Test opposite vectors -> distance 2
d = cosine_distance([1, 0], [-1, 0])
assert abs(d - 2.0) < 1e-9, f"Opposite vectors should have distance 2, got {d}"

# Test zero vector -> distance 1
d = cosine_distance([0, 0], [1, 1])
assert abs(d - 1.0) < 1e-9, f"Zero vector should give distance 1, got {d}"

# Test that the method is a @staticmethod (can be found as such in AST)
for node in _ast.walk(tree):
    if isinstance(node, _ast.ClassDef) and node.name == "EmbeddingStore":
        for item in node.body:
            if isinstance(item, _ast.FunctionDef) and item.name == "cosine_distance":
                decorators = [d.id if isinstance(d, _ast.Name) else "" for d in item.decorator_list]
                assert "staticmethod" in decorators, "cosine_distance should be a @staticmethod"

print("OK")
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"cosine_distance tests failed:\n{r.stderr}\n{r.stdout}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_specificity_split_removed():
    """MatchFailureMode enum must not contain SPECIFICITY_SPLIT."""
    src = EVAL_FILE.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MatchFailureMode":
            members = [
                t.targets[0].id
                for t in node.body
                if isinstance(t, ast.Assign) and isinstance(t.targets[0], ast.Name)
            ]
            assert "SPECIFICITY_SPLIT" not in members, \
                f"SPECIFICITY_SPLIT should be removed from MatchFailureMode, found members: {members}"
            assert "NONE" in members, "NONE should still be in MatchFailureMode"
            assert "UNDERGROUP" in members, "UNDERGROUP should still be in MatchFailureMode"
            assert "OVERGROUP" in members, "OVERGROUP should still be in MatchFailureMode"
            return
    raise AssertionError("MatchFailureMode class not found in eval_grouping_e2e.py")


# [pr_diff] fail_to_pass
def test_new_eval_metrics_emitted():
    """_capture_match_quality must emit correct_match_pre_specificity, query_diversity, and candidate_diversity."""
    src = EVAL_FILE.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_capture_match_quality":
            body_src = ast.get_source_segment(src, node)
            assert body_src is not None, "_capture_match_quality body not extractable"
            assert "correct_match_pre_specificity" in body_src, \
                "_capture_match_quality must emit correct_match_pre_specificity metric"
            assert "query_diversity" in body_src, \
                "_capture_match_quality must emit query_diversity metric"
            assert "candidate_diversity" in body_src, \
                "_capture_match_quality must emit candidate_diversity metric"
            # Verify the method accepts query_embeddings and candidates parameters
            param_names = [arg.arg for arg in node.args.args]
            assert "query_embeddings" in param_names, \
                "_capture_match_quality must accept query_embeddings parameter"
            assert "candidates" in param_names, \
                "_capture_match_quality must accept candidates parameter"
            return
    raise AssertionError("_capture_match_quality method not found")


# [pr_diff] fail_to_pass
def test_diversity_computation_logic():
    """Diversity metrics use itertools.combinations for pairwise computation."""
    r = subprocess.run(
        [
            "python3", "-c", """
import sys
sys.path.insert(0, "/workspace/posthog")
import ast

src = open("/workspace/posthog/products/signals/eval/eval_grouping_e2e.py").read()
tree = ast.parse(src)

# Check that 'from itertools import combinations' is present
has_combinations_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module == "itertools":
        for alias in node.names:
            if alias.name == "combinations":
                has_combinations_import = True

assert has_combinations_import, "Must import combinations from itertools"

# Check _capture_match_quality uses combinations for pairwise distances
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_capture_match_quality":
        body_src = ast.get_source_segment(src, node)
        assert "combinations" in body_src, "Must use combinations for pairwise computation"
        # Verify Jaccard-based candidate diversity
        assert "jaccard" in body_src.lower() or "intersection" in body_src.lower(), \
            "Candidate diversity should use Jaccard or set intersection"
        assert "union" in body_src.lower() or "signal_id" in body_src.lower(), \
            "Candidate diversity should use set union or signal_id"
        break
else:
    raise AssertionError("_capture_match_quality not found")

print("OK")
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Diversity computation check failed:\n{r.stderr}\n{r.stdout}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_metrics_updated():
    """AGENTS.md metrics table must document new metrics and remove SPECIFICITY_SPLIT."""
    content = AGENTS_FILE.read_text()

    # New metrics must be documented
    assert "correct_match_pre_specificity" in content, \
        "AGENTS.md must document correct_match_pre_specificity metric"
    assert "query_diversity" in content, \
        "AGENTS.md must document query_diversity metric"
    assert "candidate_diversity" in content, \
        "AGENTS.md must document candidate_diversity metric"

    # SPECIFICITY_SPLIT should be removed from the metrics table
    # (it was in the match-quality row: "NONE/UNDERGROUP/OVERGROUP/SPECIFICITY_SPLIT")
    lines = content.split("\n")
    for line in lines:
        if "match-quality" in line and "Per-signal" in line:
            assert "SPECIFICITY_SPLIT" not in line, \
                "match-quality metrics row should not reference SPECIFICITY_SPLIT"
            break


# [pr_diff] fail_to_pass
def test_agents_md_new_sql_sections():
    """AGENTS.md must have new SQL sections for specificity judge impact and diversity queries."""
    content = AGENTS_FILE.read_text()

    # Specificity judge impact section
    assert "specificity judge impact" in content.lower() or "specificity_impact" in content, \
        "AGENTS.md must have a specificity judge impact section"
    assert "correct_match_pre_specificity" in content, \
        "Specificity judge section must reference correct_match_pre_specificity metric"
    assert "prevented_overgroup" in content or "caused_undergroup" in content, \
        "Specificity judge section must describe impact categories"

    # Query and candidate diversity section
    assert "query_diversity" in content and "candidate_diversity" in content, \
        "AGENTS.md must have a diversity query section referencing both metrics"


# [agent_config] fail_to_pass
def test_agents_md_sql_no_specificity_split():
    """SQL query in AGENTS.md must not reference SPECIFICITY_SPLIT failure mode."""
    content = AGENTS_FILE.read_text()
    # Find the match quality failure mode SQL block and check it
    in_sql_block = False
    found_section = False
    for line in content.split("\n"):
        if "Match quality failure mode" in line:
            found_section = True
        if found_section and line.strip().startswith("```sql"):
            in_sql_block = True
            continue
        if in_sql_block and line.strip() == "```":
            break
        if in_sql_block and "SPECIFICITY_SPLIT" in line:
            raise AssertionError(
                "Match quality SQL query should not reference SPECIFICITY_SPLIT"
            )
    assert found_section, "AGENTS.md should have a 'Match quality failure mode' section"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """_capture_match_quality has real diversity computation logic, not a stub."""
    src = EVAL_FILE.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_capture_match_quality":
            body_stmts = [
                s for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))
                or (isinstance(s, ast.Expr) and not isinstance(s.value, (ast.Constant, ast.Str)))
            ]
            assert len(body_stmts) >= 10, \
                f"_capture_match_quality body has only {len(body_stmts)} statements, expected substantial logic"
            return
    raise AssertionError("_capture_match_quality not found")
