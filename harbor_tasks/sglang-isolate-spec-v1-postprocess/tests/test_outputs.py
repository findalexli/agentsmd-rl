"""
Task: sglang-isolate-spec-v1-postprocess
Repo: sglang @ 106baedbfb9fb18e96e95963b12473a6d21c0ece
PR:   22146

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: This is a large ML inference framework requiring GPU + model weights to run.
Tests focus on structural and logic verification of the refactoring.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Python files must parse without errors."""
    modified_files = [
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/srt/managers/scheduler.py",
        "python/sglang/srt/managers/scheduler_output_processor_mixin.py",
        "python/sglang/srt/speculative/eagle_info.py",
        "python/sglang/srt/speculative/ngram_info.py",
    ]

    for file_path in modified_files:
        full_path = Path(f"{REPO}/{file_path}")
        src = full_path.read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {file_path}: {e}")


def test_import_check():
    """Modified files must be importable (basic structure check)."""
    # We can't fully import due to CUDA dependencies, but we can check the files exist
    # and have the expected structure via AST
    files = [
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/srt/managers/scheduler_output_processor_mixin.py",
    ]
    for f in files:
        full_path = Path(f"{REPO}/{f}")
        assert full_path.exists(), f"File {f} does not exist"
        src = full_path.read_text()
        tree = ast.parse(src)
        # Check it's not empty
        assert len(tree.body) > 0, f"File {f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core refactoring verification
# ---------------------------------------------------------------------------

def test_handle_finished_req_helper_exists():
    """The new _handle_finished_req helper function must exist."""
    src = Path(f"{REPO}/python/sglang/srt/managers/scheduler_output_processor_mixin.py").read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_handle_finished_req":
            found = True
            # Check it has the right parameters
            args = node.args
            arg_names = [a.arg for a in args.args]
            assert "self" in arg_names, "Missing 'self' parameter"
            assert "req" in arg_names, "Missing 'req' parameter"
            assert "i" in arg_names or any(a.arg == "i" for a in args.args), "Missing 'i' parameter"
            assert "logits_output" in arg_names, "Missing 'logits_output' parameter"
            break

    assert found, "_handle_finished_req helper function not found"


def test_think_end_id_field_added():
    """think_end_id field must be declared in ModelConfig.__init__."""
    src = Path(f"{REPO}/python/sglang/srt/configs/model_config.py").read_text()
    tree = ast.parse(src)

    # Find ModelConfig class and its __init__ method
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    # Search for think_end_id assignment
                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute):
                                    if target.attr == "think_end_id":
                                        return  # Found it

    raise AssertionError("think_end_id field not found in ModelConfig")


def test_scheduler_sets_model_config_think_end_id():
    """Scheduler must set model_config.think_end_id when reasoning_parser is enabled."""
    src = Path(f"{REPO}/python/sglang/srt/managers/scheduler.py").read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if target.attr == "think_end_id":
                        # Check it's setting self.model_config.think_end_id
                        if isinstance(target.value, ast.Attribute):
                            if target.value.attr == "model_config":
                                found = True
                                break

    assert found, "scheduler does not set model_config.think_end_id"


def test_eagle_info_has_reasoning_update():
    """EagleInfo.verify must update reasoning tokens in the verify phase."""
    src = Path(f"{REPO}/python/sglang/srt/speculative/eagle_info.py").read_text()
    tree = ast.parse(src)

    found_think_end_id = False
    found_update_reasoning = False

    # Find the verify method
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "verify":
            # Look for think_end_id assignment and update_reasoning_tokens call
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == "think_end_id":
                            found_think_end_id = True

                if isinstance(stmt, ast.Call):
                    if isinstance(stmt.func, ast.Attribute):
                        if stmt.func.attr == "update_reasoning_tokens":
                            found_update_reasoning = True

    assert found_think_end_id, "think_end_id not extracted from batch.model_config in eagle_info.py"
    assert found_update_reasoning, "update_reasoning_tokens not called in eagle_info.py verify"


def test_ngram_info_has_reasoning_update():
    """NgramInfo._fill_requests must update reasoning tokens in the verify phase."""
    src = Path(f"{REPO}/python/sglang/srt/speculative/ngram_info.py").read_text()
    tree = ast.parse(src)

    found_think_end_id = False
    found_update_reasoning = False

    # Find the _fill_requests method
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_fill_requests":
            # Look for think_end_id assignment and update_reasoning_tokens call
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == "think_end_id":
                            found_think_end_id = True

                if isinstance(stmt, ast.Call):
                    if isinstance(stmt.func, ast.Attribute):
                        if stmt.func.attr == "update_reasoning_tokens":
                            found_update_reasoning = True

    assert found_think_end_id, "think_end_id not extracted from batch.model_config in ngram_info.py"
    assert found_update_reasoning, "update_reasoning_tokens not called in ngram_info.py _fill_requests"


