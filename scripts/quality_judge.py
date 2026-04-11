#!/usr/bin/env python3
"""Quality judge for agentmd-edit tasks.

Two-phase filter:
  Phase 1 (programmatic): flag obvious issues — Tier 2 only, no rubric, trivial
  Phase 2 (Gemini): read instruction.md + solve.sh summary for borderline tasks

Usage:
    source .env && export GEMINI_API_KEY
    .venv/bin/python scripts/quality_judge.py --output /tmp/quality_results.json
    .venv/bin/python scripts/quality_judge.py --delete  # actually delete LOW/DELETE tasks
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from taskforge.gemini_rubric_constructor import call_gemini

TASK_DIR = Path("harbor_tasks_agentmd_edits")

# Gemini structured output schema for quality classification
QUALITY_SCHEMA = {
    "type": "object",
    "properties": {
        "config_navigation": {
            "type": "string",
            "description": "Does the agent need to navigate a hierarchy of config files?",
            "enum": ["deep_hierarchy", "moderate", "flat_single_file", "none"],
        },
        "config_edit_organic": {
            "type": "boolean",
            "description": "Is the config edit organically connected to the code change?",
        },
        "task_type": {
            "type": "string",
            "enum": ["bugfix_plus_config", "feature_plus_config", "docs_only", "config_only", "mixed_unrelated"],
        },
        "reasoning": {
            "type": "string",
            "description": "2-3 sentence explanation of the classification",
        },
        "verdict": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW", "DELETE"],
        },
    },
    "required": ["config_navigation", "config_edit_organic", "task_type", "reasoning", "verdict"],
    "propertyOrdering": ["config_navigation", "config_edit_organic", "task_type", "reasoning", "verdict"],
}


def phase1_programmatic(task_dir: Path) -> dict:
    """Fast programmatic checks. Returns flags and auto-verdict if obvious."""
    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return {"verdict": "DELETE", "reason": "no_manifest"}

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
    if f2p <= 1:
        flags.append("trivial_code")

    # Auto-verdicts for obvious cases
    if not config_edits and not rubric and not distractors:
        return {"verdict": "DELETE", "reason": "no_config_signal", "flags": flags}

    return {
        "verdict": None,  # needs Gemini
        "flags": flags,
        "has_tier1": has_tier1,
        "tier2_only": tier2_only,
        "rubric_count": len(rubric),
        "distractor_count": len(distractors),
        "f2p": f2p,
        "config_edit_count": len(config_edits),
    }


def phase2_gemini(task_dir: Path, gemini_key: str) -> dict:
    """Gemini reads instruction + solve.sh summary and classifies quality."""
    instruction = ""
    instr_path = task_dir / "instruction.md"
    if instr_path.exists():
        instruction = instr_path.read_text()[:1500]

    solve_text = ""
    solve_path = task_dir / "solution" / "solve.sh"
    if solve_path.exists():
        solve_text = solve_path.read_text()[:2000]

    manifest_path = task_dir / "eval_manifest.yaml"
    m = yaml.safe_load(manifest_path.read_text()) or {}

    # Summarize eval_manifest
    config_edits_summary = ""
    for ce in m.get("config_edits", []):
        tier = ce.get("tier", 2)
        path = ce.get("path", "")
        added = ce.get("gold_added", "")[:200]
        config_edits_summary += f"\n- {path} (tier {tier}): {added[:100]}"

    rubric_summary = "\n".join(
        f"- {r.get('rule', '')[:100]}" for r in m.get("rubric", [])[:5]
    )
    distractor_summary = "\n".join(
        f"- [{d.get('collision_type', '')}] {d.get('rule', '')[:80]}"
        for d in m.get("distractors", [])[:3]
    )

    prompt = f"""Classify this coding task for research on agent instruction discrimination.

Our research question: can agents REASON about which repo instructions (AGENTS.md, CLAUDE.md, SKILL.md) apply vs which are distractors? We need tasks where the agent must make NON-OBVIOUS decisions about config conventions.

## What makes a task HIGH quality:
- The code change is substantial (bugfix, feature, refactor across multiple files)
- The config/doc edit is ORGANICALLY connected to the code change (not stapled on)
- The rubric rules test conventions that require JUDGMENT, not mechanical copy-paste
- Distractors create genuine decision points an agent would plausibly fall for
- A README edit IS fine if it documents a significant architectural/API change that requires understanding the codebase

