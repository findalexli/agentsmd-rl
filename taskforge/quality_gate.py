"""Quality gate for agentmd-edit tasks.

Reusable module that classifies whether a task genuinely tests agent
instruction discrimination (config hierarchy navigation, meta-referential
editing, competing principles) vs trivial config/doc changes.

Designed to be called:
  1. Post-scaffold in E2B pipeline (reject weak tasks before validation)
  2. Batch audit of existing tasks
  3. Pre-filter during PR scouting

Two phases:
  Phase 1 (programmatic, <1ms): fast flags from eval_manifest.yaml
  Phase 2 (Gemini structured output, ~3s): reads instruction + solve.sh

Usage:
    from taskforge.quality_gate import classify_task, classify_task_fast

    # Fast programmatic check (no API call)
    result = classify_task_fast(task_dir)
    if result.verdict == "DELETE":
        shutil.rmtree(task_dir)

    # Full Gemini classification
    result = classify_task(task_dir, gemini_key)
    if result.verdict in ("HIGH", "MEDIUM"):
        keep_in_agentmd_edits(task_dir)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

from taskforge.gemini_rubric_constructor import call_gemini


# ── Result dataclass ─────────────────────────────────────────────────────────

@dataclass
class QualityResult:
    """Quality classification for a single task."""
    task: str
    verdict: str  # HIGH, MEDIUM, LOW, DELETE
    flags: list[str] = field(default_factory=list)
    # Gemini fields (only set after phase 2)
    config_navigation: str = ""  # deep_hierarchy, moderate, flat_single_file, none
    config_edit_organic: bool | None = None
    task_type: str = ""
    reasoning: str = ""
    # Programmatic fields
    has_tier1: bool = False
    rubric_count: int = 0
    distractor_count: int = 0
    f2p_count: int = 0
    config_edit_count: int = 0


# ── Gemini structured output schema ─────────────────────────────────────────

QUALITY_SCHEMA = {
    "type": "object",
    "properties": {
        "config_navigation": {
            "type": "string",
            "enum": ["deep_hierarchy", "moderate", "flat_single_file", "none"],
        },
        "config_edit_organic": {
            "type": "boolean",
            "description": "Is the config edit organically connected to the code change?",
        },
        "meta_referential": {
            "type": "boolean",
            "description": "Must the agent edit/override its own instruction files?",
        },
        "competing_principles": {
            "type": "boolean",
            "description": "Do config rules conflict, requiring the agent to choose?",
        },
        "task_type": {
            "type": "string",
            "enum": ["bugfix_plus_config", "feature_plus_config", "docs_only",
                     "config_only", "mixed_unrelated"],
        },
        "reasoning": {
            "type": "string",
            "description": "2-3 sentence explanation",
        },
        "verdict": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW", "DELETE"],
        },
    },
    "required": ["config_navigation", "config_edit_organic", "meta_referential",
                  "competing_principles", "task_type", "reasoning", "verdict"],
    "propertyOrdering": ["config_navigation", "config_edit_organic", "meta_referential",
                         "competing_principles", "task_type", "reasoning", "verdict"],
}

SYSTEM_INSTRUCTION = (
    "You are a benchmark quality auditor for agent instruction discrimination research. "
    "You have the FULL context: instruction, solve.sh, config edits with gold content, "
    "rubric rules with sources, distractors with reasoning, and hierarchy analysis.\n\n"
    "The core question: does this task test whether an agent can REASON about config "
    "conventions? Not just 'does it touch config files' but 'does the config interaction "
    "require JUDGMENT?'\n\n"
    "Even if the instruction mentions which file to edit, the task can still be HIGH if "
    "writing the correct config content requires deep understanding of competing conventions, "
    "or if the distractors would genuinely confuse an agent. The instruction pointing to a "
    "file is fine — what matters is whether the CONTENT requires reasoning.\n\n"
    "A task is LOW when the config edit is mechanical (copy what the instruction says), "
    "creating docs from scratch (no existing conventions to reason about), or the rubric "
    "trivially mirrors the config change."
)


# ── Phase 1: Programmatic fast gate ─────────────────────────────────────────

def classify_task_fast(task_dir: Path) -> QualityResult:
    """Fast programmatic classification (<1ms, no API call).

    Catches obvious DELETE/LOW cases. Returns verdict=None when Gemini needed.
    """
    task_name = task_dir.name
    manifest_path = task_dir / "eval_manifest.yaml"

    if not manifest_path.exists():
        return QualityResult(task=task_name, verdict="DELETE", flags=["no_manifest"])

    if not yaml:
        return QualityResult(task=task_name, verdict="DELETE", flags=["no_yaml"])

    m = yaml.safe_load(manifest_path.read_text()) or {}
    config_edits = m.get("config_edits", [])
    rubric = m.get("rubric", [])
    distractors = m.get("distractors", [])
    checks = m.get("checks", [])
    f2p = sum(1 for c in checks if c.get("type") == "fail_to_pass")

    tiers = [ce.get("tier", 2) for ce in config_edits]
    has_tier1 = 1 in tiers
    tier2_only = tiers and not has_tier1

    flags = []
    if tier2_only:
        flags.append("tier2_only")
    if not config_edits:
        flags.append("no_config_edits")
    if not rubric:
        flags.append("no_rubric")
    if not distractors:
        flags.append("no_distractors")
    if f2p <= 1:
        flags.append("trivial_code")

    # Auto-DELETE: no config signal at all
    if not config_edits and not rubric and not distractors:
        has_agent_config_check = any(
            c.get("origin") == "agent_config" for c in checks
        )
        if not has_agent_config_check:
            return QualityResult(
                task=task_name, verdict="DELETE",
                flags=flags, f2p_count=f2p,
            )

    # Build result (verdict=None → needs Gemini)
    return QualityResult(
        task=task_name,
        verdict="",  # needs phase 2
        flags=flags,
        has_tier1=has_tier1,
        rubric_count=len(rubric),
        distractor_count=len(distractors),
        f2p_count=f2p,
        config_edit_count=len(config_edits),
    )


# ── Phase 2: Gemini structured classification ──────────────────────────────

def _build_prompt(task_dir: Path) -> str:
    """Build the Gemini quality classification prompt with full context."""
    instruction = ""
    instr_path = task_dir / "instruction.md"
    if instr_path.exists():
        instruction = instr_path.read_text()[:2000]

    solve_text = ""
    solve_path = task_dir / "solution" / "solve.sh"
    if solve_path.exists():
        solve_text = solve_path.read_text()[:3000]

    manifest_path = task_dir / "eval_manifest.yaml"
    m = yaml.safe_load(manifest_path.read_text()) or {}

    # Full config edits with gold content
    config_edits_text = ""
    for ce in m.get("config_edits", []):
        tier = ce.get("tier", 2)
        path = ce.get("path", "")
        added = ce.get("gold_added", "")[:400]
        removed = ce.get("gold_removed", "")[:200]
        config_edits_text += f"\n### {path} (tier {tier})"
        if added:
            config_edits_text += f"\nAdded:\n```\n{added}\n```"
        if removed:
            config_edits_text += f"\nRemoved:\n```\n{removed}\n```"

    # Full rubric with sources and evidence
    rubric_text = ""
    for r in m.get("rubric", []):
        rubric_text += f"\n- Rule: {r.get('rule', '')[:150]}"
        if r.get("source"):
            rubric_text += f"\n  Source: {r['source'].get('path', '')}:{r['source'].get('lines', '')}"
        if r.get("evidence"):
            rubric_text += f"\n  Evidence: {r['evidence'][:150]}"

    # Full distractors with reasoning
    distractor_text = ""
    for d in m.get("distractors", []):
        distractor_text += f"\n- [{d.get('collision_type', '')}] {d.get('rule', '')[:120]}"
        distractor_text += f"\n  Why distracting: {d.get('why_distracting', '')[:150]}"
        distractor_text += f"\n  Severity: {d.get('severity', '')}"

    # Hierarchy analysis (if available)
    hierarchy = m.get("hierarchy_analysis", "")

    # Count code files vs config files in solve.sh
    code_files = []
    config_files = []
    for line in solve_text.splitlines():
        if "diff --git" in line:
            path = line.split(" b/")[-1] if " b/" in line else ""
            if any(path.endswith(ext) for ext in (".md", ".mdc", ".yml", ".yaml")) or \
               any(n in path.upper() for n in ("CLAUDE", "AGENTS", "SKILL", "CURSOR", "COPILOT")):
                config_files.append(path)
            elif path:
                code_files.append(path)

    return f"""Classify this task for agent instruction discrimination research.

