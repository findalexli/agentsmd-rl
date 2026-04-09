"""Gemini 3.1 Pro judge for rubric rule evaluation.

Evaluates soft rubric rules from eval_manifest.yaml against the gold
solution diff. Called from the orchestrator after Docker validation passes.

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


async def judge_rubric(
    manifest_path: Path,
    solve_sh_path: Path,
    api_key: str | None = None,
    http: httpx.AsyncClient | None = None,
) -> list[dict] | None:
    """Evaluate rubric rules via Gemini 3.1 Pro.

    Returns list of {rule_num, rule, pass, reason} dicts, or None if no rubric.
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

    # Build prompt
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
For each rule, determine if the gold patch follows it. Return a JSON array:
[
  {{"rule_num": 1, "rule": "...", "pass": true, "reason": "..."}},
  ...
]

Only return the JSON array, no other text."""

    own_client = http is None
    if own_client:
        http = httpx.AsyncClient(timeout=60)

    try:
        resp = await http.post(
            f"{GEMINI_API_URL}?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096},
            },
        )

        if resp.status_code != 200:
            return None

        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Extract JSON from response
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]

        return json.loads(text)

    except Exception:
        return None
    finally:
        if own_client:
            await http.aclose()
