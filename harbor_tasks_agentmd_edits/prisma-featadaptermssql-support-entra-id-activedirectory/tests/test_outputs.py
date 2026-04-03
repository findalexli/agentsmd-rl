"""
Task: {{TASK_NAME}}
Repo: {{REPO}} @ {{BASE_COMMIT}}
PR:   {{PR_NUMBER}}

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/{{REPO_SHORT}}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass

# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass

# [pr_diff] fail_to_pass

# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass

# [static] pass_to_pass

    # TODO: check that modified function(s) have meaningful body
    # Example:
    #   src = Path(f"{REPO}/path/to/file.py").read_text()
    #   tree = ast.parse(src)
    #   for node in ast.walk(tree):
    #       if isinstance(node, ast.FunctionDef) and node.name == "target_func":
    #           stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
    #           assert len(stmts) >= 2, "Function body is a stub"
    raise NotImplementedError("Replace with anti-stub check")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — {{CONFIG_FILE}}:{{LINES}} @ {{COMMIT}}