## Task: {task_dir.name}

## Instruction (what the agent sees):
{instruction}

## Gold solution touches:
- Code files ({len(code_files)}): {', '.join(code_files[:8])}
- Config/doc files ({len(config_files)}): {', '.join(config_files[:5])}

## Gold solution (solve.sh):
```
{solve_text}
```

## Config edits (gold content):
{config_edits_text or "(none)"}

## Positive rubric rules (with sources):
{rubric_text or "(none)"}

## Distractors (with reasoning):
{distractor_text or "(none)"}

## Hierarchy analysis:
{hierarchy or "(none)"}

## Classification guide:

HIGH = the task is meaningfully harder BECAUSE of config files. The agent must:
- Understand competing/conflicting config rules to decide what to do
- Navigate config hierarchy (rules at different directory levels)
- Write config content that requires understanding the code change deeply
- Override or rewrite existing config rules that conflict with the task
Even if the instruction mentions which file to edit, if the CONTENT requires deep judgment about conventions → HIGH.

MEDIUM = real code change with genuine config signal, but:
- Config hierarchy is flat (single file)
- Distractors are present but not very confusing
- Config content is fairly obvious once you understand the code change

LOW = config edit does not test instruction discrimination:
- Config edit is mechanical (add a line, remove a reference)
- Config edit is creating docs/examples from scratch (no existing conventions to navigate)
- Rubric rules trivially mirror the config edit
- Code and config are unrelated (two tasks stapled together)

