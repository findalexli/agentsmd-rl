#!/usr/bin/env python3
"""Standalone LLM judge for Track 3 (rubric) + Track 4 (distractors).

Designed to run INSIDE the harbor container after programmatic tests.
No external dependencies beyond Python stdlib + PyYAML.

Reads eval_manifest.yaml and agent's diff, calls Gemini API for judging.
Writes results to /logs/verifier/track3_rubric.json and track4_distractors.json.

Usage (inside container):
    python3 /tests/standalone_judge.py /tests/eval_manifest.yaml /logs/verifier/agent.diff

Env vars:
    GEMINI_API_KEY — required for LLM judge calls
    ANTHROPIC_API_KEY — fallback if no Gemini key
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

GEMINI_MODEL = "gemini-3.1-pro-preview-customtools"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# ── YAML loading (handles missing PyYAML gracefully) ──────────────────────

def load_yaml(path: str) -> dict:
    """Load YAML file. Tries PyYAML, falls back to basic parsing."""
    text = Path(path).read_text()
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    # Minimal YAML-ish parser for our schema (handles simple key-value + lists)
    return _parse_yaml_minimal(text)


def _parse_yaml_minimal(text: str) -> dict:
    """Bare-minimum YAML parser for eval_manifest.yaml structure."""
    import re
    data = {}
    current_list_key = None
    current_item = None
    items = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Top-level key
        if not line.startswith(" ") and not line.startswith("\t"):
            if current_list_key and items:
                data[current_list_key] = items
                items = []
            m = re.match(r"(\w+):\s*(.*)", stripped)
            if m:
                key, val = m.group(1), m.group(2).strip().strip("'\"")
                if not val:
                    current_list_key = key
                else:
                    data[key] = val
                    current_list_key = None
            continue

        # List item
        if stripped.startswith("- "):
            if current_item is not None:
                items.append(current_item)
            rest = stripped[2:].strip()
            m = re.match(r"(\w+):\s*(.*)", rest)
            if m:
                current_item = {m.group(1): m.group(2).strip().strip("'\"").rstrip("'")}
            else:
                current_item = rest
            continue

        # Nested key inside list item
        if current_item is not None and isinstance(current_item, dict):
            m = re.match(r"\s+(\w+):\s*(.*)", line)
            if m:
                val = m.group(2).strip().strip("'\"").rstrip("'")
                current_item[m.group(1)] = val

    if current_item is not None:
        items.append(current_item)
    if current_list_key and items:
        data[current_list_key] = items

    return data


# ── Gemini API ────────────────────────────────────────────────────────────

def _call_gemini(prompt: str, api_key: str, schema: dict) -> list[dict]:
    """Call Gemini with structured output."""
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    }).encode()

    req = urllib.request.Request(
        GEMINI_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return json.loads(text)
    except Exception as e:
        print(f"  [judge] Gemini call failed: {e}", file=sys.stderr)
        return []


def _call_anthropic(prompt: str, api_key: str) -> list[dict]:
    """Fallback: call Anthropic Claude Haiku."""
    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        text = data["content"][0]["text"].strip()
        if text.startswith("["):
            return json.loads(text)
        s, e = text.find("["), text.rfind("]") + 1
        return json.loads(text[s:e]) if s >= 0 and e > s else []
    except Exception as e:
        print(f"  [judge] Anthropic call failed: {e}", file=sys.stderr)
        return []


# ── Track 3: Rubric judge ─────────────────────────────────────────────────

_RUBRIC_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "rule_num": {"type": "integer"},
            "reasoning": {"type": "string"},
            "pass": {"type": "boolean"},
        },
        "required": ["rule_num", "reasoning", "pass"],
        "propertyOrdering": ["rule_num", "reasoning", "pass"],
    },
}


def judge_rubric(rules: list[dict], diff: str, gemini_key: str, anthropic_key: str) -> dict:
    """Track 3: Evaluate agent's code against convention rules."""
    if not rules:
        return {"score": 1.0, "passed": 0, "total": 0, "results": []}

    eval_items = []
    for i, r in enumerate(rules):
        item = f"Rule {i+1}: {r.get('rule', '')}"
        src = r.get("source")
        if isinstance(src, dict):
            item += f"\n  Convention source: {src.get('path', '?')}"
            if src.get("lines"):
                item += f", lines {src['lines']}"
        if r.get("source_text"):
            item += f"\n  Config text: {str(r['source_text'])[:300]}"
        if r.get("evidence"):
            item += f"\n  Gold evidence: {str(r['evidence'])[:400]}"
        elif r.get("reference"):
            item += f"\n  Gold reference: {str(r['reference'])[:400]}"
        eval_items.append(item)

    prompt = f"""You are evaluating whether a coding agent's code changes follow specific conventions from the repository's config files (CLAUDE.md, AGENTS.md, etc.).

The agent was given a bug-fix task. Below are conventions from the repo's config that the gold (correct) solution follows. For each rule, examine the agent's diff and decide: does the agent's code follow this convention?

Rules to evaluate:
{chr(10).join(eval_items)}

Agent's full diff:
```diff
{diff[:40000]}
```

For each rule, decide:
- PASS: The agent's code changes clearly follow this convention
- PASS: The convention is about something the agent didn't need to touch (not applicable)
- FAIL: The agent's code visibly violates this convention
- FAIL: The convention directly applies to the agent's changes but was not followed

Be generous — minor style differences are fine. Focus on whether the spirit of the convention was respected.

Respond with ONLY a JSON array:
[{{"rule_num": N, "pass": true/false, "reasoning": "one sentence"}}]"""

    if gemini_key:
        results = _call_gemini(prompt, gemini_key, _RUBRIC_SCHEMA)
    elif anthropic_key:
        results = _call_anthropic(prompt, anthropic_key)
    else:
        return {"score": 0.5, "passed": 0, "total": len(rules), "results": [], "error": "no API key"}

    passed = sum(1 for r in results if r.get("pass", False))
    return {
        "score": passed / len(rules) if rules else 1.0,
        "passed": passed,
        "total": len(rules),
        "results": results,
    }


