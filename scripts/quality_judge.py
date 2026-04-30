#!/usr/bin/env python3
"""Quality judge for agentmd-edit tasks AND markdown_authoring tasks.

Two-phase filter:
  Phase 1 (programmatic): flag obvious issues — Tier 2 only, no rubric, trivial
  Phase 2 (Gemini): read instruction.md + solve.sh summary for borderline tasks

Modes:
  --mode agentmd_edits      (default) Original schema for markdown_edits/
  --mode markdown_authoring Markdown-authoring task quality (load-bearing vs slop)

Pre-judge mode:
  --scout-jsonl <in> --filtered-output <out>
  Judges scout rows by title + file_paths + repo only (no body / no patch).
  Catches obvious slop (auto-bot titles, dummy test PRs) before scaffolder
  wastes work on them. Lighter signal than the full markdown_authoring judge,
  so we keep the post-scaffold judge as a final gate.

Usage:
    source .env && export GEMINI_API_KEY
    # Original agentmd-edits
    .venv/bin/python scripts/quality_judge.py --output /tmp/quality_results.json
    # Markdown authoring corpus
    .venv/bin/python scripts/quality_judge.py \\
        --mode markdown_authoring \\
        --task-dir markdown_authoring \\
        --quarantine
    # Pre-judge: filter scout JSONL before scaffolder runs
    .venv/bin/python scripts/quality_judge.py \\
        --mode markdown_authoring \\
        --scout-jsonl /home/alex/agentsmd-rl/scouted_X.jsonl \\
        --filtered-output /tmp/filtered_X.jsonl \\
        --concurrency 32
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

# TASK_DIR is now a CLI arg; keep this as the legacy default.
DEFAULT_TASK_DIR = Path("markdown_edits")

# Gemini structured output schema for quality classification
# Markdown_authoring quality schema — load-bearing vs slop, for the
# pure-tier-1-md corpus produced by scripts/scaffold_markdown_only.py.
MD_AUTHORING_SCHEMA = {
    "type": "object",
    "properties": {
        "load_bearing": {
            "type": "boolean",
            "description": "Does the markdown change actually alter agent behavior in a verifiable way?",
        },
        "research_relevant": {
            "type": "boolean",
            "description": "Does this fit the agent-md research schema (tier-1 file with measurable behavioral signal)?",
        },
        "slop_score": {
            "type": "integer",
            "description": "0=high quality, 10=pure AI slop / boilerplate / generic prose / auto-bot.",
        },
        "primary_issue": {
            "type": "string",
            "description": "If verdict=LOW or DELETE, dominant reason in <= 10 words. Empty otherwise.",
        },
        "evidence": {
            "type": "string",
            "description": "One short sentence quoting or citing the most decisive signal from the diff.",
        },
        "verdict": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW", "DELETE"],
        },
    },
    "required": ["load_bearing", "research_relevant", "slop_score",
                 "evidence", "verdict"],
    "propertyOrdering": ["load_bearing", "research_relevant", "slop_score",
                         "primary_issue", "evidence", "verdict"],
}


def _md_authoring_prompt(task_dir: Path) -> str:
    """Build the prompt for a markdown_authoring task."""
    instruction = ""
    instr_path = task_dir / "instruction.md"
    if instr_path.exists():
        instruction = instr_path.read_text(errors="replace")[:6000]

    manifest_path = task_dir / "eval_manifest.yaml"
    try:
        m = yaml.safe_load(manifest_path.read_text()) or {}
    except yaml.YAMLError:
        return f"BROKEN_MANIFEST in {task_dir.name}"
    src = m.get("source", {})
    repo = src.get("repo", "?")
    pr = src.get("pr", "?")
    config_edits = m.get("config_edits", []) or []
    file_paths = "\n".join(f"- {ce.get('path','?')}" for ce in config_edits)
    gold_added = "\n\n---\n\n".join(
        (ce.get("gold_added") or "")[:6000] for ce in config_edits
    )[:18000]

    return f"""You are a strict reviewer auditing an SWE-benchmark corpus called `agentsmd-rl`. The benchmark tests whether AI coding agents follow project-specific rule files (CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules) during coding tasks.