DELETE = no agent config interaction at all.

Focus on: does the RUBRIC test something that requires understanding the config HIERARCHY? Do the DISTRACTORS create genuine confusion? Is the config CONTENT non-trivial to write correctly?"""


def classify_task(task_dir: Path, gemini_key: str = "") -> QualityResult:
    """Full two-phase quality classification.

    Phase 1: programmatic fast gate
    Phase 2: Gemini structured output (if needed and key available)
    """
    # Phase 1
    result = classify_task_fast(task_dir)
    if result.verdict == "DELETE":
        return result

    # Phase 2
    gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        result.verdict = "UNKNOWN"
        result.flags.append("no_gemini_key")
        return result

    prompt = _build_prompt(task_dir)
    gemini_result = call_gemini(
        prompt, gemini_key,
        schema=QUALITY_SCHEMA,
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.1,
    )

    if "error" in gemini_result:
        result.verdict = "ERROR"
        result.flags.append(f"gemini_error:{gemini_result.get('error', '')[:50]}")
        return result

    # Apply Gemini classification
    result.config_navigation = gemini_result.get("config_navigation", "")
    result.config_edit_organic = gemini_result.get("config_edit_organic", False)
    result.task_type = gemini_result.get("task_type", "")
    result.reasoning = gemini_result.get("reasoning", "")
    result.verdict = gemini_result.get("verdict", "LOW")

    # Boost: only when BOTH meta-referential AND competing principles AND
    # Gemini says config edit is organic (prevents boosting spoon-fed tasks)
    meta = gemini_result.get("meta_referential", False)
    competing = gemini_result.get("competing_principles", False)
    organic = gemini_result.get("config_edit_organic", False)
    if meta and competing and organic and result.verdict == "MEDIUM":
        if result.f2p_count >= 3:
            old = result.verdict
            result.verdict = "HIGH"
            result.flags.append(f"boosted:{old}→{result.verdict}")

    return result


# ── Batch utilities ──────────────────────────────────────────────────────────

def classify_batch(
    task_dir: Path,
    gemini_key: str = "",
    limit: int = 0,
) -> list[QualityResult]:
    """Classify all tasks in a directory."""
    import time

    results = []
    tasks = sorted([t for t in task_dir.iterdir() if t.is_dir()])

    for i, task in enumerate(tasks):
        result = classify_task(task, gemini_key)
        results.append(result)

        if gemini_key and result.verdict not in ("DELETE",):
            time.sleep(0.3)  # rate limit

        if limit and len(results) >= limit:
            break

    return results