## What makes a task LOW/DELETE:
- Config edit is trivially connected to rubrics (add 1 line to README, rubric says "added line to README")
- Task is primarily creating new docs/examples from scratch (not fixing/modifying existing code)
- Config edit is completely unrelated to the code change (two unrelated tasks stapled together)
- The agent just needs to be "aware of X" without any reasoning about conflicting conventions
- Rubric rules are surface-level ("use TypeScript") rather than requiring config hierarchy navigation

## Verdicts:
- HIGH: agent must reason about competing instructions, config hierarchy, or non-obvious convention application
- MEDIUM: real code change with some config signal, but connection is shallow or hierarchy is flat
- LOW: trivial config edit, primarily docs, or config/code are disconnected
- DELETE: wrong dataset entirely (no agent config interaction)

## Task: {task_dir.name}

## Instruction:
{instruction}

## Gold solution (solve.sh):
```
{solve_text}
```

## Config edits:
{config_edits_summary or "(none)"}

## Rubric rules:
{rubric_summary or "(none)"}

## Distractors:
{distractor_summary or "(none)"}

Think carefully: does the rubric test something NON-TRIVIAL? Is the config edit organically connected to the code change? Would an agent need to reason about which instructions apply?"""

    result = call_gemini(
        prompt, gemini_key,
        schema=QUALITY_SCHEMA,
        system_instruction="You are a benchmark quality auditor. Be brutally honest. A task where the rubric is trivially connected to the config edit (add line → rubric checks line was added) is LOW. A README edit documenting a major architectural change IS valuable. Focus on whether the agent must REASON about competing instructions.",
        temperature=0.1,
    )

    if "error" in result:
        return {"verdict": "ERROR", "error": result.get("error", "")}

    return result


def run_audit(gemini_key: str, limit: int = 0) -> list[dict]:
    """Run full audit on all agentmd tasks."""
    results = []

    for task_path in sorted(TASK_DIR.iterdir()):
        if not task_path.is_dir():
            continue

        # Phase 1
        p1 = phase1_programmatic(task_path)

        if p1["verdict"] == "DELETE":
            results.append({
                "task": task_path.name,
                "phase": "p1",
                "verdict": "DELETE",
                "reason": p1.get("reason", ""),
                "flags": p1.get("flags", []),
            })
            continue

        # Phase 2: Gemini for all remaining
        if not gemini_key:
            results.append({
                "task": task_path.name,
                "phase": "p1_only",
                "verdict": "UNKNOWN",
                "flags": p1.get("flags", []),
                **{k: v for k, v in p1.items() if k not in ("verdict", "flags")},
            })
            continue

        p2 = phase2_gemini(task_path, gemini_key)
        results.append({
            "task": task_path.name,
            "phase": "p2",
            "verdict": p2.get("verdict", "ERROR"),
            "config_navigation": p2.get("config_navigation", ""),
            "config_edit_organic": p2.get("config_edit_organic", False),
            "task_type": p2.get("task_type", ""),
            "reasoning": p2.get("reasoning", ""),
            "p1_flags": p1.get("flags", []),
            "has_tier1": p1.get("has_tier1", False),
            "rubric_count": p1.get("rubric_count", 0),
            "distractor_count": p1.get("distractor_count", 0),
            "f2p": p1.get("f2p", 0),
        })

        time.sleep(0.5)  # rate limit

        if limit and len(results) >= limit:
            break

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/quality_results.json")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--delete", action="store_true", help="Actually delete LOW/DELETE tasks")
    parser.add_argument("--move-tier2", action="store_true", help="Move Tier 2 only tasks to harbor_tasks")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"')

    print(f"Gemini key: {gemini_key[:8]}...{gemini_key[-4:]}" if gemini_key else "No Gemini key")

    results = run_audit(gemini_key, args.limit)

    # Summary
    from collections import Counter
    verdicts = Counter(r["verdict"] for r in results)
    print(f"\n{'='*60}")
    print(f"AUDIT RESULTS ({len(results)} tasks)")
    for v, count in verdicts.most_common():
        print(f"  {v:8s}: {count}")
    print(f"{'='*60}")

    # Save
    Path(args.output).write_text(json.dumps(results, indent=2))
    print(f"Details saved to {args.output}")

    if args.delete:
        import shutil
        deleted = 0
        for r in results:
            if r["verdict"] in ("DELETE", "LOW"):
                task_path = TASK_DIR / r["task"]
                if task_path.exists():
                    shutil.rmtree(task_path)
                    deleted += 1
                    print(f"  DELETED: {r['task']}")
        print(f"\nDeleted {deleted} tasks")


if __name__ == "__main__":
    main()
