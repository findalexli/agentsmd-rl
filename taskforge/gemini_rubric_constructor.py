#!/usr/bin/env python3
"""Gemini-powered rubric constructor with structured output + Kimi validation.

Feeds the FULL config hierarchy + gold solution + instruction to Gemini 3.1 Pro
using constrained decoding (responseSchema) for guaranteed-consistent output.

Optional Kimi→Gemini→Kimi loop:
  1. Gemini generates structured rubrics (constrained decoding)
  2. Kimi validates each rubric against actual repo config files
  3. Gemini resolves any disagreements (structured follow-up)

Usage (standalone):
    python3 -m taskforge.gemini_rubric_constructor \
        --task harbor_tasks_agentmd_edits/opencode-acp-question-tool-flag \
        --repo /tmp/repos/opencode

    # With Kimi validation:
    python3 -m taskforge.gemini_rubric_constructor \
        --task ... --repo ... --kimi-validate
"""

from __future__ import annotations

import argparse
import json
import os
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


# ── Gemini structured output schemas ────────────────────────────────────────

GEMINI_MODEL = "gemini-3.1-pro-preview-customtools"

# Schema for positive rubric items.
# propertyOrdering: source/evidence BEFORE rule — model reasons before committing.
_POSITIVE_RUBRIC_SCHEMA = {
    "type": "object",
    "properties": {
        "source_file": {"type": "string", "description": "Config file path (repo-relative)"},
        "source_lines": {"type": "string", "description": "Line range, e.g. '28-32'"},
        "evidence_in_gold": {"type": "string", "description": "How the gold solution demonstrates compliance"},
        "category": {
            "type": "string",
            "enum": ["naming", "style", "architecture", "testing", "documentation", "tooling"],
        },
        "rule": {"type": "string", "description": "The convention being followed"},
    },
    "required": ["source_file", "evidence_in_gold", "rule"],
    "propertyOrdering": ["source_file", "source_lines", "evidence_in_gold", "category", "rule"],
}

# Schema for negative rubric (distractor) items.
# propertyOrdering: source/reasoning BEFORE collision_type — think then classify.
_NEGATIVE_RUBRIC_SCHEMA = {
    "type": "object",
    "properties": {
        "source_file": {"type": "string", "description": "Config file containing the rule"},
        "source_lines": {"type": "string", "description": "Line range"},
        "why_distracting": {"type": "string", "description": "Why following this rule hurts this PR"},
        "collision_type": {
            "type": "string",
            "enum": ["rule_conflict", "scope_ambiguity", "meta_confusion",
                     "architecture_boundary", "would_cause_bug"],
        },
        "severity": {
            "type": "string",
            "enum": ["high", "medium", "low"],
        },
        "rule": {"type": "string", "description": "The convention that creates a collision"},
    },
    "required": ["source_file", "why_distracting", "collision_type", "rule"],
    "propertyOrdering": ["source_file", "source_lines", "why_distracting", "collision_type", "severity", "rule"],
}

# Top-level response schema for construct_rubrics.
RUBRIC_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "positive_rubrics": {
            "type": "array",
            "items": _POSITIVE_RUBRIC_SCHEMA,
        },
        "negative_rubrics": {
            "type": "array",
            "items": _NEGATIVE_RUBRIC_SCHEMA,
        },
        "hierarchy_analysis": {"type": "string"},
        "summary": {"type": "string"},
    },
    "required": ["positive_rubrics", "negative_rubrics"],
    "propertyOrdering": ["positive_rubrics", "negative_rubrics", "hierarchy_analysis", "summary"],
}