def test_v1_isolation_in_decode_postprocess():
    """process_batch_result_decode must have Spec V1 isolation with early continue."""
    src = Path(f"{REPO}/python/sglang/srt/managers/scheduler_output_processor_mixin.py").read_text()
    tree = ast.parse(src)

    found_is_spec_v1 = False
    found_early_continue = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "process_batch_result_decode":
            src_lines = src.split('\n')
            func_start = node.lineno - 1
            func_end = node.end_lineno if hasattr(node, 'end_lineno') else len(src_lines)
            func_body = '\n'.join(src_lines[func_start:func_end])

            # Check for is_spec_v1 variable
            if "is_spec_v1" in func_body:
                found_is_spec_v1 = True

            # Check for early continue pattern (should have two continue statements,
            # one for overlap case and one for spec v1 case)
            if func_body.count("continue") >= 2:
                found_early_continue = True

    assert found_is_spec_v1, "is_spec_v1 check not found in process_batch_result_decode"
    assert found_early_continue, "early continue pattern not found for Spec V1 isolation"


def test_removed_else_block_reconstructing_tokens():
    """The old else block that reconstructed token list from accept_length_per_req_cpu must be removed."""
    src = Path(f"{REPO}/python/sglang/srt/managers/scheduler_output_processor_mixin.py").read_text()

    # The old code had a pattern like:
    # else:
    #     next_token_ids = []
    #     for i, req in enumerate(batch.reqs):
    #         accept_length = result.accept_length_per_req_cpu[i]
    # This should be removed

    # Check that the old pattern is NOT present
    if "accept_length_per_req_cpu[i]" in src and "cum_num_tokens : cum_num_tokens + accept_length + 1" in src:
        raise AssertionError("Old else block with accept_length_per_req_cpu reconstruction still present")

    # The old pattern should have been replaced with a comment
    assert "Spec V1" in src or "are already handled in the verify phase" in src, \
        "Expected comment about Spec V1 handling not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo's ruff lint check passes on modified files (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/srt/managers/scheduler.py",
        "python/sglang/srt/managers/scheduler_output_processor_mixin.py",
        "python/sglang/srt/speculative/eagle_info.py",
        "python/sglang/srt/speculative/ngram_info.py",
    ]
    r = subprocess.run(
        ["ruff", "check"] + [f"{REPO}/{f}" for f in modified_files] + ["--select=F401,F821"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_black_check():
    """Repo's black format check passes on modified files (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/srt/managers/scheduler.py",
        "python/sglang/srt/managers/scheduler_output_processor_mixin.py",
        "python/sglang/srt/speculative/eagle_info.py",
        "python/sglang/srt/speculative/ngram_info.py",
    ]
    r = subprocess.run(
        ["black", "--check"] + [f"{REPO}/{f}" for f in modified_files],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_isort_check():
    """Repo's isort import order check passes on modified files (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/srt/managers/scheduler.py",
        "python/sglang/srt/managers/scheduler_output_processor_mixin.py",
        "python/sglang/srt/speculative/eagle_info.py",
        "python/sglang/srt/speculative/ngram_info.py",
    ]
    r = subprocess.run(
        ["isort", "--check-only"] + [f"{REPO}/{f}" for f in modified_files],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_codespell_check():
    """Repo's codespell check passes on modified files (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/srt/managers/scheduler.py",
        "python/sglang/srt/managers/scheduler_output_processor_mixin.py",
        "python/sglang/srt/speculative/eagle_info.py",
        "python/sglang/srt/speculative/ngram_info.py",
    ]
    r = subprocess.run(
        ["codespell"] + [f"{REPO}/{f}" for f in modified_files] +
        ["--ignore-words-list=ans,als,hel,boostrap,childs,te,vas,hsa,ment,cann,thi,makro,wil,rouge,PRIS"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"codespell check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

def test_handle_finished_req_not_stub():
    """_handle_finished_req helper must have real logic, not just pass/return."""
    src = Path(f"{REPO}/python/sglang/srt/managers/scheduler_output_processor_mixin.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_handle_finished_req":
            # Count non-trivial statements (not Pass, not docstring)
            non_trivial = []
            for stmt in node.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                    continue  # Skip docstrings
                if not isinstance(stmt, (ast.Pass, ast.Expr)):
                    non_trivial.append(stmt)

            assert len(non_trivial) >= 3, \
                f"_handle_finished_req appears to be a stub (only {len(non_trivial)} non-trivial statements)"


def test_process_batch_result_decode_refactored():
    """process_batch_result_decode must have been refactored (not a stub)."""
    src = Path(f"{REPO}/python/sglang/srt/managers/scheduler_output_processor_mixin.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "process_batch_result_decode":
            # Check function has substantial content
            func_lines = src.split('\n')[node.lineno:node.end_lineno]
            non_empty = [l for l in func_lines if l.strip() and not l.strip().startswith('#')]
            assert len(non_empty) > 20, \
                f"process_batch_result_decode seems too short ({len(non_empty)} non-empty lines)"
