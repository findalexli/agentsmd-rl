#!/usr/bin/env python3
"""Mine CI/CD check-runs from a PR's merge commit and produce structured
output describing every CI test job that gates the merge.

Output schema (JSON):
  {
    "task": "<task name>",
    "repo": "owner/repo",
    "base_commit": "<sha>",
    "merge_commit": "<sha>",
    "fetched_at": "<iso ts>",
    "checks": [
      {
        "name": "<check-run name>",        # e.g. "test (22)"
        "conclusion_at_merge": "success",
        "conclusion_at_base": "success" | "failure" | "missing",
        "kind": "p2p" | "f2p" | "skipped",  # derived from base/merge diff
        "workflow": ".github/workflows/ci.yml",
        "job_id": "test",                   # YAML job name
        "matrix": {"node": "22"},           # if matrixed
        "command": "pnpm -r test",          # extracted from `run:` step
        "step_name": "Run tests",
        "details_url": "https://github.com/.../jobs/...",
        "skipped_reason": null              # if kind=skipped
      },
      ...
    ]
  }

This is the data layer. A separate `revamp_tests.py` script consumes this
JSON and produces the new `tests/test_outputs.py` and `eval_manifest.yaml`
checks list per task.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "pipeline_logs" / "ci_miner_cache"

# Filtering heuristics --------------------------------------------------------

# A check-run is a candidate test job if its name contains one of these tokens.
TEST_NAME_ALLOWLIST = re.compile(
    r"\b(test|tests|pytest|jest|vitest|cargo[- ]?test|go[- ]?test|spec|"
    r"specs|unit|integration|e2e|lint|linter|format|typecheck|tsc|"
    r"build|compile|check|verify|validate)\b",
    re.IGNORECASE,
)

# A check-run is rejected if its name matches any of these (even if it
# matched the allowlist — denylist wins).
NAME_DENYLIST = re.compile(
    r"\b(deploy|deployment|release|publish|push|version|tag|notify|slack|"
    r"discord|comment|backport|milestone|triage|stale|labeler|labelling|"
    r"changeset|changeset-validation|coverage|codecov|preview|docs[- ]?deploy|"
    r"adev[- ]?deploy|kubernetes|k8s|helm|cluster|aws|gcp|azure|"
    r"docker[- ]?push|registry[- ]?push|finalize|summarize|trigger|"
    r"create-tag|setup|upload-artifact|cache)\b",
    re.IGNORECASE,
)


def gh_api(path: str, *, timeout: int = 20) -> Any:
    """Call `gh api`, return parsed JSON or raise."""
    r = subprocess.run(
        ["gh", "api", path],
        capture_output=True, text=True, timeout=timeout,
    )
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {r.stderr.strip()[:300]}")
    return json.loads(r.stdout) if r.stdout.strip() else None


def _fetch_check_runs_graphql(repo: str, sha: str) -> list[dict] | None:
    """GraphQL: fetch check-runs for a commit. Returns REST-shaped dicts.

    Returns None on error (caller falls back to REST)."""
    if "/" not in repo or not sha: return None
    owner, name = repo.split("/", 1)
    q = """
    query($owner:String!, $name:String!, $sha:GitObjectID!) {
      repository(owner:$owner, name:$name) {
        object(oid:$sha) {
          ... on Commit {
            checkSuites(first: 50) {
              nodes {
                app { slug name }
                checkRuns(first: 100) {
                  nodes { name conclusion status detailsUrl databaseId }
                }
              }
            }
          }
        }
      }
    }"""
    try:
        r = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={q}",
             "-f", f"owner={owner}",
             "-f", f"name={name}",
             "-f", f"sha={sha}"],
            capture_output=True, text=True, timeout=20,
        )
        if r.returncode != 0: return None
        data = json.loads(r.stdout)
        obj = (((data or {}).get("data") or {}).get("repository") or {}).get("object")
        if not obj: return []  # commit doesn't exist
        out: list[dict] = []
        suites = (obj.get("checkSuites") or {}).get("nodes") or []
        for s in suites:
            for cr in ((s.get("checkRuns") or {}).get("nodes") or []):
                # Map GraphQL → REST shape
                concl = (cr.get("conclusion") or "").lower() or None
                status = (cr.get("status") or "").lower() or None
                out.append({
                    "name": cr.get("name") or "",
                    "conclusion": concl,
                    "status": status,
                    "details_url": cr.get("detailsUrl") or "",
                    "id": cr.get("databaseId"),  # for run_id extraction
                    "app": s.get("app") or {},
                })
        return out
    except Exception:
        return None


def fetch_check_runs(repo: str, sha: str) -> list[dict]:
    """Return all check-runs for a commit. Tries GraphQL first (saves REST budget),
    falls back to REST."""
    g = _fetch_check_runs_graphql(repo, sha)
    if g is not None:
        return g
    # REST fallback
    out = []
    page = 1
    while True:
        try:
            data = gh_api(f"repos/{repo}/commits/{sha}/check-runs?per_page=100&page={page}")
        except RuntimeError:
            return []
        if not data: break
        out.extend(data.get("check_runs", []))
        if len(data.get("check_runs", [])) < 100: break
        page += 1
        if page > 5: break
    return out


def _commit_exists_graphql(repo: str, sha: str) -> bool:
    """GraphQL probe: does this SHA exist on the remote?"""
    if "/" not in repo or not sha: return False
    owner, name = repo.split("/", 1)
    q = """
    query($owner:String!, $name:String!, $sha:GitObjectID!) {
      repository(owner:$owner, name:$name) {
        object(oid:$sha) { ... on Commit { oid } }
      }
    }"""
    try:
        r = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={q}",
             "-f", f"owner={owner}",
             "-f", f"name={name}",
             "-f", f"sha={sha}"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0: return False
        d = json.loads(r.stdout)
        return bool(((d or {}).get("data") or {}).get("repository", {}).get("object"))
    except Exception:
        return False


def _pr_merge_sha_graphql(repo: str, pr: int) -> str:
    """GraphQL: get PR's merge_commit oid (and head sha as fallback)."""
    merge, _ = _pr_shas_graphql(repo, pr)
    return merge


