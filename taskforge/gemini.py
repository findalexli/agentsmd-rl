"""Gemini judge for rubric rule evaluation (async httpx).

Evaluates soft rubric rules from eval_manifest.yaml against the gold
solution diff. Called from the orchestrator after Docker validation passes.

Uses structured output (responseSchema) for guaranteed-valid JSON.

Usage:
    from taskforge.gemini import judge_rubric
    results = await judge_rubric(manifest_path, solve_sh_path, api_key)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

# Structured output schema — reasoning before verdict (propertyOrdering).
_RUBRIC_JUDGE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "rule_num": {"type": "integer"},
            "rule": {"type": "string"},
            "reason": {"type": "string"},
            "pass": {"type": "boolean"},
        },
        "required": ["rule_num", "reason", "pass"],
        "propertyOrdering": ["rule_num", "rule", "reason", "pass"],
    },
}


async def judge_rubric(
    manifest_path: Path,
    solve_sh_path: Path,
    api_key: str | None = None,
    http: httpx.AsyncClient | None = None,
) -> list[dict] | None:
    """Evaluate rubric rules via Gemini with structured output.

    Returns list of {rule_num, rule, reason, pass} dicts, or None if no rubric.
    """
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    import yaml
    manifest = yaml.safe_load(manifest_path.read_text())
    rubric = manifest.get("rubric", [])
    if not rubric:
        return None

    solve_diff = solve_sh_path.read_text()

    # Build prompt — no need to specify JSON format (schema handles it)
    rules_text = "\n".join(
        f"{i+1}. {r['rule']}" + (f" (source: {r['source']['path']}:{r['source'].get('lines', '')})" if r.get('source') else "")
        for i, r in enumerate(rubric)
    )

    prompt = f"""You are evaluating whether a code patch follows a set of style/convention rules.

## Rules to evaluate:
{rules_text}

## Gold patch (solve.sh):
```
{solve_diff[:8000]}
```

## Task:
For each rule, determine if the gold patch follows it. Explain your reasoning before giving the verdict."""

    own_client = http is None
    if own_client:
        http = httpx.AsyncClient(timeout=60)

    try:
        resp = await http.post(
            GEMINI_API_URL,
            headers={"x-goog-api-key": api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 4096,
                    "responseMimeType": "application/json",
                    "responseSchema": _RUBRIC_JUDGE_SCHEMA,
                },
            },
        )

        if resp.status_code != 200:
            return None

        data = resp.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        if not parts:
            return None

        return json.loads(parts[0].get("text", "[]"))

    except Exception:
        return None
    finally:
        if own_client:
            await http.aclose()