# Combined schema: rubric construction + quality classification in ONE call.
# Saves ~50% latency vs two sequential calls.
COMBINED_RUBRIC_QUALITY_SCHEMA = {
    "type": "object",
    "properties": {
        "positive_rubrics": {
            "type": "array",
            "items": _POSITIVE_RUBRIC_SCHEMA,
        },
        "negative_rubrics": {
            "type": "array",
            "items": _NEGATIVE_RUBRIC_SCHEMA,
        },
        "hierarchy_analysis": {"type": "string"},
        "quality_verdict": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW", "DELETE"],
        },
        "quality_reasoning": {"type": "string"},
        "meta_referential": {
            "type": "boolean",
            "description": "Must the agent edit/override its own instruction files?",
        },
        "competing_principles": {
            "type": "boolean",
            "description": "Do config rules conflict, requiring the agent to choose?",
        },
        "config_navigation": {
            "type": "string",
            "enum": ["deep_hierarchy", "moderate", "flat_single_file", "none"],
        },
    },
    "required": ["positive_rubrics", "negative_rubrics", "quality_verdict", "quality_reasoning"],
    "propertyOrdering": [
        "positive_rubrics", "negative_rubrics", "hierarchy_analysis",
        "config_navigation", "meta_referential", "competing_principles",
        "quality_reasoning", "quality_verdict",
    ],
}


# Schema for Kimi validation verdicts (Gemini follow-up).
KIMI_VALIDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "rubric_verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "type": {"type": "string", "enum": ["positive", "negative"]},
                    "reasoning": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["confirmed", "revised", "rejected"]},
                    "revised_rule": {"type": "string"},
                },
                "required": ["index", "type", "reasoning", "verdict"],
                "propertyOrdering": ["index", "type", "reasoning", "verdict", "revised_rule"],
            },
        },
        "additional_rules": {
            "type": "array",
            "items": _POSITIVE_RUBRIC_SCHEMA,
            "description": "Rules Kimi found that Gemini missed",
        },
        "additional_distractors": {
            "type": "array",
            "items": _NEGATIVE_RUBRIC_SCHEMA,
            "description": "Distractors Kimi found that Gemini missed",
        },
        "summary": {"type": "string"},
    },
    "required": ["rubric_verdicts"],
    "propertyOrdering": ["rubric_verdicts", "additional_rules", "additional_distractors", "summary"],
}


# ── Gemini API call with structured output ──────────────────────────────────

def call_gemini(
    prompt: str,
    gemini_key: str,
    *,
    schema: dict | None = None,
    system_instruction: str = "",
    max_tokens: int = 8192,
    temperature: float = 0.1,
) -> dict:
    """Call Gemini with optional structured output (constrained decoding).

    When schema is provided, uses responseMimeType + responseSchema for
    guaranteed-valid JSON. No manual parsing needed.

    When schema is None, falls back to freeform text with JSON extraction.
    """
    import urllib.request  # noqa: lazy import for standalone use

    gen_config: dict = {
        "temperature": temperature,
        "maxOutputTokens": max_tokens,
    }
    if schema is not None:
        gen_config["responseMimeType"] = "application/json"
        gen_config["responseSchema"] = schema

    body: dict = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": gen_config,
    }
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": gemini_key,
        },
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    # Extract text from response
    candidates = data.get("candidates", [])
    if not candidates:
        return {"error": "no_candidates", "raw": json.dumps(data)[:500]}

    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        # Structured output may hit MAX_TOKENS — check finishReason
        reason = candidates[0].get("finishReason", "")
        return {"error": f"no_parts (finishReason={reason})", "raw": ""}

    text = parts[0].get("text", "").strip()

    # With structured output, response is already valid JSON
    if schema is not None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"error": "structured_parse_failed", "raw": text[:500]}

    # Freeform fallback: extract JSON from markdown fences
    return _extract_json_from_text(text)


def _extract_json_from_text(text: str) -> dict:
    """Extract JSON from freeform Gemini response (markdown fences, etc.)."""
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
        if text.startswith("{") or text.startswith("["):
            return json.loads(text)
        s = text.find("{")
        e = text.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(text[s:e])
    except json.JSONDecodeError:
        pass

    return {"error": "parse_failed", "raw": text[:500]}


# ── Kimi API call (Fireworks, Anthropic Messages format) ────────────────────

KIMI_MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/messages"


