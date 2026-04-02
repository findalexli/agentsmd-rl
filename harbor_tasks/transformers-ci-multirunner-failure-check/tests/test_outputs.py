"""
Task: transformers-ci-multirunner-failure-check
Repo: huggingface/transformers @ 882ffdbbd6b8ad50feaa860d702e70950cfc95d0
PR:   #45032 (Use multi runners to check new failing tests in a CI run)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import yaml

REPO = "/workspace/transformers"
SCRIPT = f"{REPO}/utils/check_bad_commit.py"
WORKFLOW = f"{REPO}/.github/workflows/check_failed_tests.yml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_fixtures():
    """Create mock failures JSON and patched script (mocking git bisect)."""
    # 12 tests across 3 models
    failures = {
        "model_a": {"single-gpu": [{"line": f"tests/test_a_{i}.py::test_{i}"} for i in range(5)]},
        "model_b": {"single-gpu": [{"line": f"tests/test_b_{i}.py::test_{i}"} for i in range(4)]},
        "model_c": {"single-gpu": [{"line": f"tests/test_c_{i}.py::test_{i}"} for i in range(3)]},
    }
    failures_path = "/tmp/test_failures.json"
    with open(failures_path, "w") as f:
        json.dump(failures, f)

    # Patch script: mock find_bad_commit and get_commit_info to avoid real git bisect
    source = Path(SCRIPT).read_text()
    mock = '''
# === TEST MOCKS (inserted by test harness) ===
def find_bad_commit(target_test, start_commit, end_commit):
    return {"bad_commit": "abc123def456", "status": "found"}

def get_commit_info(commit, pr_number=None):
    return {"commit": commit, "author": "test_author", "pr_number": "42"}
# === END MOCKS ===
'''
    idx = source.find("if __name__")
    assert idx != -1, "Cannot find if __name__ block in check_bad_commit.py"
    patched = source[:idx] + mock + source[idx:]
    patched_path = "/tmp/check_bad_commit_patched.py"
    with open(patched_path, "w") as f:
        f.write(patched)

    return failures_path, patched_path


def _run_script(patched_path, failures_path, run_idx=None, n_runners=None):
    """Run the patched script with optional partitioning env vars."""
    env = os.environ.copy()
    env.pop("run_idx", None)
    env.pop("n_runners", None)
    if run_idx is not None:
        env["run_idx"] = str(run_idx)
    if n_runners is not None:
        env["n_runners"] = str(n_runners)

    outfile = tempfile.mktemp(suffix=".json")
    result = subprocess.run(
        ["python3", patched_path,
         "--start_commit", "aaa", "--end_commit", "bbb",
         "--file", failures_path,
         "--output_file", outfile],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, (
        f"Script failed (run_idx={run_idx}, n_runners={n_runners}):\n"
        f"stdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
    )
    with open(outfile) as f:
        return json.load(f)


def _count_tests(output):
    """Count total single-gpu tests in script output."""
    total = 0
    for model_data in output.values():
        total += len(model_data.get("single-gpu", []))
    return total


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_python_syntax():
    """check_bad_commit.py must parse without syntax errors."""
    import py_compile
    py_compile.compile(SCRIPT, doraise=True)


# [static] pass_to_pass
def test_yaml_syntax():
    """check_failed_tests.yml must be valid YAML."""
    with open(WORKFLOW) as f:
        wf = yaml.safe_load(f)
    assert isinstance(wf, dict), "Workflow YAML did not parse to a dict"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_partition_across_runners():
    """Script partitions 12 tests across 3 runners via run_idx/n_runners env vars.

    Each runner must get a non-empty subset; together they cover all 12 tests
    with no duplicates. Accepts both 0-indexed and 1-indexed schemes.
    """
    failures_path, patched_path = _create_fixtures()
    n_runners = 3

    for start_idx in (0, 1):
        all_tests = []
        runner_counts = []
        ok = True

        for idx in range(start_idx, start_idx + n_runners):
            try:
                out = _run_script(patched_path, failures_path, run_idx=idx, n_runners=n_runners)
            except AssertionError:
                ok = False
                break

            tests = []
            for model_data in out.values():
                for t in model_data.get("single-gpu", []):
                    tests.append(t.get("test", t.get("line", "")))

            runner_counts.append(len(tests))
            all_tests.extend(tests)

        if not ok:
            continue
        # Each runner must get a subset, not all 12
        if max(runner_counts) >= 12:
            continue
        # Together must cover exactly 12 unique tests
        if len(set(all_tests)) != 12 or len(all_tests) != 12:
            continue
        # Each runner must get at least 1 test
        if min(runner_counts) == 0:
            continue

        return  # success with this indexing scheme

    assert False, "Partitioning failed with both 0-indexed and 1-indexed schemes"


# [pr_diff] fail_to_pass
def test_partition_with_different_runner_counts():
    """Partitioning works with 2 runners and 4 runners, not just 3."""
    failures_path, patched_path = _create_fixtures()

    for n_runners in (2, 4):
        for start_idx in (0, 1):
            all_tests = []
            ok = True
            for idx in range(start_idx, start_idx + n_runners):
                try:
                    out = _run_script(patched_path, failures_path, run_idx=idx, n_runners=n_runners)
                except (AssertionError, Exception):
                    ok = False
                    break
                for model_data in out.values():
                    for t in model_data.get("single-gpu", []):
                        all_tests.append(t.get("test", t.get("line", "")))
            if ok and len(set(all_tests)) == 12 and len(all_tests) == 12:
                break  # this indexing scheme works
        else:
            assert False, f"Partitioning failed for n_runners={n_runners}"


# [pr_diff] fail_to_pass
def test_output_keyed_by_model():
    """Output from each runner is a dict keyed by model name, not a flat list.

    With n_runners=1, all 12 tests should appear under their respective models.
    """
    failures_path, patched_path = _create_fixtures()

    # Try both 0-indexed and 1-indexed for single runner
    out = None
    for idx in (0, 1):
        try:
            out = _run_script(patched_path, failures_path, run_idx=idx, n_runners=1)
            break
        except AssertionError:
            continue
    assert out is not None, "Script failed with n_runners=1"

    assert isinstance(out, dict), f"Output is {type(out).__name__}, expected dict keyed by model"
    expected_models = {"model_a", "model_b", "model_c"}
    assert expected_models.issubset(set(out.keys())), (
        f"Expected models {expected_models}, got keys {set(out.keys())}"
    )

    for model in expected_models:
        sg = out[model].get("single-gpu", [])
        assert len(sg) > 0, f"Model '{model}' has no single-gpu tests"
        for entry in sg:
            assert "test" in entry or "line" in entry, f"Entry in {model} missing test/line key"

    assert _count_tests(out) == 12, f"Expected 12 tests with n_runners=1, got {_count_tests(out)}"


# [pr_diff] fail_to_pass
def test_merge_step_combines_runners():
    """Merge step in workflow correctly merges multi-runner JSON outputs.

    Extracts the merge step's run block from YAML and executes it against
    mock data from 3 runners.
    """
    with open(WORKFLOW) as f:
        wf = yaml.safe_load(f)

    jobs = wf.get("jobs", {})

    # Find the process/merge job
    merge_job = None
    for name, defn in jobs.items():
        if "process_new_failures" in name:
            merge_job = defn
            break
    assert merge_job is not None, "No process_new_failures job found"

    # Find merge step by name
    merge_step = None
    for step in merge_job.get("steps", []):
        if "merge" in step.get("name", "").lower():
            merge_step = step
            break
    assert merge_step is not None, "No merge step found in process_new_failures job"

    run_cmd = merge_step.get("run", "")

    # Reject the buggy baseline (simple cp of _1.json)
    lines = [l.strip() for l in run_cmd.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
    assert not (len(lines) == 1 and lines[0].startswith("cp ") and "_1.json" in lines[0]), (
        "Merge step is still a simple cp of _1.json"
    )

    # Execute the merge step with mock data
    job_name = "test_job"
    merge_dir = f"/transformers/new_failures_with_bad_commit_{job_name}"
    os.makedirs(merge_dir, exist_ok=True)

    runner_outputs = [
        {"model_a": {"single-gpu": [{"test": "tests/test_a_0.py::test_0", "bad_commit": "abc"}]}},
        {"model_a": {"single-gpu": [{"test": "tests/test_a_1.py::test_1", "bad_commit": "def"}]},
         "model_b": {"single-gpu": [{"test": "tests/test_b_0.py::test_0", "bad_commit": "ghi"}]}},
        {"model_b": {"single-gpu": [{"test": "tests/test_b_1.py::test_1", "bad_commit": "jkl"}]},
         "model_c": {"single-gpu": [{"test": "tests/test_c_0.py::test_0", "bad_commit": "mno"}]}},
    ]

    for i, data in enumerate(runner_outputs):
        path = os.path.join(merge_dir, f"new_failures_with_bad_commit_{job_name}_{i}.json")
        with open(path, "w") as f:
            json.dump(data, f)

    env = os.environ.copy()
    env["job"] = job_name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as tf:
        tf.write("#!/bin/bash\nset -e\n")
        tf.write("cd /transformers\n")
        tf.write(run_cmd)
        tf_path = tf.name
    os.chmod(tf_path, 0o755)

    result = subprocess.run(
        ["bash", tf_path], env=env, capture_output=True, text=True,
        timeout=30, cwd="/transformers",
    )
    assert result.returncode == 0, f"Merge script failed: {result.stderr[:500]}"

    # Find merged output
    merged_path = None
    for candidate in [
        "/transformers/new_failures_with_bad_commit.json",
        f"/transformers/new_failures_with_bad_commit_{job_name}/merged.json",
        f"/transformers/new_failures_with_bad_commit_{job_name}.json",
    ]:
        if os.path.exists(candidate):
            merged_path = candidate
            break

    if merged_path is None:
        for fname in os.listdir("/transformers"):
            if "new_failures_with_bad_commit" in fname and fname.endswith(".json") and "test_job" not in fname:
                merged_path = os.path.join("/transformers", fname)
                break

    assert merged_path is not None, "Merge step did not produce an output file"

    with open(merged_path) as f:
        merged = json.load(f)

    assert isinstance(merged, dict), f"Merged output is {type(merged).__name__}, expected dict"

    total = sum(len(v.get("single-gpu", [])) for v in merged.values())
    assert total == 5, f"Expected 5 total tests in merged output, got {total}"
    for model in ("model_a", "model_b", "model_c"):
        assert model in merged, f"Merged output missing model '{model}'"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_backward_compatible_without_env_vars():
    """Script processes all 12 tests when run_idx/n_runners are NOT set."""
    failures_path, patched_path = _create_fixtures()
    out = _run_script(patched_path, failures_path, run_idx=None, n_runners=None)
    total = _count_tests(out)
    assert total == 12, f"Without env vars should process all 12 tests, got {total}"


# [pr_diff] pass_to_pass
def test_workflow_structure_preserved():
    """Workflow retains core jobs and required inputs (docker, job)."""
    with open(WORKFLOW) as f:
        wf = yaml.safe_load(f)

    jobs = wf.get("jobs", {})
    assert any("check_new_failures" in n for n in jobs), "Missing check_new_failures job"
    assert any("process_new_failures" in n for n in jobs), "Missing process_new_failures job"

    on = wf.get("on", wf.get(True, {}))
    assert "workflow_call" in on, "Missing workflow_call trigger"
    inputs = on["workflow_call"].get("inputs", {})
    for required in ("docker", "job"):
        assert required in inputs, f"Missing required input '{required}'"


# [pr_diff] fail_to_pass
def test_max_num_runners_input():
    """Workflow has a max_num_runners (or similar) input with number type and default."""
    with open(WORKFLOW) as f:
        wf = yaml.safe_load(f)

    on = wf.get("on", wf.get(True, {}))
    inputs = on.get("workflow_call", {}).get("inputs", {})

    runner_input = None
    for name, defn in inputs.items():
        if "runner" in name.lower() and ("max" in name.lower() or "num" in name.lower()):
            runner_input = defn
            break

    assert runner_input is not None, "No max runners input found in workflow_call inputs"
    assert runner_input.get("type") in ("number", "integer"), (
        f"Max runners input type should be number, got {runner_input.get('type')}"
    )
    assert runner_input.get("default") is not None, "Max runners input should have a default value"


# [pr_diff] fail_to_pass
def test_dynamic_matrix():
    """check_new_failures uses dynamic matrix (not hardcoded [1]) and depends on a setup job."""
    with open(WORKFLOW) as f:
        wf = yaml.safe_load(f)

    jobs = wf.get("jobs", {})

    check_job = None
    for name, defn in jobs.items():
        if "check_new_failures" in name and "process" not in name and "setup" not in name:
            check_job = defn
            break
    assert check_job is not None, "No check_new_failures job found"

    strategy = check_job.get("strategy", {})
    matrix = strategy.get("matrix", {})
    run_idx = matrix.get("run_idx")

    assert run_idx != [1], "run_idx is still hardcoded to [1]"
    assert run_idx is not None, "No run_idx in strategy.matrix"

    needs = check_job.get("needs", [])
    if isinstance(needs, str):
        needs = [needs]
    assert any("setup" in n for n in needs), "check_new_failures does not depend on a setup job"


# [static] pass_to_pass
def test_script_not_bloated():
    """check_bad_commit.py is not bloated with unnecessary code (original ~330 lines)."""
    lines = Path(SCRIPT).read_text().splitlines()
    assert len(lines) < 500, (
        f"check_bad_commit.py is {len(lines)} lines (expected <500, original ~330)"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from agent config files
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:185-186
def test_no_bare_type_ignore():
    """No bare '# type: ignore' without error code in check_bad_commit.py.

    Per SKILL.md: Always add the specific error code, e.g. '# type: ignore[call-arg]',
    not bare '# type: ignore'.
    """
    import re
    source = Path(SCRIPT).read_text()
    # Match '# type: ignore' NOT followed by '[' (bare ignore)
    bare_ignores = re.findall(r"#\s*type:\s*ignore(?!\[)", source)
    assert len(bare_ignores) == 0, (
        f"Found {len(bare_ignores)} bare '# type: ignore' without error code in check_bad_commit.py. "
        "Use '# type: ignore[error-code]' instead."
    )
