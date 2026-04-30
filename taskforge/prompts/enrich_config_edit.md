# Enrich Config Edit Tests

Add config file update tests to an existing agentmd-edit task that's missing them.

## Input

`$ARGUMENTS` = task name in `markdown_edits/` (e.g., `remix-add-charset-to-contenttype-for`)

## Context

This task was scaffolded from a PR that changed both code AND agent config files (README.md, CLAUDE.md, AGENTS.md, SKILL.md, etc.), but the scaffold didn't create proper tests for the config file changes.

## Steps

### 1. Understand the task

Read these files:
- `markdown_edits/$ARGUMENTS/instruction.md` — what the task asks
- `markdown_edits/$ARGUMENTS/solution/solve.sh` — the gold patch
- `markdown_edits/$ARGUMENTS/tests/test_outputs.py` — existing tests
- `markdown_edits/$ARGUMENTS/eval_manifest.yaml` — existing checks

### 2. Identify config file changes in the gold patch

Look at `solve.sh` and identify which config/doc files are modified:
- README.md, CLAUDE.md, AGENTS.md, SKILL.md, CONTRIBUTING.md, etc.
- What content was added/changed in those files?
- What is the semantic purpose of the change?

If the gold patch does NOT modify any config files, add a note to instruction.md saying the agent should also update the relevant config file, and add the config file change to solve.sh.

### 3. Add config_edit tests to test_outputs.py

Add at least ONE test that verifies the config file was updated correctly:

```python
def test_readme_documents_new_feature():
    """README.md must document the new X feature."""
    readme = Path(REPO) / "path/to/README.md"
    content = readme.read_text()
    # Check semantic content, not exact wording
    assert "key_concept" in content.lower(), "README should mention key_concept"
    assert "api_name" in content or "function_name" in content, \
        "README should reference the new API"
```

**Design rules:**
1. Check semantic content, not exact wording
2. Must fail on base commit, pass after gold patch
3. Check 2-3 key terms/concepts from the config change
4. Don't check formatting or exact position

### 4. Update eval_manifest.yaml

Add matching check entries. Use `origin: agent_config` if an existing rule in CLAUDE.md/AGENTS.md requires the doc update (and point `source` to that rule). Otherwise use `origin: pr_diff`:

```yaml
  # If driven by a rule in AGENTS.md:
  - id: readme_documents_new_feature
    type: fail_to_pass
    origin: agent_config
    description: "README.md updated to document new feature"
    source:
      path: "AGENTS.md"              # the file with the rule, NOT the file being edited
      lines: "21"
      commit: "base_commit_sha"

  # If just part of the PR change (no pre-existing rule):
  - id: claude_md_adds_lint_rule
    type: fail_to_pass
    origin: pr_diff
    description: "CLAUDE.md adds the new lint rule"
```

### 5. Remove any remaining placeholders

If `test_config_rule` with `NotImplementedError` still exists, remove it.

### 6. Update instruction.md if needed

If the instruction doesn't mention updating config files, add a sentence like:
"After making the code changes, update the relevant documentation to reflect the new behavior."

### 7. Verify

- The new test references a file that exists in the repo at base commit
- The test would fail before the config change and pass after
- The eval_manifest.yaml is in sync with test_outputs.py