def _pr_shas_graphql(repo: str, pr: int) -> tuple[str, str]:
    """GraphQL: return (merge_commit_oid, head_oid) for a PR.
    Either may be empty. CI check-runs typically attach to head_oid, not the merge."""
    if "/" not in repo or not pr: return ("", "")
    owner, name = repo.split("/", 1)
    q = """
    query($owner:String!, $name:String!, $n:Int!) {
      repository(owner:$owner, name:$name) {
        pullRequest(number:$n) {
          merged
          mergeCommit { oid }
          headRefOid
        }
      }
    }"""
    try:
        r = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={q}",
             "-f", f"owner={owner}",
             "-f", f"name={name}",
             "-F", f"n={pr}"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0: return ("", "")
        d = json.loads(r.stdout)
        pr_obj = (((d or {}).get("data") or {}).get("repository") or {}).get("pullRequest") or {}
        merge = ""
        if pr_obj.get("merged"):
            mc = pr_obj.get("mergeCommit") or {}
            merge = mc.get("oid") or ""
        head = pr_obj.get("headRefOid", "") or ""
        return (merge, head)
    except Exception:
        return ("", "")


def resolve_merge_commit(repo: str, pr: int, manifest_merge: str) -> str:
    """If manifest's merge_commit returns 404 (squash-merged), fall back to PR API.
    Uses GraphQL to preserve REST budget."""
    if manifest_merge and _commit_exists_graphql(repo, manifest_merge):
        return manifest_merge
    if pr:
        alt = _pr_merge_sha_graphql(repo, pr)
        if alt: return alt
    return manifest_merge  # caller will see empty checks and report the error


def filter_test_runs(runs: list[dict]) -> list[dict]:
    """Filter to genuinely test-flavored check-runs (allowlist + denylist + non-skipped)."""
    kept = []
    for r in runs:
        name = r.get("name", "") or ""
        conclusion = r.get("conclusion", "") or ""
        # Drop skipped, neutral, cancelled
        if conclusion in ("skipped", "neutral", "cancelled", "action_required"):
            continue
        if NAME_DENYLIST.search(name):
            continue
        if not TEST_NAME_ALLOWLIST.search(name):
            continue
        kept.append(r)
    return kept


def fetch_workflow_runs(repo: str, sha: str) -> list[dict]:
    """Return GitHub Actions workflow_runs for a commit."""
    try:
        data = gh_api(f"repos/{repo}/actions/runs?head_sha={sha}&per_page=100")
    except RuntimeError:
        return []
    return data.get("workflow_runs", []) if data else []


