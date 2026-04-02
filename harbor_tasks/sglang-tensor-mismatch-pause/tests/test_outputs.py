"""
Task: sglang-tensor-mismatch-pause
Repo: sgl-project/sglang @ 279e7738c5857ce8664a77b1ffcb59d46960f1e4
PR:   21514

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"
SCHEDULER = Path(f"{REPO}/python/sglang/srt/managers/scheduler.py")


# ---------------------------------------------------------------------------
# Mock objects replicating ScheduleBatch's tensor-size invariant (plain lists)
# ---------------------------------------------------------------------------

class _MockReq:
    def __init__(self, finished=False):
        self._finished = finished


class _MockBatch:
    """Lightweight stand-in for ScheduleBatch; tracks the len(reqs)==len(seq_lens) invariant."""

    def __init__(self, n, all_finished=False):
        self.reqs = [_MockReq(finished=all_finished) for _ in range(n)]
        self.seq_lens = list(range(n))
        self.seq_lens_cpu = list(range(n))
        self.orig_seq_lens = list(range(n))
        self.req_pool_indices = [0] * n
        self.output_ids = [0] * n
        self.seq_lens_sum = n

    def is_empty(self):
        return len(self.reqs) == 0

    def filter_batch(self, chunked_req_to_exclude=None):
        """Replicates the base-commit early-return bug: clears reqs but not tensors."""
        keep = [i for i, r in enumerate(self.reqs) if not r._finished]
        if not keep:
            self.reqs = []  # tensors NOT cleared — this is the bug trigger
            return
        if len(keep) == len(self.reqs):
            return
        self.reqs = [self.reqs[i] for i in keep]
        self.seq_lens = [self.seq_lens[i] for i in keep]
        self.seq_lens_cpu = [self.seq_lens_cpu[i] for i in keep]
        self.orig_seq_lens = [self.orig_seq_lens[i] for i in keep]
        self.req_pool_indices = [self.req_pool_indices[i] for i in keep]
        self.output_ids = [self.output_ids[i] for i in keep]
        self.seq_lens_sum = len(keep)

    def merge_batch(self, other):
        self.reqs.extend(other.reqs)
        self.seq_lens.extend(other.seq_lens)
        self.seq_lens_cpu.extend(other.seq_lens_cpu)
        self.orig_seq_lens.extend(other.orig_seq_lens)
        self.req_pool_indices.extend(other.req_pool_indices)
        if self.output_ids is not None and other.output_ids is not None:
            self.output_ids.extend(other.output_ids)
        self.seq_lens_sum += other.seq_lens_sum


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_invariant(batch):
    """The critical invariant: len(reqs) must equal len(seq_lens)."""
    assert len(batch.reqs) == len(batch.seq_lens), (
        f"Invariant violated: {len(batch.reqs)} reqs vs {len(batch.seq_lens)} seq_lens"
    )


def _extract_merge_section():
    """Extract the code between filter_batch(...) and self.last_batch = None in pause_generation."""
    src = SCHEDULER.read_text()
    tree = ast.parse(src)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "pause_generation":
            func_node = node
            break
    assert func_node is not None, "pause_generation not found in scheduler.py"

    lines = src.splitlines()
    func_lines = lines[func_node.lineno - 1 : func_node.end_lineno]

    section = []
    in_filter = False
    past_filter = False
    paren_depth = 0

    for line in func_lines:
        stripped = line.strip()

        if not past_filter:
            if "filter_batch" in stripped and "last_batch" in stripped:
                in_filter = True
            if in_filter:
                paren_depth += stripped.count("(") - stripped.count(")")
                if paren_depth <= 0:
                    past_filter = True
                continue
        else:
            if "self.last_batch" in stripped and "None" in stripped:
                break
            if stripped:
                section.append(line)

    assert section, "Could not extract merge section from pause_generation"
    return textwrap.dedent("\n".join(section))


def _run_merge(running, last):
    """Execute the actual merge section from pause_generation with mock batches."""
    code = _extract_merge_section()

    class _Self:
        pass

    s = _Self()
    s.running_batch = running
    s.last_batch = last
    exec(code, {"self": s})
    return s.running_batch


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """scheduler.py must parse without syntax errors."""
    ast.parse(SCHEDULER.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug reproduction
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_empty_batch_not_merged():
    """All-finished single-req last_batch must not corrupt running_batch tensors."""
    running = _MockBatch(100)
    last = _MockBatch(1, all_finished=True)
    last.filter_batch()  # empties reqs, stale tensors remain

    assert last.is_empty(), "Precondition: last_batch should be empty after filter"
    assert len(last.seq_lens) == 1, "Precondition: stale tensors still present"

    result = _run_merge(running, last)
    _check_invariant(result)
    assert len(result.reqs) == 100, f"Expected 100 reqs, got {len(result.reqs)}"


# [pr_diff] fail_to_pass
def test_larger_empty_batch_not_merged():
    """Same invariant violation with a 5-request batch where all finish."""
    running = _MockBatch(651)
    last = _MockBatch(5, all_finished=True)
    last.filter_batch()

    assert last.is_empty()
    assert len(last.seq_lens) == 5, "Stale tensors from 5 finished reqs"

    result = _run_merge(running, last)
    _check_invariant(result)
    assert len(result.reqs) == 651, f"Expected 651 reqs, got {len(result.reqs)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_nonempty_batch_still_merged():
    """When last_batch has live requests after filter, merge must still happen."""
    running = _MockBatch(100)
    last = _MockBatch(4, all_finished=False)
    last.reqs[0]._finished = True  # 1 finished, 3 alive
    last.filter_batch()

    assert not last.is_empty(), "last_batch should still have live reqs"
    assert len(last.reqs) == 3

    result = _run_merge(running, last)
    _check_invariant(result)
    assert len(result.reqs) == 103, f"Expected 103 reqs, got {len(result.reqs)}"


# [pr_diff] pass_to_pass
def test_all_alive_batch_merged():
    """When no requests are finished, all should be merged unchanged."""
    running = _MockBatch(200)
    last = _MockBatch(10, all_finished=False)
    last.filter_batch()  # no-op, all alive

    assert not last.is_empty()
    assert len(last.reqs) == 10

    result = _run_merge(running, last)
    _check_invariant(result)
    assert len(result.reqs) == 210, f"Expected 210 reqs, got {len(result.reqs)}"


# [pr_diff] pass_to_pass
def test_empty_running_batch_assignment():
    """When running_batch is empty but last_batch has live reqs, running_batch should become last_batch."""
    running = _MockBatch(0)
    last = _MockBatch(7, all_finished=False)
    last.filter_batch()  # no-op, all alive

    assert running.is_empty()
    assert not last.is_empty()

    result = _run_merge(running, last)
    _check_invariant(result)
    assert len(result.reqs) == 7, f"Expected 7 reqs, got {len(result.reqs)}"


# [static] pass_to_pass
def test_not_stub():
    """pause_generation must have a meaningful body, not a stub."""
    src = SCHEDULER.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "pause_generation":
            stmts = [
                s for s in node.body
                if not isinstance(s, ast.Pass)
                and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
            ]
            assert len(stmts) >= 3, f"Only {len(stmts)} meaningful statements"
            return
    raise AssertionError("pause_generation not found")