# ── Track 4: Distractor judge ────────────────────────────────────────────

_DISTRACTOR_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "rule_num": {"type": "integer"},
            "applied": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["rule_num", "applied", "reason"],
    },
}


def judge_distractors(distractors: list[dict], diff: str, gemini_key: str, anthropic_key: str) -> dict:
    """Track 4: Check if agent incorrectly applied distractor rules."""
    if not distractors:
        return {"score": 1.0, "passed": 0, "total": 0, "results": []}

    items = []
    for i, d in enumerate(distractors):
        line = f"Distractor {i+1}: {d.get('rule', '')}"
        if d.get("why_distracting"):
            line += f"\n  Why distracting: {d['why_distracting']}"
        if d.get("severity"):
            line += f"  (severity: {d['severity']})"
        items.append(line)

    prompt = f"""You are evaluating whether a coding agent **incorrectly applied** a set of distractor rules to its code changes.

Distractor rules are conventions from the repo's agent config files that **look relevant** but are actually **wrong to apply** here — the gold solution correctly ignores each of them.

For each distractor, decide whether the agent's diff shows the rule being applied.

Distractors:
{chr(10).join(items)}

Agent diff:
```diff
{diff[:40000]}
```

For each distractor:
- applied=true  → the agent visibly followed the distractor (FAIL)
- applied=false → the agent correctly ignored the distractor (PASS)

Respond with ONLY a JSON array:
[{{"rule_num": N, "applied": true/false, "reason": "one short sentence"}}]"""

    if gemini_key:
        results = _call_gemini(prompt, gemini_key, _DISTRACTOR_SCHEMA)
    elif anthropic_key:
        results = _call_anthropic(prompt, anthropic_key)
    else:
        return {"score": 0.5, "passed": 0, "total": len(distractors), "results": [], "error": "no API key"}

    passed = sum(1 for r in results if not r.get("applied", False))
    return {
        "score": passed / len(distractors) if distractors else 1.0,
        "passed": passed,
        "total": len(distractors),
        "results": results,
    }


