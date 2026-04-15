"""LLM judge for task quality.

Reads a task directory, invokes the Anthropic API once, and returns verdicts
for all `llm_judge`-type rubrics. Single-call-per-task design — the prompt
bundles all rubrics so the model evaluates them in one pass.

We use a SEPARATE env var (JUDGE_API_KEY) so the judge always hits the real
Anthropic endpoint even when the surrounding executor is pool'd through
MiniMax/GLM/Kimi via ANTHROPIC_BASE_URL overrides.

Cost estimate: ~4-8k input tokens × ~600 output tokens per task at Opus 4.6 rates
≈ $0.08-0.12 per task. For 1100 tasks: ~$100 full retrofit.

Usage:
    from pathlib import Path
    from taskforge.quality_judge import judge_task
    result = judge_task(Path("harbor_tasks/my-task"))
    if result["tier_a_fails"]:
        print("quality judge flagged:", result["tier_a_fails"])
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from taskforge.rubrics import LLM_JUDGE, Rubric


JUDGE_API_ENV = "JUDGE_API_KEY"
JUDGE_API_URL = "https://api.anthropic.com/v1/messages"
# Opus 4.6 — our best-quality model. The model ID convention
# (claude-opus-4-6) is the stable alias; [1m] is only in model names.
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-4-6")


# ─── Prompt construction ───────────────────────────────────────────────────

def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n… [truncated at {limit} chars]"


def _read(path: Path, limit: int) -> str:
    if not path.exists():
        return "(missing)"
    try:
        return _truncate(path.read_text(errors="ignore"), limit)
    except Exception as e:
        return f"(read error: {e})"


def _rubric_block(r: Rubric) -> str:
    q = r.judge_prompt or r.description
    return f"- `{r.name}` [Tier {r.tier}]: {q}"


def build_prompt(task_dir: Path) -> str:
    instruction = _read(task_dir / "instruction.md", 8000)
    tests_py = _read(task_dir / "tests" / "test_outputs.py", 10000)
    solve = _read(task_dir / "solution" / "solve.sh", 5000)
    dockerfile = _read(task_dir / "environment" / "Dockerfile", 3000)

    rubrics_md = "\n".join(_rubric_block(r) for r in LLM_JUDGE)
    schema_keys = ", ".join(f'"{r.name}"' for r in LLM_JUDGE)

    return f"""You are auditing a benchmark task used as an RL reward signal for coding agents.

The agent sees ONLY instruction.md. It does NOT see tests/ or solution/. Your job \
is to score this task against the rubrics below. Be STRICT — a failure here means \
an LLM trained with this reward will learn the wrong thing.

## Task: {task_dir.name}

### instruction.md (what the agent sees)
{instruction}

### tests/test_outputs.py (hidden — the reward oracle)
{tests_py}

### solution/solve.sh (hidden — the gold patch)
{solve}

### environment/Dockerfile (hidden)
{dockerfile}

---

## Rubrics to score

For each rubric below, judge PASS / FAIL / NOT_APPLICABLE and give a 1-sentence reason.

{rubrics_md}

---

## Output

Return ONE JSON object, no prose before or after, no markdown fences. Schema:

{{
  {schema_keys}: {{"outcome": "pass" | "fail" | "not_applicable", "reason": "..."}}
}}

Return exactly one key per rubric listed above. For any rubric you judge FAIL, the \
`reason` MUST cite specific evidence (line numbers, function names, literal strings) \
from the task files — not vague language."""


# ─── API call ──────────────────────────────────────────────────────────────

class JudgeError(Exception):
    pass


def _call_anthropic(prompt: str, api_key: str, model: str,
                    max_retries: int = 4, timeout: float = 180.0) -> dict:
    body = json.dumps({
        "model": model,
        "max_tokens": 3000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    last_err = ""
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                JUDGE_API_URL,
                data=body,
                headers={
                    "content-type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            text = data["content"][0]["text"].strip()
            # Strip possible code fences
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(l for l in lines[1:] if not l.startswith("```"))
                text = text.strip()
            return json.loads(text)
        except urllib.error.HTTPError as e:
            last_err = f"http {e.code}"
            if e.code in (429, 500, 502, 503, 529) and attempt < max_retries - 1:
                time.sleep(5 * (2 ** attempt))
                continue
            raise JudgeError(f"{last_err}: {e.read()[:200].decode(errors='ignore')}")
        except json.JSONDecodeError as e:
            last_err = f"json decode: {e}"
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
        except Exception as e:
            last_err = str(e)[:200]
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
    raise JudgeError(f"retries exhausted: {last_err}")


def judge_task(task_dir: Path, api_key: str = "", model: str = "") -> dict:
    """Score a task against all LLM rubrics.

    Returns:
      {
        "model": "claude-opus-4-6",
        "rubric_verdicts": {rubric_name: {"outcome": ..., "reason": ...}, ...},
        "tier_a_fails": [rubric_names],
        "tier_b_fails": [rubric_names],
        "tier_c_fails": [rubric_names],
        "pass_count": int,
        "fail_count": int,
      }
    Raises JudgeError on persistent API failures.
    """
    api_key = api_key or os.environ.get(JUDGE_API_ENV, "")
    if not api_key:
        raise JudgeError(f"no {JUDGE_API_ENV} in env")
    model = model or JUDGE_MODEL

    prompt = build_prompt(task_dir)
    raw = _call_anthropic(prompt, api_key, model)

    verdicts: dict[str, dict] = {}
    for r in LLM_JUDGE:
        v = raw.get(r.name)
        if not isinstance(v, dict):
            verdicts[r.name] = {"outcome": "error", "reason": "missing from response"}
            continue
        outcome = str(v.get("outcome", "error")).lower()
        reason = str(v.get("reason", ""))[:500]
        verdicts[r.name] = {"outcome": outcome, "reason": reason}

    tier_a = [r.name for r in LLM_JUDGE if r.tier == "A" and verdicts[r.name]["outcome"] == "fail"]
    tier_b = [r.name for r in LLM_JUDGE if r.tier == "B" and verdicts[r.name]["outcome"] == "fail"]
    tier_c = [r.name for r in LLM_JUDGE if r.tier == "C" and verdicts[r.name]["outcome"] == "fail"]

    return {
        "model": model,
        "rubric_verdicts": verdicts,
        "tier_a_fails": tier_a,
        "tier_b_fails": tier_b,
        "tier_c_fails": tier_c,
        "pass_count": sum(1 for v in verdicts.values() if v["outcome"] == "pass"),
        "fail_count": sum(1 for v in verdicts.values() if v["outcome"] == "fail"),
    }


# ─── CLI ──────────────────────────────────────────────────────────────────

def _cli():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("task_dir")
    p.add_argument("--model", default="")
    p.add_argument("--api-key", default="")
    args = p.parse_args()
    result = judge_task(Path(args.task_dir), api_key=args.api_key, model=args.model)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
