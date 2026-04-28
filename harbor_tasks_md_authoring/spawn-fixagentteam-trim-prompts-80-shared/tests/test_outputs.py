"""Behavioral checks for spawn-fixagentteam-trim-prompts-80-shared (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spawn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/_shared-rules.md')
    assert 'For proactive work: default outcome is "nothing to do, shut down." Override only if something is actually broken or vulnerable. Do NOT create proactive PRs for: style-only changes, adding comments/doc' in text, "expected to find: " + 'For proactive work: default outcome is "nothing to do, shut down." Override only if something is actually broken or vulnerable. Do NOT create proactive PRs for: style-only changes, adding comments/doc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/_shared-rules.md')
    assert 'Before posting ANY comment on a PR or issue, check for existing signatures from the same team. Never duplicate acknowledgments, status updates, or re-triages. Only comment with genuinely new informati' in text, "expected to find: " + 'Before posting ANY comment on a PR or issue, check for existing signatures from the same team. Never duplicate acknowledgments, status updates, or re-triages. Only comment with genuinely new informati'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/_shared-rules.md')
    assert 'Before ANY PR: `gh pr list --repo OpenRouterTeam/spawn --state open` and `--state closed --limit 20`. If a similar PR exists (open or recently closed), do not create another. Closed-without-merge mean' in text, "expected to find: " + 'Before ANY PR: `gh pr list --repo OpenRouterTeam/spawn --state open` and `--state closed --limit 20`. If a similar PR exists (open or recently closed), do not create another. Closed-without-merge mean'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/discovery-team-prompt.md')
    assert 'Research new cloud/sandbox providers. Criteria: prestige or unbeatable pricing (beat Hetzner ~€3.29/mo), public REST API/CLI, SSH/exec access. NO GPU clouds. Check manifest.json + existing proposals f' in text, "expected to find: " + 'Research new cloud/sandbox providers. Criteria: prestige or unbeatable pricing (beat Hetzner ~€3.29/mo), public REST API/CLI, SSH/exec access. NO GPU clouds. Check manifest.json + existing proposals f'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/discovery-team-prompt.md')
    assert 'gh api graphql -f query=\'{ repository(owner: "OpenRouterTeam", name: "spawn") { issues(states: OPEN, labels: ["cloud-proposal", "agent-proposal"], first: 50) { nodes { number title labels(first: 5) { ' in text, "expected to find: " + 'gh api graphql -f query=\'{ repository(owner: "OpenRouterTeam", name: "spawn") { issues(states: OPEN, labels: ["cloud-proposal", "agent-proposal"], first: 50) { nodes { number title labels(first: 5) { '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/discovery-team-prompt.md')
    assert 'Research best skills, MCP servers, and configs per agent in manifest.json. For each agent: check for skill standards, community skills, useful MCP servers, agent-specific configs, prerequisites. Verif' in text, "expected to find: " + 'Research best skills, MCP servers, and configs per agent in manifest.json. For each agent: check for skill standards, community skills, useful MCP servers, agent-specific configs, prerequisites. Verif'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/qa-quality-prompt.md')
    assert '`TeamCreate` with team name matching the env. Spawn 5 teammates in parallel. For each, read `.claude/skills/setup-agent-team/teammates/qa-{name}.md` for their full protocol — copy it into their prompt' in text, "expected to find: " + '`TeamCreate` with team name matching the env. Spawn 5 teammates in parallel. For each, read `.claude/skills/setup-agent-team/teammates/qa-{name}.md` for their full protocol — copy it into their prompt'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/qa-quality-prompt.md')
    assert 'Mission: Run tests, E2E validation, remove duplicate/theatrical tests, enforce code quality, keep README.md in sync.' in text, "expected to find: " + 'Mission: Run tests, E2E validation, remove duplicate/theatrical tests, enforce code quality, keep README.md in sync.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/qa-quality-prompt.md')
    assert 'Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules. Those rules are binding.' in text, "expected to find: " + 'Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules. Those rules are binding.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/refactor-team-prompt.md')
    assert 'Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules (Off-Limits, Diminishing Returns, Dedup, PR Justification, Worktrees, Commit Markers, Monitor Loop, Shutdown, Comment Dedup, ' in text, "expected to find: " + 'Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules (Off-Limits, Diminishing Returns, Dedup, PR Justification, Worktrees, Commit Markers, Monitor Loop, Shutdown, Comment Dedup, '[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/refactor-team-prompt.md')
    assert 'Refactor team creates PRs — security team reviews/closes/merges them. NEVER `gh pr review --approve` or `--request-changes`. NEVER `gh pr close` (exception: superseding with a new PR). MAY `gh pr merg' in text, "expected to find: " + 'Refactor team creates PRs — security team reviews/closes/merges them. NEVER `gh pr review --approve` or `--request-changes`. NEVER `gh pr close` (exception: superseding with a new PR). MAY `gh pr merg'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/refactor-team-prompt.md')
    assert 'Reject proactive plans with vague justifications, targeting working code, duplicating existing PRs, touching off-limits files, or adding tests that re-implement source functions inline.' in text, "expected to find: " + 'Reject proactive plans with vague justifications, targeting working code, duplicating existing PRs, touching off-limits files, or adding tests that re-implement source functions inline.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/security-review-all-prompt.md')
    assert '2. Spawn **pr-reviewer** (Sonnet) per non-draft PR, named `pr-reviewer-NUMBER`. Read `.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md` for the COMPLETE review protocol — copy it into' in text, "expected to find: " + '2. Spawn **pr-reviewer** (Sonnet) per non-draft PR, named `pr-reviewer-NUMBER`. Read `.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md` for the COMPLETE review protocol — copy it into'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/security-review-all-prompt.md')
    assert '3. Spawn **issue-checker** (google/gemini-3-flash-preview). Read `.claude/skills/setup-agent-team/teammates/security-issue-checker.md` for protocol.' in text, "expected to find: " + '3. Spawn **issue-checker** (google/gemini-3-flash-preview). Read `.claude/skills/setup-agent-team/teammates/security-issue-checker.md` for protocol.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/security-review-all-prompt.md')
    assert '4. If ≤5 open PRs, also spawn **scanner** (Sonnet). Read `.claude/skills/setup-agent-team/teammates/security-scanner.md` for protocol.' in text, "expected to find: " + '4. If ≤5 open PRs, also spawn **scanner** (Sonnet). Read `.claude/skills/setup-agent-team/teammates/security-scanner.md` for protocol.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-code-quality.md')
    assert 'Fix each finding. Run `bash -n` on modified .sh, `bun test` for .ts. If changes made: commit, push, open PR "refactor: Remove dead code and stale references". Sign-off: `-- qa/code-quality`' in text, "expected to find: " + 'Fix each finding. Run `bash -n` on modified .sh, `bun test` for .ts. If changes made: commit, push, open PR "refactor: Remove dead code and stale references". Sign-off: `-- qa/code-quality`'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-code-quality.md')
    assert '- **Python usage**: any `python3 -c` or `python -c` in shell scripts → replace with `bun -e` or `jq`' in text, "expected to find: " + '- **Python usage**: any `python3 -c` or `python -c` in shell scripts → replace with `bun -e` or `jq`'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-code-quality.md')
    assert '- **Dead code**: functions in `sh/shared/*.sh` or `packages/cli/src/` never called → remove' in text, "expected to find: " + '- **Dead code**: functions in `sh/shared/*.sh` or `packages/cli/src/` never called → remove'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-dedup-scanner.md')
    assert 'For each finding: fix (consolidate, rewrite, or remove). Run `bun test` to verify. If changes made: commit, push, open PR "test: Remove duplicate and theatrical tests". Report: duplicates found, remov' in text, "expected to find: " + 'For each finding: fix (consolidate, rewrite, or remove). Run `bun test` to verify. If changes made: commit, push, open PR "test: Remove duplicate and theatrical tests". Report: duplicates found, remov'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-dedup-scanner.md')
    assert '- **Bash-grep tests**: tests using `type FUNCTION_NAME` or grepping function body instead of calling it → rewrite as real unit tests' in text, "expected to find: " + '- **Bash-grep tests**: tests using `type FUNCTION_NAME` or grepping function body instead of calling it → rewrite as real unit tests'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-dedup-scanner.md')
    assert '- **Always-pass patterns**: conditional expects like `if (cond) { expect(...) } else { skip }` → make deterministic or remove' in text, "expected to find: " + '- **Always-pass patterns**: conditional expects like `if (cond) { expect(...) } else { skip }` → make deterministic or remove'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-e2e-tester.md')
    assert '- **Provision failure**: check stderr log, read `{cloud}.ts`, `agent-setup.ts`, `sh/e2e/lib/provision.sh`' in text, "expected to find: " + '- **Provision failure**: check stderr log, read `{cloud}.ts`, `agent-setup.ts`, `sh/e2e/lib/provision.sh`'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-e2e-tester.md')
    assert '- **Verification failure**: SSH into VM, check binary paths/env vars in `manifest.json` and `verify.sh`' in text, "expected to find: " + '- **Verification failure**: SSH into VM, check binary paths/env vars in `manifest.json` and `verify.sh`'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-e2e-tester.md')
    assert '5. Fix in worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/e2e-tester -b qa/e2e-fix origin/main`' in text, "expected to find: " + '5. Fix in worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/e2e-tester -b qa/e2e-fix origin/main`'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-record-keeper.md')
    assert '**Gate 3 — Troubleshooting gaps**: Fetch `gh issue list --limit 30 --state all`, cluster by similar problem. Triggers ONLY when: same problem in 2+ issues, clear actionable fix, AND fix not already in' in text, "expected to find: " + '**Gate 3 — Troubleshooting gaps**: Fetch `gh issue list --limit 30 --state all`, cluster by similar problem. Triggers ONLY when: same problem in 2+ issues, clear actionable fix, AND fix not already in'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-record-keeper.md')
    assert '**Gate 1 — Matrix drift**: Compare `manifest.json` (agents, clouds, matrix) against README matrix table + tagline counts. Triggers when agent/cloud added/removed, matrix status flipped, or counts wron' in text, "expected to find: " + '**Gate 1 — Matrix drift**: Compare `manifest.json` (agents, clouds, matrix) against README matrix table + tagline counts. Triggers when agent/cloud added/removed, matrix status flipped, or counts wron'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-record-keeper.md')
    assert '**Gate 2 — Commands drift**: Compare `packages/cli/src/commands/help.ts` → `getHelpUsageSection()` against README commands table. Triggers when a command exists in code but not README, or vice versa.' in text, "expected to find: " + '**Gate 2 — Commands drift**: Compare `packages/cli/src/commands/help.ts` → `getHelpUsageSection()` against README commands table. Triggers when a command exists in code but not README, or vice versa.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-test-runner.md')
    assert '3. If tests fail: read failing test + source, determine if test or source is wrong, fix, re-run. If still failing after 2 attempts, report and stop.' in text, "expected to find: " + '3. If tests fail: read failing test + source, determine if test or source is wrong, fix, re-run. If still failing after 2 attempts, report and stop.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-test-runner.md')
    assert '1. Worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/test-runner -b qa/test-runner origin/main`' in text, "expected to find: " + '1. Worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/test-runner -b qa/test-runner origin/main`'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/qa-test-runner.md')
    assert '6. If changes made: commit, push, open PR (NOT draft) "fix: Fix failing tests"' in text, "expected to find: " + '6. If changes made: commit, push, open PR (NOT draft) "fix: Fix failing tests"'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-code-health.md')
    assert 'Best match for `bug` labeled issues. Proactive: post-merge consistency sweep + gap detection. ONE PR max.' in text, "expected to find: " + 'Best match for `bug` labeled issues. Proactive: post-merge consistency sweep + gap detection. ONE PR max.'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-code-health.md')
    assert 'Reliability, dead code, inconsistency. Pick top 3 findings, fix in ONE PR. Run tests after every change.' in text, "expected to find: " + 'Reliability, dead code, inconsistency. Pick top 3 findings, fix in ONE PR. Run tests after every change.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-code-health.md')
    assert '- Find half-migrated code (e.g., one function uses Result helpers, next still uses raw try/catch)' in text, "expected to find: " + '- Find half-migrated code (e.g., one function uses Result helpers, next still uses raw try/catch)'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md')
    assert '- **Strict dedup**: if `-- refactor/community-coordinator` exists in any comment, only comment again for NEW PR links or concrete resolutions' in text, "expected to find: " + '- **Strict dedup**: if `-- refactor/community-coordinator` exists in any comment, only comment again for NEW PR links or concrete resolutions'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md')
    assert '- Acknowledge once, categorize (bug/feature/question), then **immediately delegate to a teammate for fixing** — do not just acknowledge' in text, "expected to find: " + '- Acknowledge once, categorize (bug/feature/question), then **immediately delegate to a teammate for fixing** — do not just acknowledge'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md')
    assert 'Manage open issues. Fetch: `gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,body,labels,createdAt`' in text, "expected to find: " + 'Manage open issues. Fetch: `gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,body,labels,createdAt`'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-complexity-hunter.md')
    assert 'Proactive scan: find functions >50 lines (bash) or >80 lines (ts), refactor top 2-3 by extracting helpers. ONE PR max. Run tests after every change.' in text, "expected to find: " + 'Proactive scan: find functions >50 lines (bash) or >80 lines (ts), refactor top 2-3 by extracting helpers. ONE PR max. Run tests after every change.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-complexity-hunter.md')
    assert 'Best match for `maintenance` labeled issues.' in text, "expected to find: " + 'Best match for `maintenance` labeled issues.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-complexity-hunter.md')
    assert '# complexity-hunter (Sonnet)' in text, "expected to find: " + '# complexity-hunter (Sonnet)'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md')
    assert 'First: `gh pr list --repo OpenRouterTeam/spawn --state open --json number,title,headRefName,updatedAt,mergeable,reviewDecision,isDraft`' in text, "expected to find: " + 'First: `gh pr list --repo OpenRouterTeam/spawn --state open --json number,title,headRefName,updatedAt,mergeable,reviewDecision,isDraft`'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md')
    assert 'For EACH PR, fetch full context (comments + reviews). Read ALL comments — they contain decisions and scope changes.' in text, "expected to find: " + 'For EACH PR, fetch full context (comments + reviews). Read ALL comments — they contain decisions and scope changes.'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md')
    assert '- **Stale non-draft (3+ days, no review)** → check out in worktree, continue work, push, comment.' in text, "expected to find: " + '- **Stale non-draft (3+ days, no review)** → check out in worktree, continue work, push, comment.'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-security-auditor.md')
    assert 'Proactive scan: `.sh` files for command injection, path traversal, credential leaks, unsafe eval/source. `.ts` files for XSS, prototype pollution, auth bypass. Fix findings in ONE PR. Run `bash -n` an' in text, "expected to find: " + 'Proactive scan: `.sh` files for command injection, path traversal, credential leaks, unsafe eval/source. `.ts` files for XSS, prototype pollution, auth bypass. Fix findings in ONE PR. Run `bash -n` an'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-security-auditor.md')
    assert 'Best match for `security` labeled issues.' in text, "expected to find: " + 'Best match for `security` labeled issues.'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-security-auditor.md')
    assert '# security-auditor (Sonnet)' in text, "expected to find: " + '# security-auditor (Sonnet)'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-style-reviewer.md')
    assert '3. TypeScript vs `.claude/rules/type-safety.md`: no `as` assertions (except `as const`), no `require()`/`module.exports`, no manual multi-level typeguards (use valibot), no `vitest`' in text, "expected to find: " + '3. TypeScript vs `.claude/rules/type-safety.md`: no `as` assertions (except `as const`), no `require()`/`module.exports`, no manual multi-level typeguards (use valibot), no `vitest`'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-style-reviewer.md')
    assert '2. Shell scripts vs `.claude/rules/shell-scripts.md`: no `echo -e`, no `source <(cmd)`, no `((var++))` with `set -e`, no `set -u`, no `python3 -c`, no relative source paths' in text, "expected to find: " + '2. Shell scripts vs `.claude/rules/shell-scripts.md`: no `echo -e`, no `source <(cmd)`, no `((var++))` with `set -e`, no `set -u`, no `python3 -c`, no relative source paths'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-style-reviewer.md')
    assert '4. Tests vs `.claude/rules/testing.md`: no `homedir` from `node:os`, no subprocess spawning, tests must import real source' in text, "expected to find: " + '4. Tests vs `.claude/rules/testing.md`: no `homedir` from `node:os`, no subprocess spawning, tests must import real source'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-test-engineer.md')
    assert '- **NEVER copy-paste functions into test files.** Every test MUST import from the real source module. If a function is not exported, do NOT test it — do not re-implement it inline.' in text, "expected to find: " + '- **NEVER copy-paste functions into test files.** Every test MUST import from the real source module. If a function is not exported, do NOT test it — do not re-implement it inline.'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-test-engineer.md')
    assert '- **Maximum 1 new test file per cycle.** Before writing ANY test, verify: (1) function is exported, (2) not already tested, (3) test will actually fail if source breaks.' in text, "expected to find: " + '- **Maximum 1 new test file per cycle.** Before writing ANY test, verify: (1) function is exported, (2) not already tested, (3) test will actually fail if source breaks.'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-test-engineer.md')
    assert "- **NEVER create tests that pass without the source code.** If a test doesn't break when the real implementation changes, it is worthless." in text, "expected to find: " + "- **NEVER create tests that pass without the source code.** If a test doesn't break when the real implementation changes, it is worthless."[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-ux-engineer.md')
    assert 'Proactive scan: test end-to-end flows, improve error messages, fix UX papercuts. Focus on onboarding friction (prompts, labels, help text). ONE PR max.' in text, "expected to find: " + 'Proactive scan: test end-to-end flows, improve error messages, fix UX papercuts. Focus on onboarding friction (prompts, labels, help text). ONE PR max.'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-ux-engineer.md')
    assert 'Best match for `cli` or UX-related issues.' in text, "expected to find: " + 'Best match for `cli` or UX-related issues.'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/refactor-ux-engineer.md')
    assert '# ux-engineer (Sonnet)' in text, "expected to find: " + '# ux-engineer (Sonnet)'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-issue-checker.md')
    assert '- **Strict dedup**: if `-- security/issue-checker` or `-- security/triage` exists in ANY comment → SKIP unless new human comments posted after the last security sign-off' in text, "expected to find: " + '- **Strict dedup**: if `-- security/issue-checker` or `-- security/triage` exists in ANY comment → SKIP unless new human comments posted after the last security sign-off'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-issue-checker.md')
    assert '- **NEVER** post status updates, re-triages, or acknowledgment-only follow-ups. ONE triage comment per issue, EVER.' in text, "expected to find: " + '- **NEVER** post status updates, re-triages, or acknowledgment-only follow-ups. ONE triage comment per issue, EVER.'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-issue-checker.md')
    assert '`gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,labels,updatedAt,comments`' in text, "expected to find: " + '`gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,labels,updatedAt,comments`'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md')
    assert 'Every changed file: command injection, credential leaks, path traversal, XSS/injection, unsafe eval/source, curl|bash safety, macOS bash 3.x compat. Record each finding: `path`, `line`, `start_line` (' in text, "expected to find: " + 'Every changed file: command injection, credential leaks, path traversal, XSS/injection, unsafe eval/source, curl|bash safety, macOS bash 3.x compat. Record each finding: `path`, `line`, `start_line` ('[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md')
    assert 'If `updatedAt` > 48h AND `mergeable` CONFLICTING → file follow-up issue if valid work, close PR. If > 48h but no conflicts → proceed. If fresh → proceed.' in text, "expected to find: " + 'If `updatedAt` > 48h AND `mergeable` CONFLICTING → file follow-up issue if valid work, close PR. If > 48h but no conflicts → proceed. If fresh → proceed.'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md')
    assert '"body": "## Security Review\\n**Verdict**: ...\\n**Commit**: ${HEAD_SHA}\\n### Findings\\n...\\n### Tests\\n...\\n---\\n*-- security/pr-reviewer*",' in text, "expected to find: " + '"body": "## Security Review\\n**Verdict**: ...\\n**Commit**: ${HEAD_SHA}\\n### Findings\\n...\\n### Tests\\n...\\n---\\n*-- security/pr-reviewer*",'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-scanner.md')
    assert 'File CRITICAL/HIGH findings as individual GitHub issues (dedup first: `gh issue list --state open --label security`). Report all findings to team lead.' in text, "expected to find: " + 'File CRITICAL/HIGH findings as individual GitHub issues (dedup first: `gh issue list --state open --label security`). Report all findings to team lead.'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-scanner.md')
    assert 'For `.sh` files: command injection, credential leaks, path traversal, unsafe eval/source, curl|bash safety, macOS bash 3.x compat.' in text, "expected to find: " + 'For `.sh` files: command injection, credential leaks, path traversal, unsafe eval/source, curl|bash safety, macOS bash 3.x compat.'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/teammates/security-scanner.md')
    assert 'Scan files changed in the last 24 hours for security issues. Spawned only when ≤5 open PRs.' in text, "expected to find: " + 'Scan files changed in the last 24 hours for security issues. Spawned only when ≤5 open PRs.'[:80]

