"""
Task: transformers-use-docbuilder-runnable-example-for
Repo: huggingface/transformers @ bb8031052cbd88f8b30c75df84b9703eee80200f
PR:   44277

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    for rel in [
        "setup.py",
        "src/transformers/dependency_versions_table.py",
    ]:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(Path(REPO) / rel)],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, f"{rel} has syntax errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: setup.py / dependency
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docs_extra_defined():
    """setup.py must define an extras["docs"] entry."""
    setup_src = (Path(REPO) / "setup.py").read_text()
    assert 'extras["docs"]' in setup_src, (
        'setup.py should define extras["docs"] for doc-builder'
    )


# [pr_diff] fail_to_pass
def test_docs_extra_in_testing():
    """The testing extras must include the docs extra."""
    setup_src = (Path(REPO) / "setup.py").read_text()
    # Find the extras["testing"] definition block and check it references docs
    testing_match = re.search(
        r'extras\["testing"\]\s*=\s*\((.*?)\)',
        setup_src,
        re.DOTALL,
    )
    assert testing_match is not None, 'Could not find extras["testing"] in setup.py'
    testing_block = testing_match.group(1)
    assert 'extras["docs"]' in testing_block, (
        'extras["testing"] should include extras["docs"]'
    )


# [pr_diff] fail_to_pass
def test_dependency_table_uses_git_doc_builder():
    """dependency_versions_table.py must reference doc-builder via git+."""
    dep_table = (
        Path(REPO) / "src/transformers/dependency_versions_table.py"
    ).read_text()
    assert "git+https://github.com/huggingface/doc-builder" in dep_table, (
        "hf-doc-builder should use a git+ URL in the dependency table"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — doc example fixes in glmasr.md
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_glmasr_has_runnable_fences():
    """GLM-ASR doc must have code fences marked with runnable labels."""
    glmasr = (Path(REPO) / "docs/source/en/model_doc/glmasr.md").read_text()
    runnable_fences = re.findall(r"```py\s+runnable(?::(\w+))?", glmasr)
    assert len(runnable_fences) >= 3, (
        f"Expected at least 3 runnable code fences, found {len(runnable_fences)}"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CONTRIBUTING.md and testing.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — doc install command updated
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