Below is a single candidate **markdown_authoring** task. Decide whether it should stay in the corpus or be rejected as **AI slop / decorative / non-load-bearing**.

## Task source
Repo: {repo}
PR: #{pr}
Files changed (all live inside skill / rule-file directory hierarchies):
{file_paths}

The changed paths fall into one of these categories — keep this in mind when judging:
1. **Direct rule files** (CLAUDE.md / AGENTS.md / SKILL.md / .cursorrules / .claude/rules/*.md) — agents read these directly
2. **Skill content .md** (skills/<name>/forms.md, references/api.md, CHANGELOG.md) — referenced from a SKILL.md, instructs the agent on how to do a specific task
3. **Skill-supporting scripts** (skills/<name>/scripts/*.py / *.js) — helper code an agent invokes while doing skill work; load-bearing only when (a) the script implements a concrete decision the agent must make OR (b) the SKILL.md tells the agent to call it
4. **Skill assets** (skills/<name>/assets/*) — fixtures, templates, examples; load-bearing only when the asset encodes specific structure the agent must reproduce (e.g. an example output template), NOT when it's just decoration

## PR description (this becomes the agent's instruction.md)
```
{instruction}
```

## Gold patch — the content the PR added
```
{gold_added}
```

## What "load-bearing" means here
A change is **load-bearing** when it would cause an agent to behave differently downstream — e.g. specific commands, anti-patterns, file paths, version pins, conventions that contradict defaults, cross-references that route the agent to actual code, behavioral rules a competent agent could violate, helper scripts whose absence would force the agent to make a specific judgment call differently.

A change is **NOT load-bearing** if it is:
- Generic AI-generated boilerplate any LLM could output ("This skill helps with X", "comprehensive guide for Y", "best practices") with no specifics
- Auto-generated by a bot ("Automated AGENTS.md update for commit ABC", "Generated by Claude Code") with no human-curated content
- Pure typo / formatting / linting fixes
- Self-referential meta-content ("This is a skill for managing skills") with no concrete behavior change
- Lockfile-style updates that happen to touch a markdown file
- A net-new skill file whose body is generic prose with no specific commands, file paths, or anti-patterns
- A skill helper script that's just a thin wrapper around stdlib calls (e.g. `print(json.dumps(...))`) with no project-specific decisions baked in
- Asset/fixture changes that are aesthetic-only (image regenerated, diagram restyled, example reformatted) without altering specified structure

## Verdicts
- HIGH: clear specific behavioral rule OR concrete decision-bearing helper, low slop (slop_score <= 3)
- MEDIUM: plausible but generic-leaning, mid slop (slop_score 4-6)
- LOW: decorative/boilerplate, marginal value (slop_score 7-8)
- DELETE: pure slop or auto-bot output (slop_score >= 9, OR load_bearing=false AND research_relevant=false)

Be strict. When in doubt, downgrade. A skill PR that adds a `scripts/build.py` containing 30 lines of generic glue is LOW or DELETE — it's not testing whether the agent follows the project's conventions, it's just net-new code.
"""


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


def phase1_programmatic(task_dir: Path, mode: str = "agentmd_edits") -> dict:
    """Fast programmatic checks. Returns flags and auto-verdict if obvious.

    For markdown_authoring mode, the bar is different: any tier-1 config_edit
    counts as a real signal; rubric/distractor absence isn't a defect.
    """
    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return {"verdict": "DELETE", "reason": "no_manifest"}

    try:
        m = yaml.safe_load(manifest_path.read_text()) or {}
    except yaml.YAMLError as e:
        # Scaffolder mis-escaped backticks/etc. → bad manifest.
        return {"verdict": "DELETE", "reason": f"yaml_parse_error: {str(e)[:80]}"}
    config_edits = m.get("config_edits", [])
    rubric = m.get("rubric", [])
    distractors = m.get("distractors", [])
    checks = m.get("checks", [])
    f2p = sum(1 for c in checks if c.get("type") == "fail_to_pass")

    # Markdown-authoring mode: simpler programmatic gate
    if mode == "markdown_authoring":
        flags = []
        if not config_edits:
            return {"verdict": "DELETE", "reason": "no_config_edits", "flags": flags}
        # Auto-DELETE for known auto-bot patterns (PrefectHQ etc.)
        instr = task_dir / "instruction.md"
        if instr.exists():
            txt = instr.read_text(errors="replace")[:2000].lower()
            if ("automated agents.md update" in txt or
                "this pr was generated by claude code" in txt):
                return {"verdict": "DELETE", "reason": "auto_bot_pr",
                        "flags": ["auto_bot"]}
        return {"verdict": None, "flags": flags,
                "config_edit_count": len(config_edits), "f2p": f2p}

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


def phase2_gemini(task_dir: Path, gemini_key: str,
                  mode: str = "agentmd_edits",
                  service_tier: str | None = None) -> dict:
    """Gemini reads task content and classifies quality.

    `mode` selects prompt + schema. `service_tier="flex"` for 50% Standard cost.
    """
    if mode == "markdown_authoring":
        prompt = _md_authoring_prompt(task_dir)
        schema = MD_AUTHORING_SCHEMA
        sys_inst = ("You are an SWE-benchmark quality auditor. Be brutally "
                    "honest. Reject AI slop, auto-bot output, and decorative "
                    "edits. Reward concrete behavioral rules an agent could "
                    "violate.")
        result = call_gemini(
            prompt, gemini_key,
            schema=schema, system_instruction=sys_inst,
            temperature=0.1, service_tier=service_tier,
        )
        if "error" in result:
            return {"verdict": "ERROR", "error": result.get("error", "")}
        return result

    return _phase2_agentmd_edits(task_dir, gemini_key, service_tier)


def _phase2_agentmd_edits(task_dir: Path, gemini_key: str,
                          service_tier: str | None = None) -> dict:
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
        service_tier=service_tier,
    )

    if "error" in result:
        return {"verdict": "ERROR", "error": result.get("error", "")}

    return result


def run_audit(task_dir: Path, gemini_key: str, mode: str = "agentmd_edits",
              limit: int = 0, service_tier: str | None = None,
              concurrency: int = 1) -> list[dict]:
    """Run full audit. Concurrency>1 uses asyncio + ThreadPool for parallel
    Gemini calls (call_gemini is sync urllib, so we offload to threads)."""
    paths = [p for p in sorted(task_dir.iterdir()) if p.is_dir()]
    if limit:
        paths = paths[:limit]

    if concurrency <= 1:
        return _run_audit_sequential(paths, gemini_key, mode, service_tier)
    return _run_audit_concurrent(paths, gemini_key, mode, service_tier,
                                 concurrency)


def _run_audit_sequential(paths, gemini_key, mode, service_tier):
    results = []
    for task_path in paths:
        results.append(_audit_one(task_path, gemini_key, mode, service_tier))
        time.sleep(0.3)
    return results


def _run_audit_concurrent(paths, gemini_key, mode, service_tier, concurrency):
    import asyncio
    import concurrent.futures
    started = time.monotonic()
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "DELETE": 0,
              "ERROR": 0, "UNKNOWN": 0}
    results: list = []

    def progress():
        if len(results) % 25 == 0 and len(results):
            r = len(results) / max(1, time.monotonic() - started)
            print(f"  [{len(results)}/{len(paths)}] {r:.2f}/s  "
                  f"H={counts['HIGH']} M={counts['MEDIUM']} "
                  f"L={counts['LOW']} D={counts['DELETE']} "
                  f"ERR={counts['ERROR']}", flush=True)

    async def main():
        loop = asyncio.get_running_loop()
        sem = asyncio.Semaphore(concurrency)
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            async def one(p):
                async with sem:
                    r = await loop.run_in_executor(
                        pool, _audit_one, p, gemini_key, mode, service_tier)
                    results.append(r)
                    v = r.get("verdict", "ERROR")
                    counts[v] = counts.get(v, 0) + 1
                    progress()
                    return r
            await asyncio.gather(*(one(p) for p in paths))
    asyncio.run(main())
    return results


def _audit_one(task_path: Path, gemini_key: str, mode: str,
               service_tier: str | None) -> dict:
    p1 = phase1_programmatic(task_path, mode)
    if p1["verdict"] == "DELETE":
        return {"task": task_path.name, "phase": "p1", "verdict": "DELETE",
                "reason": p1.get("reason", ""), "flags": p1.get("flags", [])}
    if not gemini_key:
        return {"task": task_path.name, "phase": "p1_only",
                "verdict": "UNKNOWN", "flags": p1.get("flags", []),
                **{k: v for k, v in p1.items() if k not in ("verdict", "flags")}}
    p2 = phase2_gemini(task_path, gemini_key, mode, service_tier)
    out_path = task_path / "md_quality.json"
    try:
        out_path.write_text(json.dumps(p2, indent=2))
    except Exception:
        pass
    if mode == "markdown_authoring":
        return {"task": task_path.name, "phase": "p2",
                "verdict": p2.get("verdict", "ERROR"),
                "load_bearing": p2.get("load_bearing"),
                "research_relevant": p2.get("research_relevant"),
                "slop_score": p2.get("slop_score"),
                "primary_issue": p2.get("primary_issue", ""),
                "evidence": p2.get("evidence", ""),
                "p1_flags": p1.get("flags", [])}
    return {"task": task_path.name, "phase": "p2",
            "verdict": p2.get("verdict", "ERROR"),
            "config_navigation": p2.get("config_navigation", ""),
            "config_edit_organic": p2.get("config_edit_organic", False),
            "task_type": p2.get("task_type", ""),
            "reasoning": p2.get("reasoning", ""),
            "p1_flags": p1.get("flags", [])}


# ---------------------------------------------------------------------------
# Pre-judge — title-only / file_paths-only screening on scout output
# ---------------------------------------------------------------------------

PREJUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["KEEP", "DROP"],
        },
        "reason": {
            "type": "string",
            "description": "<= 12 words explaining the decision.",
        },
    },
    "required": ["verdict", "reason"],
    "propertyOrdering": ["verdict", "reason"],
}


def _prejudge_prompt(repo: str, pr: int, title: str, file_paths: list) -> str:
    paths_str = "\n".join(f"  - {p}" for p in file_paths)
    return f"""You are a fast pre-screen for an SWE-benchmark corpus called `agentsmd-rl`. The benchmark studies whether AI coding agents follow project-specific rule files (CLAUDE.md / AGENTS.md / SKILL.md / .cursor/rules).

Decision: KEEP or DROP this PR before we waste effort scaffolding it. You have only title + file paths + repo (no body, no patch). Default to KEEP unless the title is OBVIOUSLY slop. The post-scaffold judge will see the gold patch and apply stricter checks; pre-judge is just to skip the most obvious throwaways.

This PR's changed files all live in skill / rule-file directory hierarchies. They may include:
- **Direct rule files** — CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules, .claude/rules/*.md (high signal)
- **Skill-adjacent .md files** — references/api.md, forms.md, CHANGELOG.md inside skills/<name>/ (often load-bearing skill content)
- **Skill-supporting code** — scripts/build.py, scripts/extract.py inside skills/<name>/scripts/ (sometimes load-bearing helpers, sometimes generic glue)
- **Skill assets** — diagrams, templates, fixtures inside skills/<name>/assets/ (usually low signal)

Your job: is the TITLE itself a strong signal of slop?

DROP signals:
- Auto-bot titles: "Automated AGENTS.md update for commit XYZ", "Generated by Claude Code", "Auto-generated by ..."
- Dummy / test / CI scaffolding: "test: broken merge-batch e2e PR", "DO NOT MERGE", "[draft] testing"
- Pure version-bump / metadata-only: "bump skill version to 1.0.1", "add tags", "fix typo"
- Generic boilerplate any LLM could produce: "Add comprehensive guide for X" with no specific feature
- Asset-only churn: title references only image/diagram/fixture updates ("update screenshot", "regenerate diagram")

Otherwise KEEP. The post-judge sees the actual diff and can downgrade — your bar is "obviously throwaway".

## PR
Repo: {repo}
PR: #{pr}
Title: {title}
Files changed:
{paths_str}

Output JSON only.
"""


def _prejudge_one(row: dict, gemini_key: str, service_tier: str) -> dict:
    repo = row.get("repo", "")
    pr = row.get("pr_number") or row.get("pr") or 0
    title = row.get("title", "")
    file_paths = row.get("file_paths", []) or []
    if not file_paths:
        return {"verdict": "KEEP", "reason": "no_file_paths_skip_check"}
    prompt = _prejudge_prompt(repo, pr, title, file_paths)
    # gemini-3.1-pro-preview-customtools requires thinking (budget=0 returns
    # 400 INVALID_ARGUMENT). Use a small budget — enough to reason briefly
    # without burning maxOutputTokens before JSON is emitted.
    res = call_gemini(prompt, gemini_key,
                      schema=PREJUDGE_SCHEMA, temperature=0.1,
                      max_tokens=2048, service_tier=service_tier,
                      thinking_budget=256)
    if "error" in res:
        return {"verdict": "KEEP", "reason": f"judge_error:{res.get('error','')[:30]}"}
    return res


def run_prejudge(scout_jsonl: Path, filtered_output: Path,
                 gemini_key: str, service_tier: str | None,
                 concurrency: int = 32) -> dict:
    """Pre-judge scout JSONL by title + file_paths + repo. Writes filtered
    JSONL with only KEEP rows. Returns counts dict.

    First does a free regex pre-filter against TIER1_DISCOVERY_RE — broad
    recall for skill-related PRs (rule files OR adjacent files like
    skills/<name>/scripts/*.py, references/*.md, assets/*). Codebearing PRs
    that don't touch any skill / rule-file location drop straight to a
    separate output without a Gemini call. Gemini decides among the rest.
    """
    import asyncio
    import concurrent.futures

    from taskforge.config import TIER1_DISCOVERY_RE as TIER1

    rows: list[dict] = []
    codebearing: list[dict] = []
    with open(scout_jsonl) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            fp = d.get("file_paths", []) or []
            # Pre-filter: only pure-tier1-md PRs go to Gemini.
            if fp and all(TIER1.search(p) for p in fp):
                rows.append(d)
            else:
                codebearing.append(d)
    print(f"Scout total: {len(rows)+len(codebearing)}", flush=True)
    print(f"  pure-tier-1-md (Gemini-judged): {len(rows)}", flush=True)
    print(f"  codebearing (regex-filtered, no Gemini): {len(codebearing)}", flush=True)

    counts = {"KEEP": 0, "DROP": 0, "ERROR": 0}
    decisions: list[dict] = []
    started = time.monotonic()

    def progress():
        if len(decisions) % 100 == 0 and len(decisions):
            r = len(decisions) / max(1, time.monotonic() - started)
            print(f"  [{len(decisions)}/{len(rows)}] {r:.1f}/s  "
                  f"K={counts['KEEP']} D={counts['DROP']} E={counts['ERROR']}",
                  flush=True)

    async def main_async():
        loop = asyncio.get_running_loop()
        sem = asyncio.Semaphore(concurrency)
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            async def one(row):
                async with sem:
                    res = await loop.run_in_executor(
                        pool, _prejudge_one, row, gemini_key, service_tier)
                    decisions.append({**row, "_prejudge": res})
                    v = res.get("verdict", "ERROR")
                    counts[v] = counts.get(v, 0) + 1
                    progress()
            await asyncio.gather(*(one(r) for r in rows))

    asyncio.run(main_async())

    kept = [d for d in decisions if d["_prejudge"]["verdict"] == "KEEP"]
    # Strip _prejudge from output rows so they're a clean scout-format JSONL
    with open(filtered_output, "w") as f:
        for d in kept:
            out = {k: v for k, v in d.items() if k != "_prejudge"}
            f.write(json.dumps(out) + "\n")
    print(f"\n=== Pre-judge done ===")
    print(f"  KEEP:  {counts['KEEP']}")
    print(f"  DROP:  {counts['DROP']}")
    print(f"  ERROR: {counts['ERROR']}")
    print(f"Wrote {len(kept)} kept rows → {filtered_output}")
    # Also write a CSV of decisions for audit
    csv_path = filtered_output.with_suffix(".decisions.csv")
    with open(csv_path, "w") as f:
        f.write("repo,pr,title,verdict,reason\n")
        for d in decisions:
            r = d["_prejudge"]
            t = (d.get("title", "") or "").replace('"', "'")[:120]
            f.write(f'"{d.get("repo","")}",{d.get("pr_number") or d.get("pr","")},"{t}",{r.get("verdict","")},"{(r.get("reason","") or "").replace(chr(34), chr(39))[:200]}"\n')
    print(f"Wrote audit CSV → {csv_path}")
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        choices=["agentmd_edits", "markdown_authoring"],
                        default="agentmd_edits")
    parser.add_argument("--task-dir", type=Path,
                        help="Override task directory (default: markdown_edits or markdown_authoring per --mode)")
    parser.add_argument("--output", default="/tmp/quality_results.json")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=8,
                        help="Concurrent Gemini calls (default 8)")
    parser.add_argument("--service-tier", default="flex",
                        choices=["flex", "standard"],
                        help="Gemini service tier (default flex = 50%% off)")
    parser.add_argument("--delete", action="store_true",
                        help="(agentmd_edits) actually delete LOW/DELETE tasks")
    parser.add_argument("--quarantine", action="store_true",
                        help="(markdown_authoring) move LOW/DELETE to <task-dir>_quarantine_quality/")
    parser.add_argument("--move-tier2", action="store_true",
                        help="Move Tier 2 only tasks to markdown_following")
    # Pre-judge mode
    parser.add_argument("--scout-jsonl", type=Path,
                        help="Pre-judge mode: filter a scout JSONL by title+files (no scaffold)")
    parser.add_argument("--filtered-output", type=Path,
                        help="Pre-judge mode: where to write the kept-rows JSONL")
    args = parser.parse_args()

    # Pre-judge branch — short-circuits before the task-dir logic
    if args.scout_jsonl:
        if not args.filtered_output:
            sys.exit("--scout-jsonl requires --filtered-output")
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if not gemini_key:
            env_file = Path(".env")
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith("GEMINI_API_KEY="):
                        gemini_key = line.split("=", 1)[1].strip().strip('"')
        if not gemini_key:
            sys.exit("GEMINI_API_KEY required for pre-judge mode")
        service_tier = "flex" if args.service_tier == "flex" else None
        run_prejudge(args.scout_jsonl, args.filtered_output,
                     gemini_key, service_tier, args.concurrency)
        return

    # Default task-dir per mode
    task_dir = args.task_dir
    if task_dir is None:
        task_dir = (Path("markdown_authoring")
                    if args.mode == "markdown_authoring"
                    else DEFAULT_TASK_DIR)

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"')

    if gemini_key:
        print(f"Gemini key: {gemini_key[:8]}...{gemini_key[-4:]}")
    else:
        print("No Gemini key — phase1 only")

    service_tier = "flex" if args.service_tier == "flex" else None
    print(f"Mode: {args.mode}  Task dir: {task_dir}  Tier: {args.service_tier}  "
          f"Concurrency: {args.concurrency}")

    results = run_audit(task_dir, gemini_key, args.mode, args.limit,
                        service_tier=service_tier,
                        concurrency=args.concurrency)

    from collections import Counter
    verdicts = Counter(r["verdict"] for r in results)
    print(f"\n{'='*60}")
    print(f"AUDIT RESULTS ({len(results)} tasks)")
    for v, count in verdicts.most_common():
        print(f"  {v:8s}: {count}")
    print(f"{'='*60}")

    Path(args.output).write_text(json.dumps(results, indent=2))
    print(f"Details saved to {args.output}")

    if args.delete:
        import shutil
        deleted = 0
        for r in results:
            if r["verdict"] in ("DELETE", "LOW"):
                p = task_dir / r["task"]
                if p.exists():
                    shutil.rmtree(p)
                    deleted += 1
        print(f"\nDeleted {deleted} tasks")

    if args.quarantine:
        import shutil
        qdir = task_dir.with_name(task_dir.name + "_quarantine_quality")
        qdir.mkdir(exist_ok=True)
        moved = 0
        for r in results:
            if r["verdict"] in ("DELETE", "LOW"):
                src = task_dir / r["task"]
                dst = qdir / r["task"]
                if src.exists() and not dst.exists():
                    shutil.move(str(src), str(dst))
                    moved += 1
        print(f"\nQuarantined {moved} → {qdir.name}/")


if __name__ == "__main__":
    main()