# ── Diff capture ──────────────────────────────────────────────────────────

def capture_diff() -> str:
    """Capture agent's changes as a unified diff."""
    # Find the git repo
    for candidate in ["/workspace", "/repo", "/app", "/src"]:
        for d in Path(candidate).glob("*/.git") if Path(candidate).exists() else []:
            repo = d.parent
            try:
                subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True)
                result = subprocess.run(
                    ["git", "diff", "--cached"],
                    cwd=repo, capture_output=True, text=True,
                )
                if result.stdout.strip():
                    return result.stdout[:50000]
            except Exception:
                pass
        # Also check the candidate itself
        if Path(candidate).exists() and Path(f"{candidate}/.git").exists():
            try:
                subprocess.run(["git", "add", "-A"], cwd=candidate, capture_output=True)
                result = subprocess.run(
                    ["git", "diff", "--cached"],
                    cwd=candidate, capture_output=True, text=True,
                )
                if result.stdout.strip():
                    return result.stdout[:50000]
            except Exception:
                pass
    return ""


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: standalone_judge.py <eval_manifest.yaml> [agent.diff]", file=sys.stderr)
        sys.exit(1)

    manifest_path = sys.argv[1]
    diff_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Load manifest
    manifest = load_yaml(manifest_path)
    rubric = manifest.get("rubric") or []
    distractors = manifest.get("distractors") or []

    if not rubric and not distractors:
        print("  [judge] No rubric or distractors in manifest, skipping", file=sys.stderr)
        # Write empty results
        Path("/logs/verifier/track3_rubric.json").write_text("{}")
        Path("/logs/verifier/track4_distractors.json").write_text("{}")
        return

    # Get diff
    if diff_path and Path(diff_path).exists():
        diff = Path(diff_path).read_text()
    else:
        diff = capture_diff()

    if not diff:
        print("  [judge] No diff found, skipping LLM judge", file=sys.stderr)
        Path("/logs/verifier/track3_rubric.json").write_text(json.dumps(
            {"score": 0.0, "passed": 0, "total": len(rubric), "error": "no diff"}
        ))
        Path("/logs/verifier/track4_distractors.json").write_text(json.dumps(
            {"score": 0.0, "passed": 0, "total": len(distractors), "error": "no diff"}
        ))
        return

    # Save diff if not already saved
    diff_out = Path("/logs/verifier/agent.diff")
    if not diff_out.exists() or diff_out.stat().st_size == 0:
        diff_out.write_text(diff)

    # API keys
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not gemini_key and not anthropic_key:
        print("  [judge] No GEMINI_API_KEY or ANTHROPIC_API_KEY, skipping", file=sys.stderr)
        return

    # Track 3: Rubric
    if rubric:
        print(f"  [judge] Track 3: evaluating {len(rubric)} rubric rules...", file=sys.stderr)
        t3 = judge_rubric(rubric, diff, gemini_key, anthropic_key)
        Path("/logs/verifier/track3_rubric.json").write_text(json.dumps(t3, indent=2))
        print(f"  [judge] Track 3: {t3['passed']}/{t3['total']} passed (score={t3['score']:.2f})", file=sys.stderr)

    # Track 4: Distractors
    if distractors:
        print(f"  [judge] Track 4: evaluating {len(distractors)} distractors...", file=sys.stderr)
        t4 = judge_distractors(distractors, diff, gemini_key, anthropic_key)
        Path("/logs/verifier/track4_distractors.json").write_text(json.dumps(t4, indent=2))
        print(f"  [judge] Track 4: {t4['passed']}/{t4['total']} ignored (score={t4['score']:.2f})", file=sys.stderr)


if __name__ == "__main__":
    main()