def _fetch_file_graphql(repo: str, ref: str, path: str) -> str | None:
    """Read a file from the repo via GraphQL (cheaper than REST contents API).

    GraphQL has a separate 5K/hr budget independent of REST. Workflow YAML
    fetches dominate our API spend, so GraphQL >> REST here.
    """
    if "/" not in repo: return None
    owner, name = repo.split("/", 1)
    expr = f"{ref}:{path}"
    query = """
    query($owner:String!, $name:String!, $expr:String!) {
      repository(owner:$owner, name:$name) {
        object(expression:$expr) { ... on Blob { text } }
      }
    }"""
    try:
        r = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={query}",
             "-f", f"owner={owner}",
             "-f", f"name={name}",
             "-f", f"expr={expr}"],
            capture_output=True, text=True, timeout=20,
        )
        if r.returncode != 0: return None
        data = json.loads(r.stdout)
        obj = (((data or {}).get("data") or {}).get("repository") or {}).get("object") or {}
        return obj.get("text")
    except Exception:
        return None


def fetch_workflow_yaml(repo: str, ref: str, path: str) -> dict | None:
    """Read a workflow file via GraphQL, fall back to REST.

    GraphQL avoids burning REST budget on the hottest call type."""
    raw = _fetch_file_graphql(repo, ref, path)
    if raw is None:
        # REST fallback (only if GraphQL failed)
        try:
            data = gh_api(f"repos/{repo}/contents/{path}?ref={ref}")
        except RuntimeError:
            return None
        if not data or "content" not in data:
            return None
        import base64
        raw = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    try:
        return yaml.safe_load(raw)
    except Exception:
        return None


def parse_matrix_from_name(check_name: str) -> tuple[str, dict[str, str]]:
    """Heuristic: split 'test (22)' or 'test / unit-tests (ubuntu-latest, 22)' into (job_id, matrix dict).

    Returns (job_label, parsed_matrix). Matrix is empty if no parens.
    """
    # Pattern: 'job_label (a, b, c)'
    m = re.match(r"^(.+?)\s*\(([^)]+)\)\s*$", check_name)
    if not m:
        return check_name.strip(), {}
    job_label = m.group(1).strip()
    matrix_parts = [p.strip() for p in m.group(2).split(",")]
    # Heuristic: if 1 item, label as "value"; if more, can't reliably name keys
    matrix = {f"v{i}": v for i, v in enumerate(matrix_parts)}
    return job_label, matrix


_DETAILS_URL_RE = re.compile(r"/actions/runs/(\d+)/job/(\d+)")


def find_workflow_for_run(repo: str, sha: str, check_run: dict, workflows: list[dict]) -> dict | None:
    """Resolve check-run → workflow_run via the run_id embedded in details_url.

    details_url shape: https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}
    """
    durl = check_run.get("details_url", "") or ""
    m = _DETAILS_URL_RE.search(durl)
    if m:
        run_id = m.group(1)
        for wf in workflows:
            if str(wf.get("id", "")) == run_id:
                return wf
        # Also try fetching the run by id directly (workflows list may be incomplete)
        try:
            wr = gh_api(f"repos/{repo}/actions/runs/{run_id}")
            return wr
        except RuntimeError:
            pass
    # Last-resort: name match on workflow.name (unreliable for matrixed jobs)
    cn = check_run.get("name", "")
    job_label, _ = parse_matrix_from_name(cn)
    for wf in workflows:
        if wf.get("name", "").lower() == job_label.lower():
            return wf
    return None


def extract_run_commands_from_job(job_yaml: dict) -> list[dict]:
    """Walk job.steps[*] and emit {step_name, command} for shell-like steps."""
    out = []
    for step in job_yaml.get("steps", []) or []:
        if not isinstance(step, dict):
            continue
        cmd = step.get("run")
        if not cmd:
            continue
        out.append({
            "step_name": step.get("name") or "",
            "command": str(cmd).strip(),
            "shell": step.get("shell") or "bash",
            "if_cond": step.get("if") or "",
            "working_directory": step.get("working-directory") or "",
        })
    return out


# Cache of resolved (workflow_path, ref) → yaml so recursion doesn't re-fetch
_FOLLOW_CACHE: dict[tuple[str, str, str], dict] = {}


