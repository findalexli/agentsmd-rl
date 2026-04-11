#!/usr/bin/env python3
"""Gemini-powered rubric constructor with positive + negative rubrics.

Feeds the FULL config hierarchy + gold solution + instruction to Gemini 3.1 Pro
and extracts structured positive rubrics, negative rubrics (distractors),
skill relevance decisions, and hierarchy conflicts.

Designed to be called programmatically by Kimi agents inside E2B sandboxes
OR run standalone for batch processing.

Usage (inside sandbox):
    python3 /workspace/gemini_rubric_constructor.py \
        --task /workspace/task \
        --repo /workspace/repo \
        --output /workspace/rubric_result.json

    # Batch (local, requires pre-cloned repos):
    python3 -m taskforge.gemini_rubric_constructor \
        --task harbor_tasks_agentmd_edits/opencode-acp-question-tool-flag \
        --repo /tmp/repos/opencode
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

# Allow running standalone (not as module)
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from taskforge.hierarchy_context import (
    build_hierarchy_context,
    extract_edited_paths,
)


# ── Gemini API call ──────────────────────────────────────────────────────────

GEMINI_MODEL = "gemini-3.1-pro-preview-customtools"


def call_gemini(prompt: str, gemini_key: str, max_tokens: int = 8192) -> dict:
    """Call Gemini 3.1 Pro and parse JSON response."""
    import urllib.request

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": max_tokens,
        },
    }).encode()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={gemini_key}"
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Parse JSON from response
    if "```" in text:
        s = text.find("```json")
        if s >= 0:
            s = text.find("\n", s) + 1
        else:
            s = text.find("```") + 3
            s = text.find("\n", s) + 1
        e = text.find("```", s)
        text = text[s:e].strip()

    try:
        if text.startswith("{"):
            return json.loads(text)
        s = text.find("{")
        e = text.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(text[s:e])
    except json.JSONDecodeError:
        pass

    return {"error": "parse_failed", "raw": text[:500]}


# ── Build prompt with full context ───────────────────────────────────────────

def build_rubric_prompt(
    task_dir: Path,
    hierarchy: dict,
    config_contents: dict,
) -> str:
    """Build the Gemini prompt with full hierarchy context."""

    # Task metadata
    instruction = ""
    instr_path = task_dir / "instruction.md"
    if instr_path.exists():
        instruction = instr_path.read_text()[:2000]

    solve_text = ""
    solve_path = task_dir / "solution" / "solve.sh"
    if solve_path.exists():
        solve_text = solve_path.read_text()[:4000]

    edited_paths = hierarchy.get("edited_paths", [])

    # Build context sections
    parts = []
    parts.append("# Rubric Construction Task\n")
    parts.append(f"## Task Instruction\n{instruction}\n")
    parts.append(f"## Files Edited by Gold Solution\n{json.dumps(edited_paths)}\n")
    parts.append(f"## Gold Solution (solve.sh)\n```bash\n{solve_text}\n```\n")

    # Config hierarchy with full content
    parts.append("\n## Agent Config File Hierarchy (root → leaf)\n")
    parts.append("These files are loaded ACCUMULATIVELY — all rules from root to the nearest")
    parts.append("config file apply simultaneously. Child rules extend parent, don't replace.\n")

    for cfg in hierarchy.get("config_hierarchy", []):
        path = cfg["path"]
        content = config_contents.get(path, "")
        applies = cfg.get("applies_to", [])
        parts.append(f"\n### Level {cfg['level']}: `{path}` ({cfg['rule_count']} rules)")
        parts.append(f"Applies to: {applies}")
        parts.append(f"```markdown\n{content[:4000]}\n```\n")

    # Skills
    skills = hierarchy.get("skills", [])
    if skills:
        parts.append("\n## Skills Found in Repo\n")
        for s in skills:
            rel = "POTENTIALLY RELEVANT" if s["is_relevant"] else "LIKELY IRRELEVANT"
            parts.append(f"- [{rel}] **{s['name']}**: {s['description']}")
            parts.append(f"  Path: {s['path']}")

    # Existing rubric/config_edits
    if yaml:
        manifest_path = task_dir / "eval_manifest.yaml"
        if manifest_path.exists():
            try:
                m = yaml.safe_load(manifest_path.read_text())
                existing_rubric = m.get("rubric", [])
                config_edits = m.get("config_edits", [])
                if existing_rubric:
                    parts.append(f"\n## Existing Rubric Rules ({len(existing_rubric)})\n")
                    for r in existing_rubric:
                        if isinstance(r, dict):
                            parts.append(f"- {r.get('rule', '')[:150]}")
                if config_edits:
                    parts.append(f"\n## Gold Config Edits ({len(config_edits)})\n")
                    for ce in config_edits:
                        parts.append(f"- **{ce.get('path')}** (tier {ce.get('tier')})")
                        added = ce.get("gold_added", "")
                        if added:
                            parts.append(f"  Added: {added[:300]}")
            except Exception:
                pass

    context = "\n".join(parts)

    prompt = f"""{context}

