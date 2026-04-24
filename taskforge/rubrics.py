"""Single source of truth for task-quality rubrics.

Drawn from:
  - Harbor's 8 built-in criteria (anthropic/harbor)
  - SWE-bench Verified §3.2 (OpenAI)
  - SWE-bench+ (arXiv 2410.06992) — solution leakage
  - PatchDiff (arXiv 2503.15223) — non-functional tests, tautological passes, regressions
  - Terminal-Bench 2.0 — adversarial exploit detection, sandbox determinism
  - Docker reproducibility study (arXiv 2602.17678)
  - SWE-smith review protocol — f2p/p2p classification

Each Rubric is consumed by:
  - scaffold.md prompt checklist (agent self-check at scaffold time)
  - task_lint.py (deterministic regex/grep checks at qgate time)
  - node_quality_judge (LLM judge at post-validate time)
  - retrofit script (batch audit of existing tasks)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Tier = Literal["A", "B", "C"]          # A=reward-integrity killer, B=important, C=hygiene
Verification = Literal["programmatic", "llm_judge", "both"]


@dataclass(frozen=True)
class Rubric:
    name: str                          # snake_case, ≤40 chars, used as key
    tier: Tier
    description: str                   # one sentence
    artifacts: tuple[str, ...]         # files to inspect
    verification: Verification
    source: str                        # citation (paper/benchmark)
    failure_example: str = ""          # concrete symptom in our 1087-task audit
    # LLM judge prompt shown to the model when this rubric is scored
    judge_prompt: str = ""


RUBRICS: tuple[Rubric, ...] = (
    # ═══════════════════════ Tier A — RL reward-integrity killers ═══════════════════════
    Rubric(
        name="behavior_in_task_description",
        tier="A",
        description=(
            "Every behavior test_outputs.py asserts on MUST be derivable from instruction.md. "
            "File paths, function names, SHAs, schema keys, literal strings the tests expect — "
            "all must be named in the instruction or cited to an authoritative source."
        ),
        artifacts=("instruction.md", "tests/test_outputs.py"),
        verification="llm_judge",
        source="Harbor #1",
        failure_example=(
            "76% of 1087 tasks failed this in Opus audit: tests grep for '4acc9acc76...' but "
            "instruction only says 'install rustup with SHA256 verification'"
        ),
        judge_prompt=(
            "For every test function, identify each assert'd file path, function name, SHA, "
            "literal string, or schema key. Does instruction.md name each of these (or cite "
            "an authoritative external source that provides them)? FAIL if any test specific "
            "is undiscoverable from the instruction."
        ),
    ),
    Rubric(
        name="no_solution_leakage",
        tier="A",
        description=(
            "instruction.md describes the *symptom* of the bug, not the fix itself. The exact "
            "patch code, diagnostic conclusion, or buggy-line-number must not be copy-pasteable."
        ),
        artifacts=("instruction.md",),
        verification="llm_judge",
        source="SWE-bench+ §4 (arXiv 2410.06992)",
        failure_example="instruction.md contains the exact diff snippet the agent is supposed to write",
        judge_prompt=(
            "Would a competent developer reading ONLY instruction.md still have to reason about "
            "WHAT to change? FAIL if the instruction states the fix (e.g., 'change line 42 to "
            "X', 'replace foo() with bar()'). PASS if it only describes what's broken."
        ),
    ),
    Rubric(
        name="solution_uniqueness_guard",
        tier="A",
        description=(
            "Tests accept ANY behaviorally-correct fix, not only the gold patch's exact "
            "implementation. No assertions on internal structure unique to gold."
        ),
        artifacts=("tests/test_outputs.py", "solution/solve.sh"),
        verification="llm_judge",
        source="SWE-bench Verified §3.2",
        failure_example=(
            "29.6% of plausible patches in SWE-bench diverge from gold yet are correct; "
            "tests that hardcode gold's variable names reject them"
        ),
        judge_prompt=(
            "Consider three alternative correct fixes the agent might write. Would each still "
            "pass test_outputs.py? FAIL if tests assert on gold-specific variable names, exact "
            "line positions, specific internal helper functions, or implementation details that "
            "a correct alternative fix wouldn't share."
        ),
    ),
    Rubric(
        name="tests_verify_behavior_not_text",
        tier="A",
        description=(
            "Tests invoke the API / run the code / compile. They don't just grep for literal "
            "strings in source files. No pure-text-match assertions."
        ),
        artifacts=("tests/test_outputs.py",),
        verification="both",
        source="PatchDiff (arXiv 2503.15223); Terminal-Bench 2.0",
        failure_example="7.8% of SWE-bench 'solves' are really test-format wins, not fixes",
        judge_prompt=(
            "Do tests import and CALL the code, execute subprocesses, or inspect behavior? "
            "FAIL if every test is `assert 'foo' in open(path).read()` with no execution."
        ),
    ),
    Rubric(
        name="test_not_tautological",
        tier="A",
        description=(
            "No test passes on an empty implementation, `pass`, or `return None`. "
            "Each fail_to_pass genuinely constrains behavior."
        ),
        artifacts=("tests/test_outputs.py", "solution/solve.sh"),
        verification="llm_judge",
        source="PatchDiff §4 (arXiv 2503.15223)",
        failure_example="test asserts `result is not None` which passes for any non-None return",
        judge_prompt=(
            "For each f2p test, could a stub implementation (always returns default value, "
            "pass, return None, return empty collection) pass this test? FAIL if any f2p can "
            "be satisfied without implementing the bug fix."
        ),
    ),
    Rubric(
        name="pass_to_pass_coverage",
        tier="A",
        description=(
            "Task includes ≥1 pass_to_pass check guarding against regressions — "
            "functionality the agent could break while 'fixing' the bug."
        ),
        artifacts=("tests/test_outputs.py", "eval_manifest.yaml"),
        verification="programmatic",
        source="PatchDiff §4.3 (14.3% of wrong patches were regressive); SWE-smith protocol",
        failure_example="task has only f2p tests — agent can delete the failing code path and 'win'",
    ),
    # REMOVED 2026-04-15: `anti_cheating_measures` was over-flagging (~98% FAIL)
    # because Opus assumed the agent could read /solution/ at runtime. Harbor's
    # actual evaluation architecture mounts /solution/ ONLY during gold validation,
    # never during agent execution — the agent container cannot see it. The real
    # residual threat (Dockerfile COPY solution/ baking the answer into the image)
    # is already caught programmatically by `no_hidden_solution_artifacts`.
    Rubric(
        name="no_hidden_solution_artifacts",
        tier="A",
        description=(
            "solution/ is NOT COPY'd into the image. Build context excludes solution/ and tests/. "
            "Dockerfile has no references to solve.sh. `find / -name 'solve*'` turns up nothing."
        ),
        artifacts=("environment/Dockerfile", ".dockerignore"),
        verification="programmatic",
        source="Terminal-Bench 2.0 adversarial-exploit detection",
        failure_example="Dockerfile has `COPY solution/ /opt/solution/` — agent greps and wins",
    ),

    # ═══════════════════════════ Tier B — important ═══════════════════════════
    Rubric(
        name="dockerfile_determinism",
        tier="B",
        description=(
            "Base image pinned (ideally by digest or at minimum exact tag, NEVER `:latest`). "
            "apt/pip versions pinned. No `curl | bash` of a moving target. Build is reproducible."
        ),
        artifacts=("environment/Dockerfile",),
        verification="programmatic",
        source="arXiv 2602.17678; Terminal-Bench validator",
        failure_example="`FROM python:latest` or `pip install torch` with no ==X.Y.Z",
    ),
    Rubric(
        name="no_network_during_tests",
        tier="B",
        description=(
            "test.sh and test_outputs.py run fully offline. All deps baked into image. "
            "No pip/npm/apt/curl/git at TEST time — only at BUILD time."
        ),
        artifacts=("tests/test.sh", "tests/test_outputs.py"),
        verification="programmatic",
        source="BigCodeBench §3.1; Terminal-Bench sandbox spec",
        failure_example="test.sh does `pip install pytest` — network flake → reward noise",
    ),
    Rubric(
        name="pinned_dependencies",
        tier="B",
        description="All Python pip deps in Dockerfile are version-pinned (==X.Y.Z). apt OK.",
        artifacts=("environment/Dockerfile",),
        verification="programmatic",
        source="Harbor #6",
        failure_example="57% of 1087 tasks failed this in Opus audit",
    ),
    Rubric(
        name="f2p_p2p_classification_correct",
        tier="B",
        description=(
            "Every check tagged as fail_to_pass truly fails at base_commit and passes at gold. "
            "Every pass_to_pass truly passes at BOTH base and gold."
        ),
        artifacts=("eval_manifest.yaml", "tests/test_outputs.py"),
        verification="programmatic",
        source="SWE-smith review protocol",
    ),

    # ═══════════════════════════ Tier C — hygiene ═══════════════════════════
    Rubric(
        name="behavior_in_tests",
        tier="C",
        description="All behavior explicitly required by instruction.md is actually tested.",
        artifacts=("instruction.md", "tests/test_outputs.py"),
        verification="llm_judge",
        source="Harbor #2",
    ),
    Rubric(
        name="informative_test_structure",
        tier="C",
        description="Tests are grouped, named, or commented — not a flat unstructured blob.",
        artifacts=("tests/test_outputs.py",),
        verification="llm_judge",
        source="Harbor #3",
    ),
    Rubric(
        name="structured_data_schema",
        tier="C",
        description=(
            "If task produces structured data (JSON/CSV/API/DB), exact schema is documented "
            "in instruction.md or cited spec. N/A otherwise."
        ),
        artifacts=("instruction.md", "tests/test_outputs.py"),
        verification="llm_judge",
        source="Harbor #5",
    ),
    Rubric(
        name="no_typos",
        tier="C",
        description="No typos in filenames, paths, commands, or variable names.",
        artifacts=("instruction.md", "tests/test_outputs.py", "environment/Dockerfile"),
        verification="llm_judge",
        source="Harbor #7",
    ),
    Rubric(
        name="tests_or_solution_in_image",
        tier="C",
        description=(
            "Dockerfile does NOT COPY tests/ or solution/ into the image. Harness mounts "
            "tests/ externally at run time."
        ),
        artifacts=("environment/Dockerfile",),
        verification="programmatic",
        source="Harbor #8",
    ),
    Rubric(
        name="difficulty_calibrated",
        tier="C",
        description=(
            "task.toml has a difficulty tier consistent with observable signals "
            "(LOC changed, files touched, subprocess counts)."
        ),
        artifacts=("task.toml", "solution/solve.sh"),
        verification="programmatic",
        source="SWE-bench Verified annotator protocol",
    ),
    Rubric(
        name="instruction_no_hint_leakage",
        tier="C",
        description=(
            "instruction.md doesn't name the exact buggy line/file unless that file is already "
            "obvious from the task domain (e.g., 'the logger module' is fine; 'line 42 of "
            "logger/emit.py' is leakage when localization is part of the task)."
        ),
        artifacts=("instruction.md",),
        verification="llm_judge",
        source="SWE-bench+ §4; distinct from no_solution_leakage (this is about LOCALIZATION)",
    ),
    Rubric(
        name="config_edit_scope_bounded",
        tier="C",
        description=(
            "For agentmd-edits tasks: gold config diff is localized (not full-file rewrite) and "
            "doesn't contradict other Tier-1 files. N/A for code-only tasks."
        ),
        artifacts=("solution/solve.sh", "eval_manifest.yaml"),
        verification="llm_judge",
        source="Our own 4-track architecture",
    ),

    # ═════ Tier A — programmatic gates added 2026-04-24 from 50-task audit ═════
    Rubric(
        name="oracle_no_external_fetch",
        tier="A",
        description=(
            "solve.sh must contain the gold patch inline. It must not curl/wget/git-show/"
            "gh-pr-diff to fetch the fix from an external source — the agent could do "
            "the same and trivially game the oracle."
        ),
        artifacts=("solution/solve.sh",),
        verification="programmatic",
        source="Harbor audit 2026-04-24 (15/1117 tasks = 1.3% broken oracles)",
        failure_example=(
            "airflow-worker-serviceaccount-split: solve.sh does "
            "`curl -sL github.com/apache/airflow/pull/64730.diff | git apply -`"
        ),
    ),
    Rubric(
        name="tests_have_subprocess",
        tier="A",
        description=(
            "tests/test_outputs.py must contain at least one real subprocess invocation "
            "(subprocess.run / check_output / Popen / os.system) that executes the "
            "fixed code. Grep-only tests may supplement but never stand alone."
        ),
        artifacts=("tests/test_outputs.py",),
        verification="programmatic",
        source="Harbor audit 2026-04-24 (6% grep-only tests in random sample)",
        failure_example=(
            "areal-rpc-error-response-key: all tests only regex-search for .get() "
            "patterns in source — no runtime verification"
        ),
    ),
    Rubric(
        name="gold_diff_non_trivial",
        tier="A",
        description=(
            "Gold patch must be non-trivial: ≥15 non-whitespace added lines, OR touch a "
            "non-docs code file. Docs/CHANGELOG/README-only patches don't differentiate "
            "model capability."
        ),
        artifacts=("solution/solve.sh",),
        verification="programmatic",
        source="Harbor audit 2026-04-24 (8% trivial tasks in random 50-sample)",
        failure_example=(
            "bun-dns-lookup-non-object-crash: 1-line method swap isCell→isObject; "
            "tests only do `git log`"
        ),
    ),
    Rubric(
        name="instruction_no_path_leak",
        tier="A",
        description=(
            "instruction.md must not cite the exact file path(s) the gold patch modifies. "
            "Localization is part of the task's difficulty; naming the target file makes "
            "the bug trivially findable."
        ),
        artifacts=("instruction.md", "solution/solve.sh"),
        verification="programmatic",
        source="Harbor audit 2026-04-24 (~10% of eval 30 had direct path leaks)",
        failure_example=(
            "areal-data-proxy-batch-endpoint: instruction names app.py + rpc_server.py, "
            "exactly the two files the gold diff touches"
        ),
    ),
)


# ── Convenience accessors ───────────────────────────────────────────────────

BY_NAME: dict[str, Rubric] = {r.name: r for r in RUBRICS}
LLM_JUDGE = tuple(r for r in RUBRICS if r.verification in ("llm_judge", "both"))
# PROGRAMMATIC_RUBRICS exists implicitly — task_lint.py emits Findings whose
# `rubric` field points here via name; no need to maintain the tuple separately.


if __name__ == "__main__":
    # Smoke test
    from collections import Counter
    tiers = Counter(r.tier for r in RUBRICS)
    verif = Counter(r.verification for r in RUBRICS)
    print(f"Total rubrics: {len(RUBRICS)} — tiers A/B/C = {tiers['A']}/{tiers['B']}/{tiers['C']}")
    programmatic = sum(1 for r in RUBRICS if r.verification in ("programmatic", "both"))
    print(f"  Programmatic-checkable: {programmatic}, LLM-judge: {len(LLM_JUDGE)}")
    print()
    for r in RUBRICS:
        marker = "🔴" if r.tier == "A" else "🟡" if r.tier == "B" else "⚪"
        print(f"{marker} [{r.tier}] {r.name}: {r.description[:90]}")