def _follow_uses_to_steps(
    repo: str, ref: str, uses_value: str, *, depth: int = 0,
    max_depth: int = 3, with_inputs: dict | None = None,
) -> list[dict]:
    """Resolve a `uses:` reference to its step list.

    Handles three cases:
      ./.github/actions/X        → fetch action.yml; return its `runs.steps`
                                    (if `runs.using == "composite"`)
      ./.github/workflows/X.yml  → fetch the workflow; if it has a single
                                    workflow_call'able job, recurse into it
      org/repo[/path]@ref         → external action; we do NOT follow

    Returns extracted run commands (same shape as extract_run_commands_from_job).
    Recurses up to max_depth.
    """
    if depth > max_depth:
        return []
    s = (uses_value or "").strip()
    if not s or s.startswith(("docker://", "http://", "https://")):
        return []
    # External action (org/repo[@ref]) — we can't fetch action.yml of arbitrary
    # external actions reliably (no `run:`s typically — they're JS/Docker).
    if not (s.startswith("./") or s.startswith("/")):
        return []
    # Local reference — strip any @ref suffix, normalize.
    path_part = s.lstrip("./").split("@", 1)[0]

    # Composite action: ./.github/actions/<name>/action.yml
    if path_part.startswith(".github/actions/") or "/actions/" in path_part:
        # The path may point to the directory; the file is action.yml or action.yaml
        candidates = [path_part + "/action.yml", path_part + "/action.yaml", path_part]
        for cand in candidates:
            key = (repo, ref, cand)
            if key in _FOLLOW_CACHE:
                action_yaml = _FOLLOW_CACHE[key]
            else:
                action_yaml = fetch_workflow_yaml(repo, ref, cand)
                _FOLLOW_CACHE[key] = action_yaml
            if not action_yaml: continue
            runs = action_yaml.get("runs") or {}
            if not isinstance(runs, dict): continue
            if runs.get("using") == "composite":
                steps = runs.get("steps") or []
                # Composite actions can also have nested uses: — recurse
                out = []
                for step in steps:
                    if not isinstance(step, dict): continue
                    if step.get("run"):
                        out.append({
                            "step_name": step.get("name") or "",
                            "command": str(step["run"]).strip(),
                            "shell": step.get("shell") or "bash",
                            "if_cond": step.get("if") or "",
                            "working_directory": step.get("working-directory") or "",
                        })
                    elif step.get("uses"):
                        out.extend(_follow_uses_to_steps(
                            repo, ref, step["uses"], depth=depth+1, max_depth=max_depth
                        ))
                return out
        return []

    # Reusable workflow: ./.github/workflows/<name>.yml
    if path_part.startswith(".github/workflows/") and (path_part.endswith(".yml") or path_part.endswith(".yaml")):
        key = (repo, ref, path_part)
        if key in _FOLLOW_CACHE:
            wf_yaml = _FOLLOW_CACHE[key]
        else:
            wf_yaml = fetch_workflow_yaml(repo, ref, path_part)
            _FOLLOW_CACHE[key] = wf_yaml
        if not wf_yaml: return []
        # Find any job within — pick the one whose name matches "test*",
        # "build*", "lint*", etc., or the first if no obvious match.
        jobs = wf_yaml.get("jobs") or {}
        # Reusable workflows have `on: workflow_call` — find a job with steps.
        out: list[dict] = []
        for job_id, jdef in jobs.items():
            if not isinstance(jdef, dict): continue
            steps = jdef.get("steps") or []
            for step in steps:
                if not isinstance(step, dict): continue
                if step.get("run"):
                    out.append({
                        "step_name": step.get("name") or "",
                        "command": str(step["run"]).strip(),
                        "shell": step.get("shell") or "bash",
                        "if_cond": step.get("if") or "",
                        "working_directory": step.get("working-directory") or "",
                    })
                elif step.get("uses"):
                    out.extend(_follow_uses_to_steps(
                        repo, ref, step["uses"], depth=depth+1, max_depth=max_depth
                    ))
            # Also handle case where job itself is `uses: ...` (chained reusable)
            if not steps and jdef.get("uses"):
                out.extend(_follow_uses_to_steps(
                    repo, ref, jdef["uses"], depth=depth+1, max_depth=max_depth
                ))
        return out

    return []


def extract_run_commands_recursive(
    job_yaml: dict, *, repo: str = "", ref: str = "", max_depth: int = 3
) -> list[dict]:
    """Walk job.steps[*]. For each step that has a `uses:` (composite/reusable),
    recurse to fetch its actual `run:` commands. Returns flat list."""
    out = []
    # First — if the job itself is `uses: ...` (chained workflow_call), follow.
    if not job_yaml.get("steps") and job_yaml.get("uses") and repo and ref:
        return _follow_uses_to_steps(repo, ref, job_yaml["uses"], max_depth=max_depth)
    for step in job_yaml.get("steps", []) or []:
        if not isinstance(step, dict):
            continue
        if step.get("run"):
            out.append({
                "step_name": step.get("name") or "",
                "command": str(step["run"]).strip(),
                "shell": step.get("shell") or "bash",
                "if_cond": step.get("if") or "",
                "working_directory": step.get("working-directory") or "",
            })
        elif step.get("uses") and repo and ref:
            out.extend(_follow_uses_to_steps(
                repo, ref, step["uses"], max_depth=max_depth
            ))
    return out