## Your Task

Analyze the full config hierarchy above and the gold solution to construct a complete rubric.

### POSITIVE RUBRICS
Rules from the config files that the gold solution FOLLOWS. For each:
- `rule`: The convention being followed (specific, evaluable)
- `source_file`: Which config file contains this rule
- `source_lines`: Approximate line numbers
- `evidence_in_gold`: How the gold solution demonstrates compliance
- `category`: "naming" | "style" | "architecture" | "testing" | "documentation" | "tooling"

Only include rules where you can point to SPECIFIC evidence in the gold diff.

### NEGATIVE RUBRICS (DISTRACTORS)
Rules that create genuine COLLISIONS — where an agent would plausibly try to follow the rule, but doing so would produce WORSE code or wasted effort for this specific PR.

**CRITICAL**: Only include rules that create REAL decision points. Skip rules that are obviously irrelevant (wrong programming language, clearly unrelated subsystem). We want rules where:
- Two valid rules CONFLICT and the agent must choose (e.g., "inline single-use vars" vs readability)
- The rule's SCOPE is ambiguous (e.g., "create changeset for changes" — but are internal docs "changes"?)
- Following the rule would cause META-LEVEL confusion (e.g., writing ABOUT a tool vs USING that tool)
- Following the rule would cross an ARCHITECTURE BOUNDARY (e.g., applying JSG patterns to internal utilities)
- Following the rule would introduce a BUG or security issue in this context

For each:
- `rule`: The convention that creates a collision
- `source_file`: Which config file contains this rule
- `source_lines`: Approximate line numbers
- `collision_type`: "rule_conflict" | "scope_ambiguity" | "meta_confusion" | "architecture_boundary" | "would_cause_bug"
- `why_distracting`: WHY an agent would plausibly follow this, and what goes WRONG if it does
- `severity`: "high" (following it causes a bug/wrong behavior) | "medium" (wastes significant effort) | "low" (minor confusion)

### SKILL RELEVANCE
For each skill: should the agent activate it? Why / why not?

### HIERARCHY ANALYSIS
If multiple config files apply, note any conflicts or where the deeper file's guidance should override.