def call_kimi(
    messages: list[dict],
    *,
    system: str = "",
    max_tokens: int = 8192,
) -> str | None:
    """Call Kimi K2.5 via Fireworks API. Returns text response or None on error."""
    import urllib.request

    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    if not api_key:
        return None

    body: dict = {
        "model": KIMI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if system:
        body["system"] = system

    req = urllib.request.Request(
        FIREWORKS_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        # Anthropic Messages format response
        content = data.get("content", [])
        if content and isinstance(content, list):
            return content[0].get("text", "")
        return None
    except Exception:
        return None


# ── Build prompt ────────────────────────────────────────────────────────────

def build_rubric_prompt(
    task_dir: Path,
    hierarchy: dict,
    config_contents: dict,
) -> str:
    """Build the Gemini prompt with full hierarchy context.

    With structured output, we don't need to specify the JSON format in the
    prompt — the responseSchema handles that. We just describe WHAT to analyze.
    """

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

    # Existing rubric/config_edits for context
    if yaml:
        manifest_path = task_dir / "eval_manifest.yaml"
        if manifest_path.exists():
            try:
                m = yaml.safe_load(manifest_path.read_text())
                config_edits = m.get("config_edits", [])
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

Analyze the full config hierarchy above and the gold solution.

### POSITIVE RUBRICS
Rules from the config files that the gold solution FOLLOWS. Only include rules where you can point to SPECIFIC evidence in the gold diff. Think about the source file and evidence first, then state the rule.

### NEGATIVE RUBRICS (DISTRACTORS)
Rules that create genuine COLLISIONS — where an agent would plausibly try to follow the rule, but doing so would produce WORSE code or wasted effort for this specific PR.

**CRITICAL**: Only include rules that create REAL decision points. Skip rules that are obviously irrelevant (wrong programming language, clearly unrelated subsystem). We want rules where:
- Two valid rules CONFLICT and the agent must choose
- The rule's SCOPE is ambiguous for this PR
- Following the rule would cause META-LEVEL confusion
- Following the rule would cross an ARCHITECTURE BOUNDARY
- Following the rule would introduce a BUG in this context

Think about why the rule is distracting and what goes wrong before classifying the collision type.

### HIERARCHY ANALYSIS
If multiple config files apply, note conflicts or where deeper file guidance should override."""

    return prompt


# ── Kimi validation prompt ──────────────────────────────────────────────────

def build_kimi_validation_prompt(
    gemini_result: dict,
    config_contents: dict,
    instruction: str,
    solve_text: str,
) -> str:
    """Build prompt for Kimi to validate Gemini's rubrics against actual config files."""

    rubrics_text = ""
    for i, r in enumerate(gemini_result.get("positive_rubrics", [])):
        rubrics_text += f"\n[P{i}] Rule: {r.get('rule', '')}"
        rubrics_text += f"\n     Source: {r.get('source_file', '')}:{r.get('source_lines', '')}"
        rubrics_text += f"\n     Evidence: {r.get('evidence_in_gold', '')}"
        rubrics_text += f"\n     Category: {r.get('category', '')}\n"

    for i, d in enumerate(gemini_result.get("negative_rubrics", [])):
        rubrics_text += f"\n[N{i}] Rule: {d.get('rule', '')}"
        rubrics_text += f"\n     Source: {d.get('source_file', '')}:{d.get('source_lines', '')}"
        rubrics_text += f"\n     Collision: {d.get('collision_type', '')} ({d.get('severity', '')})"
        rubrics_text += f"\n     Why distracting: {d.get('why_distracting', '')}\n"

    configs_text = ""
    for path, content in config_contents.items():
        configs_text += f"\n### {path}\n```\n{content[:3000]}\n```\n"

    return f"""You are validating rubric rules that Gemini extracted from a coding task's config hierarchy.

## Task Instruction
{instruction[:1500]}

## Gold Solution (solve.sh)
```bash
{solve_text[:3000]}
```

## Actual Config File Contents
{configs_text}

## Gemini's Proposed Rubrics
{rubrics_text}

## Gemini's Analysis
{gemini_result.get('hierarchy_analysis', '')}

## Your Job

For EACH proposed rubric (positive and negative), verify:

1. **Source exists**: Does the rule actually appear in the cited config file at roughly those lines?
2. **Evidence is real**: For positives — does the gold solution actually demonstrate this? For negatives — would following this rule actually cause the described collision?
3. **Classification is correct**: Is the category/collision_type accurate?

For each rule, respond with a JSON object containing your verdict. Also suggest any rules Gemini missed.

Respond with ONLY a JSON object:
{{
  "rubric_verdicts": [
    {{"index": 0, "type": "positive", "reasoning": "...", "verdict": "confirmed|revised|rejected", "revised_rule": "only if revised"}}
  ],
  "additional_rules": [...],
  "additional_distractors": [...],
  "summary": "overall assessment"
}}"""


# ── Main entry points ───────────────────────────────────────────────────────

def construct_rubrics(task_dir: Path, repo_dir: Path, gemini_key: str) -> dict:
    """Gemini-only rubric construction with structured output.

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

    # Phase 2: Read config contents
    config_contents = {}
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

    # Phase 3: Call Gemini with structured output
    result = call_gemini(
        prompt,
        gemini_key,
        schema=RUBRIC_RESPONSE_SCHEMA,
        system_instruction=(
            "You are a rubric constructor for coding agent evaluation. "
            "Extract positive rubrics (rules the gold solution follows) and "
            "negative rubrics (distractors that create genuine collisions). "
            "Be precise about source files and line numbers. "
            "Think carefully about evidence before stating each rule."
        ),
    )

    if "error" in result:
        return {"status": "gemini_error", **result}

    # Add metadata
    result["status"] = "ok"
    result["hierarchy_depth"] = hierarchy.get("hierarchy_depth", 0)
    result["total_config_rules"] = hierarchy.get("total_config_rules", 0)
    result["edited_paths"] = hierarchy.get("edited_paths", [])
    result["config_files"] = [c["path"] for c in hierarchy.get("config_hierarchy", [])]

    return result


def construct_and_classify(task_dir: Path, repo_dir: Path, gemini_key: str) -> dict:
    """Combined rubric construction + quality classification in ONE Gemini call.

    Returns everything construct_rubrics returns PLUS quality_verdict,
    quality_reasoning, meta_referential, competing_principles, config_navigation.

    ~50% faster than calling construct_rubrics + classify_task separately.
    Designed for the E2B pipeline where both are needed.
    """
    # Phase 1: Extract hierarchy context
    hierarchy = build_hierarchy_context(task_dir, repo_dir)

    if not hierarchy.get("config_hierarchy"):
        return {
            "status": "no_config_files",
            "positive_rubrics": [],
            "negative_rubrics": [],
            "quality_verdict": "DELETE",
            "quality_reasoning": "No config files in hierarchy",
        }

    # Phase 2: Read config contents
    config_contents = {}
    for cfg in hierarchy.get("config_hierarchy", []):
        path = cfg["path"]
        full_path = repo_dir / path
        if full_path.exists():
            try:
                config_contents[path] = full_path.read_text(errors="replace")[:5000]
            except Exception:
                pass

    prompt = build_rubric_prompt(task_dir, hierarchy, config_contents)

    # Append quality classification instructions to the same prompt
    prompt += """

## ADDITIONALLY: Classify this task for research relevance.

After constructing rubrics, also assess:
- quality_verdict: HIGH (agent must reason about competing instructions or config hierarchy),
  MEDIUM (real code with shallow config signal), LOW (trivial config edit), DELETE (no config)
- meta_referential: must the agent edit/override its own instruction files?
- competing_principles: do config rules conflict for this task?
- config_navigation: depth of config hierarchy traversal needed

HIGH = removing config files would make the task meaningfully harder.
LOW = config edit is mechanical or disconnected from code."""

    if not gemini_key:
        return {"status": "no_gemini_key", "prompt_length": len(prompt)}

    # Single Gemini call with combined schema
    result = call_gemini(
        prompt,
        gemini_key,
        schema=COMBINED_RUBRIC_QUALITY_SCHEMA,
        system_instruction=(
            "You are a rubric constructor AND quality auditor for coding agent evaluation. "
            "First extract positive rubrics and distractors. Then classify whether this task "
            "genuinely tests instruction discrimination. Be precise about sources. "
            "Even if the instruction mentions which file to edit, the task can be HIGH if "
            "writing the correct content requires understanding competing conventions."
        ),
        max_tokens=8192,
    )

    if "error" in result:
        return {"status": "gemini_error", **result}

    # Add metadata
    result["status"] = "ok"
    result["hierarchy_depth"] = hierarchy.get("hierarchy_depth", 0)
    result["total_config_rules"] = hierarchy.get("total_config_rules", 0)
    result["edited_paths"] = hierarchy.get("edited_paths", [])
    result["config_files"] = [c["path"] for c in hierarchy.get("config_hierarchy", [])]

    return result


def construct_rubrics_with_kimi(
    task_dir: Path,
    repo_dir: Path,
    gemini_key: str,
) -> dict:
    """3-step Gemini→Kimi→Gemini rubric construction with cross-validation.

    Step 1: Gemini generates structured rubrics (constrained decoding)
    Step 2: Kimi validates each rubric against actual config files
    Step 3: Apply Kimi's verdicts (confirm/revise/reject) to produce final rubrics

    Falls back to Gemini-only if Kimi is unavailable.
    """
    # Step 1: Gemini generates
    result = construct_rubrics(task_dir, repo_dir, gemini_key)
    if result.get("status") != "ok":
        return result

    # Check if Kimi is available
    if not os.environ.get("FIREWORKS_API_KEY"):
        result["kimi_validated"] = False
        return result

    # Prepare context for Kimi
    config_contents = {}
    hierarchy = build_hierarchy_context(task_dir, repo_dir)
    for cfg in hierarchy.get("config_hierarchy", []):
        path = cfg["path"]
        full_path = repo_dir / path
        if full_path.exists():
            try:
                config_contents[path] = full_path.read_text(errors="replace")[:3000]
            except Exception:
                pass

    instruction = ""
    instr_path = task_dir / "instruction.md"
    if instr_path.exists():
        instruction = instr_path.read_text()[:1500]

    solve_text = ""
    solve_path = task_dir / "solution" / "solve.sh"
    if solve_path.exists():
        solve_text = solve_path.read_text()[:3000]

    # Step 2: Kimi validates
    kimi_prompt = build_kimi_validation_prompt(
        result, config_contents, instruction, solve_text,
    )
    kimi_response = call_kimi(
        [{"role": "user", "content": kimi_prompt}],
        system="You are a precise rubric validator. Check each rule against the actual config files and gold solution. Respond with ONLY valid JSON.",
    )

    if not kimi_response:
        result["kimi_validated"] = False
        return result

    # Parse Kimi's validation
    kimi_result = _extract_json_from_text(kimi_response)
    if "error" in kimi_result:
        result["kimi_validated"] = False
        result["kimi_parse_error"] = kimi_result.get("error", "")
        return result

    # Step 3: Apply verdicts
    verdicts = kimi_result.get("rubric_verdicts", [])
    confirmed_positive = []
    confirmed_negative = []

    pos_rubrics = result.get("positive_rubrics", [])
    neg_rubrics = result.get("negative_rubrics", [])

    for v in verdicts:
        idx = v.get("index", -1)
        verdict = v.get("verdict", "confirmed")
        rtype = v.get("type", "positive")

        if verdict == "rejected":
            continue  # Drop rejected rules

        if rtype == "positive" and 0 <= idx < len(pos_rubrics):
            rule = pos_rubrics[idx].copy()
            if verdict == "revised" and v.get("revised_rule"):
                rule["rule"] = v["revised_rule"]
            confirmed_positive.append(rule)
        elif rtype == "negative" and 0 <= idx < len(neg_rubrics):
            rule = neg_rubrics[idx].copy()
            if verdict == "revised" and v.get("revised_rule"):
                rule["rule"] = v["revised_rule"]
            confirmed_negative.append(rule)

    # Add any additional rules Kimi found
    for extra in kimi_result.get("additional_rules", []):
        if extra.get("rule"):
            confirmed_positive.append(extra)
    for extra in kimi_result.get("additional_distractors", []):
        if extra.get("rule"):
            confirmed_negative.append(extra)

    result["positive_rubrics"] = confirmed_positive
    result["negative_rubrics"] = confirmed_negative
    result["kimi_validated"] = True
    result["kimi_verdicts"] = {
        "total": len(verdicts),
        "confirmed": sum(1 for v in verdicts if v.get("verdict") == "confirmed"),
        "revised": sum(1 for v in verdicts if v.get("verdict") == "revised"),
        "rejected": sum(1 for v in verdicts if v.get("verdict") == "rejected"),
    }

    return result


# ── Stamp results to manifest ──────────────────────────────────────────────

def _to_rubric_dict(pr: dict) -> dict:
    """Convert Gemini positive rubric output to canonical RubricRule dict."""
    d = {"rule": pr.get("rule", "")}
    src_path = pr.get("source_file", "")
    if src_path:
        d["source"] = {"path": src_path, "lines": str(pr.get("source_lines", ""))}
    if pr.get("evidence_in_gold"):
        d["evidence"] = pr["evidence_in_gold"][:200]
    if pr.get("category"):
        d["category"] = pr["category"]
    return d


def _to_distractor_dict(nr: dict) -> dict:
    """Convert Gemini negative rubric output to canonical DistractorRule dict."""
    d = {
        "rule": nr.get("rule", ""),
        "collision_type": nr.get("collision_type", ""),
        "why_distracting": nr.get("why_distracting", ""),
        "severity": nr.get("severity", "medium"),
    }
    src_path = nr.get("source_file", "")
    if src_path:
        d["source"] = {"path": src_path, "lines": str(nr.get("source_lines", ""))}
    return d


def stamp_rubrics_to_manifest(task_dir: Path, result: dict) -> None:
    """Write positive + negative rubrics into eval_manifest.yaml.

    Uses canonical field sets matching Pydantic models (RubricRule, DistractorRule).
    Merges new positive rubrics with existing ones (dedup by rule text).
    """
    if not yaml:
        return

    manifest_path = task_dir / "eval_manifest.yaml"
    if not manifest_path.exists():
        return

    manifest = yaml.safe_load(manifest_path.read_text()) or {}

    # Positive rubrics → merge (keep existing, add new, dedup by rule text)
    positive = result.get("positive_rubrics", [])
    if positive:
        existing_rubric = manifest.get("rubric", [])
        existing_rules = {r.get("rule", "") for r in existing_rubric if isinstance(r, dict)}
        for pr in positive:
            rule_text = pr.get("rule", "")
            if rule_text and rule_text not in existing_rules:
                existing_rubric.append(_to_rubric_dict(pr))
                existing_rules.add(rule_text)
        manifest["rubric"] = existing_rubric

    # Negative rubrics → distractors (replace, since Gemini sees full context)
    negative = result.get("negative_rubrics", [])
    if negative:
        manifest["distractors"] = [_to_distractor_dict(nr) for nr in negative]

    # Hierarchy analysis (informational, not scored)
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
    parser.add_argument("--kimi-validate", action="store_true",
                        help="Use Kimi to validate Gemini's rubrics")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"')

    task_dir = Path(args.task)
    repo_dir = Path(args.repo)

    if args.kimi_validate:
        result = construct_rubrics_with_kimi(task_dir, repo_dir, gemini_key)
    else:
        result = construct_rubrics(task_dir, repo_dir, gemini_key)

    # Output
    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output)

    if args.stamp and result.get("status") == "ok":
        stamp_rubrics_to_manifest(task_dir, result)

    # Summary to stdout
    pos = len(result.get("positive_rubrics", []))
    neg = len(result.get("negative_rubrics", []))
    summary = {
        "status": result.get("status"),
        "positive_rubrics": pos,
        "negative_rubrics": neg,
        "hierarchy_depth": result.get("hierarchy_depth"),
        "config_files": result.get("config_files", []),
        "summary": result.get("summary", "")[:200],
    }
    if result.get("kimi_validated") is not None:
        summary["kimi_validated"] = result["kimi_validated"]
        if result.get("kimi_verdicts"):
            summary["kimi_verdicts"] = result["kimi_verdicts"]
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