def find_step_for_check(workflow_yaml: dict, check_name: str,
                         *, repo: str = "", ref: str = "") -> dict | None:
    """Best-effort: find the job in the YAML matching the check-run name.

    If the matched job has no inline `steps:` but uses a reusable workflow
    or composite action (`uses:`), follow it to extract actual `run:`s.
    """
    if not workflow_yaml or "jobs" not in workflow_yaml:
        return None
    job_label, matrix = parse_matrix_from_name(check_name)
    jobs = workflow_yaml.get("jobs") or {}

    def _emit(job_id: str, jdef: dict) -> dict:
        cmds = extract_run_commands_recursive(jdef, repo=repo, ref=ref)
        return {"job_id": job_id, "matrix": matrix, "steps": cmds}

    # Try job key match (exact)
    for job_id, jdef in jobs.items():
        if not isinstance(jdef, dict):
            continue
        nm = jdef.get("name") or job_id
        if job_id.lower() == job_label.lower() or nm.lower() == job_label.lower():
            return _emit(job_id, jdef)
        # Substring match
        if job_label.lower() in nm.lower() or nm.lower() in job_label.lower():
            return _emit(job_id, jdef)
    # Last resort: airflow-style "Foo / Bar / Baz" — split and try left segment
    lparts = [p.strip() for p in re.split(r"\s*/\s*", job_label)]
    if lparts and len(lparts) > 1:
        for job_id, jdef in jobs.items():
            if not isinstance(jdef, dict): continue
            nm = jdef.get("name") or job_id
            if lparts[0].lower() == nm.lower() or lparts[0].lower() == job_id.lower():
                return _emit(job_id, jdef)
    return None