Respond with ONLY a JSON object:
{{
  "positive_rubrics": [
    {{"rule": "...", "source_file": "...", "source_lines": "N-M", "evidence_in_gold": "...", "category": "..."}}
  ],
  "negative_rubrics": [
    {{"rule": "...", "source_file": "...", "source_lines": "N-M", "collision_type": "rule_conflict|scope_ambiguity|meta_confusion|architecture_boundary|would_cause_bug", "why_distracting": "what goes wrong if agent follows this", "severity": "high|medium|low"}}
  ],
  "skill_relevance": [
    {{"skill": "...", "relevant": true, "reason": "..."}}
  ],
  "hierarchy_analysis": "one paragraph about how the config levels interact for this PR",
  "summary": "one paragraph assessment of rubric quality and coverage"
}}"""

    return prompt


# ── Main entry point ─────────────────────────────────────────────────────────

def construct_rubrics(task_dir: Path, repo_dir: Path, gemini_key: str) -> dict:
    """Full rubric construction: hierarchy extraction → Gemini analysis.

    Returns structured result with positive + negative rubrics.
    """
    # Phase 1: Extract hierarchy context
    hierarchy = build_hierarchy_context(task_dir, repo_dir)

    if not hierarchy.get("config_hierarchy"):
        return {
            "status": "no_config_files",
            "positive_rubrics": [],
            "negative_rubrics": [],
        }

    # Phase 2: Build and call Gemini
    config_contents = {}
    # Re-read full contents (hierarchy_context only stores truncated)
    for cfg in hierarchy.get("config_hierarchy", []):
        path = cfg["path"]
        full_path = repo_dir / path
        if full_path.exists():
            try:
                config_contents[path] = full_path.read_text(errors="replace")[:5000]
            except Exception:
                pass

    prompt = build_rubric_prompt(task_dir, hierarchy, config_contents)

    if not gemini_key:
        return {"status": "no_gemini_key", "prompt_length": len(prompt)}

    result = call_gemini(prompt, gemini_key)

    if "error" in result:
        return {"status": "gemini_error", **result}

    # Add metadata
    result["status"] = "ok"
    result["hierarchy_depth"] = hierarchy.get("hierarchy_depth", 0)
    result["total_config_rules"] = hierarchy.get("total_config_rules", 0)
    result["edited_paths"] = hierarchy.get("edited_paths", [])
    result["config_files"] = [c["path"] for c in hierarchy.get("config_hierarchy", [])]

    return result


def stamp_rubrics_to_manifest(task_dir: Path, result: dict) -> None:
    """Write positive + negative rubrics into eval_manifest.yaml."""
    if not yaml:
        return

    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return

    manifest = yaml.safe_load(manifest_path.read_text()) or {}

    # Positive rubrics → rubric section (existing format, compatible)
    positive = result.get("positive_rubrics", [])
    if positive:
        rubric_rules = []
        for pr in positive:
            rule = {
                "rule": pr.get("rule", ""),
                "source": {
                    "path": pr.get("source_file", ""),
                    "lines": pr.get("source_lines", ""),
                },
                "category": pr.get("category", ""),
            }
            if pr.get("evidence_in_gold"):
                rule["evidence"] = pr["evidence_in_gold"][:200]
            rubric_rules.append(rule)
        manifest["rubric"] = rubric_rules

    # Negative rubrics → distractors section
    negative = result.get("negative_rubrics", [])
    if negative:
        distractor_rules = []
        for nr in negative:
            distractor_rules.append({
                "rule": nr.get("rule", ""),
                "source": {
                    "path": nr.get("source_file", ""),
                    "lines": nr.get("source_lines", ""),
                },
                "collision_type": nr.get("collision_type", ""),
                "why_distracting": nr.get("why_distracting", ""),
                "severity": nr.get("severity", "medium"),
            })
        manifest["distractors"] = distractor_rules

    # Hierarchy analysis
    if result.get("hierarchy_analysis"):
        manifest["hierarchy_analysis"] = result["hierarchy_analysis"]

    manifest_path.write_text(yaml.dump(
        manifest, default_flow_style=False, sort_keys=False, allow_unicode=True
    ))


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gemini rubric constructor")
    parser.add_argument("--task", required=True, help="Task directory")
    parser.add_argument("--repo", required=True, help="Repo directory at base commit")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--stamp", action="store_true", help="Write results into eval_manifest.yaml")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"')

    result = construct_rubrics(Path(args.task), Path(args.repo), gemini_key)

    # Output
    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output)

    if args.stamp and result.get("status") == "ok":
        stamp_rubrics_to_manifest(Path(args.task), result)

    # Summary to stdout
    pos = len(result.get("positive_rubrics", []))
    neg = len(result.get("negative_rubrics", []))
    print(json.dumps({
        "status": result.get("status"),
        "positive_rubrics": pos,
        "negative_rubrics": neg,
        "hierarchy_depth": result.get("hierarchy_depth"),
        "config_files": result.get("config_files", []),
        "summary": result.get("summary", "")[:200],
    }, indent=2))


if __name__ == "__main__":
    main()
