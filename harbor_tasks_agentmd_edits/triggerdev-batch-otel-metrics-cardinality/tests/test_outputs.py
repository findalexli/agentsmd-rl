"""
Task: triggerdev-batch-otel-metrics-cardinality
Repo: triggerdotdev/trigger.dev @ 6dfbe1d7628aefc894708a752d45aedb249ed5e7
PR:   2846

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/trigger.dev"
BATCH_QUEUE = Path(REPO) / "internal-packages/run-engine/src/batch-queue/index.ts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_metric_calls(source: str) -> list[str]:
    """Extract the attribute objects from metric .add() and .record() calls.

    Returns the string between the attribute object braces for each metric call.
    Matches patterns like:
        Counter?.add(1, { ... })
        Histogram?.record(value, { ... })
    """
    # Match .add(value, { ... }) and .record(value, { ... }) - capture the braces content
    # Use a simple approach: find lines with Counter/Histogram .add/.record and grab
    # the surrounding context up to the closing });
    results = []
    lines = source.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # Look for metric recording calls (counter.add or histogram.record)
        if re.search(r'\.(add|record)\(', line) and re.search(r'(Counter|Histogram)', line, re.IGNORECASE):
            # Collect lines until we see the closing });
            block = line
            j = i + 1
            while j < len(lines) and '});' not in block:
                block += "\n" + lines[j]
                j += 1
            results.append(block)
            i = j
        else:
            i += 1
    return results


def _find_metric_attr_lines(source: str) -> list[str]:
    """Find all lines that appear inside metric attribute objects.

    Uses a broader pattern: any line between a .add(N, { or .record(N, { and });
    """
    # Simpler regex approach: find all attribute keys in metric calls
    attr_lines = []
    in_metric = False
    brace_depth = 0
    for line in source.split("\n"):
        stripped = line.strip()
        # Detect start of metric attribute object
        if re.search(r'\?\.(add|record)\(', line):
            if '{' in line:
                in_metric = True
                brace_depth = line.count('{') - line.count('}')
                attr_lines.append(stripped)
                if brace_depth <= 0:
                    in_metric = False
                continue
        if in_metric:
            brace_depth += line.count('{') - line.count('}')
            attr_lines.append(stripped)
            if brace_depth <= 0:
                in_metric = False
    return attr_lines


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript file must exist and be non-empty."""
    assert BATCH_QUEUE.exists(), f"File not found: {BATCH_QUEUE}"
    content = BATCH_QUEUE.read_text()
    assert len(content) > 1000, "batch-queue/index.ts is suspiciously small"
    # Basic syntax: check balanced braces (rough)
    assert content.count('{') - content.count('}') < 5, "Severely unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_env_id_in_metric_attributes():
    """Metric attributes must not use envId (high cardinality UUID)."""
    source = BATCH_QUEUE.read_text()
    attr_lines = _find_metric_attr_lines(source)
    assert len(attr_lines) > 0, "No metric attribute lines found — file may be stubbed"

    for line in attr_lines:
        assert "envId" not in line, (
            f"Found high-cardinality 'envId' in metric attributes: {line}"
        )


# [pr_diff] fail_to_pass
def test_no_item_count_in_metric_attributes():
    """Metric attributes must not use itemCount (high cardinality unbounded integer)."""
    source = BATCH_QUEUE.read_text()
    attr_lines = _find_metric_attr_lines(source)
    assert len(attr_lines) > 0, "No metric attribute lines found"

    for line in attr_lines:
        assert "itemCount" not in line, (
            f"Found high-cardinality 'itemCount' in metric attributes: {line}"
        )


# [pr_diff] fail_to_pass
def test_metrics_use_environment_type():
    """Metric attributes must use environment type (low cardinality enum)."""
    source = BATCH_QUEUE.read_text()
    attr_lines = _find_metric_attr_lines(source)
    assert len(attr_lines) > 0, "No metric attribute lines found"

    # At least several metric calls should use environment type (snake_case or camelCase)
    env_type_count = sum(
        1 for line in attr_lines
        if "environment_type" in line or "environmentType" in line
    )
    assert env_type_count >= 5, (
        f"Expected at least 5 metric attribute lines with environment type, found {env_type_count}. "
        f"All metric counters and histograms should use environmentType/environment_type instead of envId."
    )


# [pr_diff] fail_to_pass
def test_queue_time_histogram_after_meta_lookup():
    """itemQueueTimeHistogram must be recorded AFTER meta is available (not before).

    The histogram should use environment_type from meta, so it must be called
    after the meta lookup succeeds, not immediately after computing queueTimeMs.
    """
    source = BATCH_QUEUE.read_text()
    lines = source.split("\n")

    # Find the line where queueTimeMs is calculated
    queue_time_line = None
    for i, line in enumerate(lines):
        if "queueTimeMs" in line and "Date.now()" in line:
            queue_time_line = i
            break

    assert queue_time_line is not None, "Could not find queueTimeMs calculation"

    # The histogram record should NOT be on the very next few lines (before meta check)
    # It should appear later, after meta is retrieved
    immediate_block = "\n".join(lines[queue_time_line:queue_time_line + 3])
    assert "itemQueueTimeHistogram" not in immediate_block, (
        "itemQueueTimeHistogram is recorded immediately after queueTimeMs calculation, "
        "before meta is available. It should be moved after the meta lookup."
    )


# ---------------------------------------------------------------------------
# Config file update tests (config_edit)
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    The repo needs a .cursor/rules/ file that documents guidelines for
    metric attribute cardinality to prevent future high-cardinality issues.
    """
    rules_dir = Path(REPO) / ".cursor" / "rules"
    assert rules_dir.exists(), ".cursor/rules/ directory not found"

    # Find any rule file that covers otel/metrics/cardinality
    rule_files = list(rules_dir.glob("*.mdc"))
    found = False
    for f in rule_files:
        content = f.read_text().lower()
        if "cardinality" in content and ("metric" in content or "otel" in content):
            found = True
            break

    assert found, (
        "No .cursor/rules/*.mdc file found covering OpenTelemetry metric cardinality guidelines. "
        "A rule file should be added to document low vs high cardinality attribute usage."
    )


# [config_edit] fail_to_pass

    It should mention specific high-cardinality attribute types to avoid
    (like UUIDs/IDs) and low-cardinality alternatives (like enums/booleans).
    """
    rules_dir = Path(REPO) / ".cursor" / "rules"
    rule_files = list(rules_dir.glob("*.mdc"))

    rule_content = ""
    for f in rule_files:
        content = f.read_text()
        if "cardinality" in content.lower() and ("metric" in content.lower() or "otel" in content.lower()):
            rule_content = content
            break

    assert rule_content, "No OTel metrics rule file found"

    content_lower = rule_content.lower()
    # Must mention high cardinality things to avoid
    assert any(term in content_lower for term in ["uuid", "envid", "userid", "runid"]), (
        "Rule should mention specific high-cardinality attributes to avoid (IDs/UUIDs)"
    )
    # Must mention low cardinality alternatives
    assert any(term in content_lower for term in ["enum", "boolean", "environment_type"]), (
        "Rule should mention low-cardinality alternatives (enums, booleans)"
    )
    # Must explain consequences
    assert any(term in content_lower for term in ["memory", "time series", "cost", "bloat"]), (
        "Rule should explain consequences of high cardinality (memory bloat, costs, etc.)"
    )


# [config_edit] fail_to_pass

    rule_content = ""
    for f in rule_files:
        content = f.read_text()
        if "cardinality" in content.lower() and ("metric" in content.lower() or "otel" in content.lower()):
            rule_content = content
            break

    assert rule_content, "No OTel metrics rule file found"

    # Rule should either have a glob for TS files or be marked alwaysApply
    assert "*.ts" in rule_content or "alwaysApply: true" in rule_content, (
        "OTel metrics rule should apply to TypeScript files (glob pattern *.ts or alwaysApply)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_batch_queue_has_metric_counters():
    """batch-queue/index.ts must still have metric counter/histogram fields."""
    source = BATCH_QUEUE.read_text()
    assert "batchesEnqueuedCounter" in source, "Missing batchesEnqueuedCounter"
    assert "itemsEnqueuedCounter" in source, "Missing itemsEnqueuedCounter"
    assert "itemsProcessedCounter" in source, "Missing itemsProcessedCounter"
    assert "itemsFailedCounter" in source, "Missing itemsFailedCounter"
    assert "itemQueueTimeHistogram" in source, "Missing itemQueueTimeHistogram"
    assert "batchCompletedCounter" in source, "Missing batchCompletedCounter"
    assert "batchProcessingDurationHistogram" in source, "Missing batchProcessingDurationHistogram"