def mine_task(repo: str, base_commit: str, merge_commit: str, *,
              task: str = "", pr: int = 0,
              max_checks: int = 25, max_yamls: int = 15,
              use_cache: bool = True, cache_dir: Path | None = None) -> dict:
    """Top-level: produce the JSON spec for one task.

    Caps:
      max_checks  -- after dedup-by-name, keep at most N check-runs to mine
      max_yamls   -- limit distinct workflow YAML fetches (rate-limit guard)

    Caching:
      Per-task JSON written to pipeline_logs/ci_miner_cache/<task>.json,
      keyed by (repo, base_commit, merge_commit). Re-runs hit the cache and
      skip ALL GitHub API calls. Pass use_cache=False to force re-mine.
    """
    cache_root = cache_dir or CACHE_DIR
    cache_key = (
        f"{(task or repo).replace('/', '__')}__"
        f"{(base_commit or '')[:10]}__{(merge_commit or '')[:10]}.json"
    )
    cache_path = cache_root / cache_key
    if use_cache and cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text())
            cached["_from_cache"] = True
            return cached
        except Exception:
            pass  # fall through to re-mine
    out = {
        "task": task,
        "repo": repo,
        "base_commit": base_commit,
        "merge_commit": merge_commit,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "checks": [],
        "errors": [],
    }
    if "/" not in (repo or ""):
        out["errors"].append(f"bad repo format: {repo!r}")
        return out

    # Resolve squash-merge SHA mismatch via PR API
    if pr:
        resolved = resolve_merge_commit(repo, pr, merge_commit)
        if resolved != merge_commit:
            out["merge_commit_resolved"] = resolved
            merge_commit = resolved

    merge_runs = fetch_check_runs(repo, merge_commit)
    # GitHub attaches check-runs to the PR HEAD commit, not the merge commit.
    # When the manifest's merge_commit returns 0 check-runs, fall back to head SHA.
    if not merge_runs and pr:
        _, head_sha = _pr_shas_graphql(repo, pr)
        if head_sha and head_sha != merge_commit:
            head_runs = fetch_check_runs(repo, head_sha)
            if head_runs:
                out["check_runs_source"] = f"pr_head ({head_sha[:8]})"
                merge_runs = head_runs
    if not merge_runs:
        out["errors"].append(f"no check-runs for merge_commit {merge_commit[:8]}")
    base_runs = fetch_check_runs(repo, base_commit)
    base_status = {r["name"]: r.get("conclusion") for r in base_runs}

    test_runs = filter_test_runs(merge_runs)

    # Dedup BY NAME first — keeps one canonical run per check-run name
    by_name: dict[str, dict] = {}
    for cr in test_runs:
        nm = cr.get("name", "")
        # Prefer a 'success' over any prior entry
        prev = by_name.get(nm)
        if prev is None or (cr.get("conclusion") == "success" and prev.get("conclusion") != "success"):
            by_name[nm] = cr
    candidates = list(by_name.values())[:max_checks]
    if len(by_name) > max_checks:
        out["errors"].append(f"capped check-runs at {max_checks}/{len(by_name)} (matrix-heavy)")

    workflows = fetch_workflow_runs(repo, merge_commit)
    yaml_cache: dict[str, dict] = {}
    yaml_fetches = 0

    for cr in candidates:
        name = cr.get("name", "")
        wf_run = find_workflow_for_run(repo, merge_commit, cr, workflows) or (
            workflows[0] if workflows else None
        )
        wf_path = wf_run.get("path") if wf_run else None
        wf_yaml = None
        if wf_path:
            if wf_path in yaml_cache:
                wf_yaml = yaml_cache[wf_path]
            elif yaml_fetches < max_yamls:
                wf_yaml = fetch_workflow_yaml(repo, merge_commit, wf_path)
                yaml_cache[wf_path] = wf_yaml
                yaml_fetches += 1
        step_match = find_step_for_check(wf_yaml, name,
                                          repo=repo, ref=merge_commit) if wf_yaml else None

        base_concl = base_status.get(name, "missing")
        merge_concl = cr.get("conclusion", "")
        if merge_concl != "success":
            kind = "skipped"
        elif base_concl == "failure":
            kind = "f2p"
        else:
            kind = "p2p"

        out["checks"].append({
            "name": name,
            "conclusion_at_merge": merge_concl,
            "conclusion_at_base": base_concl,
            "kind": kind,
            "workflow": wf_path,
            "job_id": step_match["job_id"] if step_match else None,
            "matrix": step_match["matrix"] if step_match else {},
            "steps": step_match["steps"] if step_match else [],
            "details_url": cr.get("details_url"),
        })

    # Persist to cache (best-effort)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(out, indent=2))
    except Exception:
        pass
    return out


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", help="Task name (reads harbor_tasks/<task>/eval_manifest.yaml)")
    ap.add_argument("--repo", help="owner/repo (overrides manifest)")
    ap.add_argument("--base", help="base_commit SHA (overrides)")
    ap.add_argument("--merge", help="merge_commit SHA (overrides)")
    ap.add_argument("--out", help="Path to write JSON output (default: stdout)")
    ap.add_argument("--input-jsonl", help="Mine many tasks from a JSONL file with {task,repo,base,merge}")
    ap.add_argument("--out-jsonl", help="Aggregate output JSONL (one mining record per task)")
    args = ap.parse_args()

    if args.input_jsonl:
        rows = [json.loads(l) for l in Path(args.input_jsonl).read_text().splitlines() if l.strip()]
        out_lines = []
        for r in rows:
            print(f"  mining {r['task']} ({r['repo']}#{r.get('pr')}) ...", file=sys.stderr)
            try:
                spec = mine_task(r["repo"], r["base"], r["merge"],
                                 task=r["task"], pr=int(r.get("pr") or 0))
            except Exception as e:
                spec = {"task": r["task"], "errors": [str(e)[:300]], "checks": []}
            out_lines.append(json.dumps(spec))
        out_path = Path(args.out_jsonl or "/dev/stdout")
        out_path.write_text("\n".join(out_lines) + "\n")
        return 0

    # Single-task mode
    if args.task and not (args.repo and args.base and args.merge):
        manifest = ROOT / "harbor_tasks" / args.task / "eval_manifest.yaml"
        if not manifest.exists():
            return print(f"manifest not found: {manifest}", file=sys.stderr) or 2
        d = yaml.safe_load(manifest.read_text())
        s = d.get("source", {}) or {}
        args.repo = args.repo or s.get("repo")
        args.base = args.base or s.get("base_commit")
        args.merge = args.merge or s.get("merge_commit")
    if not (args.repo and args.base and args.merge):
        return print("missing repo/base/merge (provide --task or --repo/--base/--merge)", file=sys.stderr) or 2

    spec = mine_task(args.repo, args.base, args.merge, task=args.task or "")
    body = json.dumps(spec, indent=2)
    if args.out:
        Path(args.out).write_text(body)
    else:
        print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
