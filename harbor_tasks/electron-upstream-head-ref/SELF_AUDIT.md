# Self-Audit Report

## Summary

- **Tests**: 6 total (4 fail-to-pass, 2 pass-to-pass)
- **Stub score**: 0 (all tests must fail on stub)
- **Alternative fix passes**: Yes
- **Anti-patterns**: None detected
- **Manifest sync**: Yes

## Test Breakdown

### Fail-to-Pass Tests (will fail on base commit)

1. `test_upstream_head_has_hash_suffix` - Verifies UPSTREAM_HEAD format includes 8-char hash
2. `test_upstream_head_hash_matches_script_dir` - Verifies hash is derived from SCRIPT_DIR
3. `test_import_patches_updates_both_refs` - Verifies import_patches updates both new and legacy refs
4. `test_guess_base_commit_prefers_new_ref` - Verifies new ref is tried first

### Pass-to-Pass Tests (should pass on base and merge)

1. `test_legacy_ref_constant` - Verifies legacy ref constant is unchanged
2. `test_guess_base_commit_fallback_to_legacy` - Verifies fallback to legacy ref works

## Anti-Pattern Analysis

| Pattern | Status | Notes |
|---------|--------|-------|
| Self-referential constant extraction | Not present | Tests compare against hashlib computation, not hardcoded values |
| Import fallback to AST | Not present | Imports fail = test fails |
| Grep-only frontend tests | Not present | All tests execute Python code and verify return values |
| Stub-passable tests | Not present | All tests assert specific return values |
| Superficial guard checks | Not present | Tests assert state changed (ref values) |
| Single parameter value | Not present | Tests vary across multiple git operations |
| Ungated structural tests | Not present | All structural tests are behavioral |
| Compilation-ungated structural | N/A | Python project |
| Keyword stuffing | Not present | Tests check specific behavior |
| File-exists fallback | Not present | No existence checks |

## Eval Manifest Sync

All 6 test functions have corresponding `check` entries in `eval_manifest.yaml` with matching IDs:
- `test_upstream_head_has_hash_suffix` → `upstream_head_format`
- `test_upstream_head_hash_matches_script_dir` → `upstream_head_hash_correct`
- `test_legacy_ref_constant` → `legacy_ref_constant`
- `test_import_patches_updates_both_refs` → `import_patches_dual_update`
- `test_guess_base_commit_prefers_new_ref` → `guess_base_commit_new_ref`
- `test_guess_base_commit_fallback_to_legacy` → `guess_base_commit_fallback`

## Agent Config Analysis

From the config files analyzed:
- **CLAUDE.md**: Contains Python coding standards and project structure info
- **.github/copilot-instructions.md**: Contains build/test commands
- **docs/CLAUDE.md**: Documentation-specific guidance (not relevant to this task)

The task is in `script/lib/git.py` - a Python utility module. The configs emphasize:
1. Following existing patterns in the codebase
2. Using standard Python imports (hashlib)
3. Maintaining backwards compatibility

These are captured in the eval_manifest `agent_config` section.
