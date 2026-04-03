"""
Task: backstage-featmcpactions-add-server-operation-and
Repo: backstage/backstage @ 1ee5b28e41c274ea38c16a07290387763b5e2284
PR:   32978

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/backstage"
PLUGIN = Path(REPO) / "plugins" / "mcp-actions-backend"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_syntax():
    """All modified TypeScript files must parse without syntax errors."""
    files = [
        PLUGIN / "src" / "services" / "McpService.ts",
        PLUGIN / "src" / "plugin.ts",
        PLUGIN / "src" / "routers" / "createStreamableRouter.ts",
    ]
    for f in files:
        assert f.exists(), f"{f.name} must exist"
        content = f.read_text()
        # Basic syntax check: file is non-empty and has no obvious truncation
        assert len(content) > 50, f"{f.name} appears truncated or empty"
        # Ensure balanced braces (rough syntax check for TS)
        assert content.count("{") == content.count("}"), (
            f"{f.name} has unbalanced braces"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_metrics_module_exports_bucket_boundaries():
    """New metrics.ts must export bucketBoundaries array with OTel-standard values."""
    metrics_file = PLUGIN / "src" / "metrics.ts"
    assert metrics_file.exists(), "metrics.ts must be created"
    content = metrics_file.read_text()

    # Must export bucket boundaries
    assert "bucketBoundaries" in content, "Must export bucketBoundaries"
    assert "export" in content.split("bucketBoundaries")[0].split("\n")[-1], (
        "bucketBoundaries must be exported"
    )
    # Must contain standard OTel boundary values
    for val in ["0.01", "0.05", "0.1", "1", "10", "60", "300"]:
        assert val in content, f"bucketBoundaries should include {val}"


def test_metrics_module_defines_operation_attributes():
    """metrics.ts must define McpServerOperationAttributes interface."""
    content = (PLUGIN / "src" / "metrics.ts").read_text()
    assert "McpServerOperationAttributes" in content
    # Must include required MCP method name attribute
    assert "'mcp.method.name'" in content or '"mcp.method.name"' in content, (
        "Operation attributes must include mcp.method.name"
    )
    # Must include optional error type
    assert "'error.type'" in content or '"error.type"' in content
    # Must include tool name attribute
    assert "'gen_ai.tool.name'" in content or '"gen_ai.tool.name"' in content


def test_metrics_module_defines_session_attributes():
    """metrics.ts must define McpServerSessionAttributes interface."""
    content = (PLUGIN / "src" / "metrics.ts").read_text()
    assert "McpServerSessionAttributes" in content
    # Must include protocol version attribute
    assert "'mcp.protocol.version'" in content or '"mcp.protocol.version"' in content
    # Must include network transport attribute
    assert "'network.transport'" in content or '"network.transport"' in content


def test_mcpservice_creates_operation_duration_histogram():
    """McpService must create an mcp.server.operation.duration histogram."""
    content = (PLUGIN / "src" / "services" / "McpService.ts").read_text()
    assert "mcp.server.operation.duration" in content, (
        "McpService must create mcp.server.operation.duration histogram"
    )
    assert "createHistogram" in content, (
        "Must use createHistogram from metrics service"
    )
    # Must import from metrics module
    assert "bucketBoundaries" in content, (
        "Must use shared bucketBoundaries from metrics module"
    )


def test_mcpservice_records_metrics_for_tools_list():
    """tools/list handler must record operation duration with mcp.method.name."""
    content = (PLUGIN / "src" / "services" / "McpService.ts").read_text()

    # Find the ListToolsRequestSchema handler section
    assert "ListToolsRequestSchema" in content

    # The handler must use performance.now() for timing
    assert "performance.now()" in content, "Must use performance.now() for timing"

    # Must record with tools/list method name
    assert "'tools/list'" in content or '"tools/list"' in content, (
        "Must record metrics with 'tools/list' method name"
    )

    # Must have finally block to always record
    assert "finally" in content, "Must use finally block to ensure metrics are recorded"


def test_mcpservice_records_metrics_for_tools_call():
    """tools/call handler must record operation duration with tool name and error type."""
    content = (PLUGIN / "src" / "services" / "McpService.ts").read_text()

    # Must record with tools/call method name
    assert "'tools/call'" in content or '"tools/call"' in content, (
        "Must record metrics with 'tools/call' method name"
    )

    # Must include gen_ai.tool.name in call metrics
    assert "'gen_ai.tool.name'" in content or '"gen_ai.tool.name"' in content, (
        "Must record gen_ai.tool.name for tool call metrics"
    )

    # Must include gen_ai.operation.name = execute_tool
    assert "'execute_tool'" in content or '"execute_tool"' in content, (
        "Must record gen_ai.operation.name as 'execute_tool'"
    )

    # Must handle tool_error for isError results
    assert "'tool_error'" in content or '"tool_error"' in content, (
        "Must record 'tool_error' for CallToolResult with isError=true"
    )


def test_streamable_router_creates_session_duration_histogram():
    """createStreamableRouter must create mcp.server.session.duration histogram."""
    content = (PLUGIN / "src" / "routers" / "createStreamableRouter.ts").read_text()

    assert "mcp.server.session.duration" in content, (
        "Router must create mcp.server.session.duration histogram"
    )
    assert "createHistogram" in content, "Must use createHistogram"
    assert "bucketBoundaries" in content, "Must use shared bucket boundaries"

    # Must record on close and on error
    assert "performance.now()" in content, "Must time with performance.now()"
    assert "'error.type'" in content or '"error.type"' in content, (
        "Must record error.type on session failure"
    )


def test_plugin_injects_metrics_service():
    """plugin.ts must import and inject metricsServiceRef into deps."""
    content = (PLUGIN / "src" / "plugin.ts").read_text()
    assert "metricsServiceRef" in content, (
        "Plugin must import metricsServiceRef"
    )
    assert "metrics:" in content or "metrics :" in content, (
        "Plugin must declare metrics in deps"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README documentation update
# ---------------------------------------------------------------------------


    # Must have a Metrics heading
    assert "## Metrics" in content, "README must have a ## Metrics section"

    # Must document both metric names
    assert "mcp.server.operation.duration" in content, (
        "README must document mcp.server.operation.duration metric"
    )
    assert "mcp.server.session.duration" in content, (
        "README must document mcp.server.session.duration metric"
    )



    # Find the metrics section
    lower = content.lower()
    metrics_idx = lower.find("## metrics")
    assert metrics_idx != -1, "README must have ## Metrics section"

    # Get content after the Metrics heading until next heading
    after_metrics = content[metrics_idx:]
    next_heading = after_metrics.find("\n## ", 1)
    if next_heading != -1:
        metrics_section = after_metrics[:next_heading]
    else:
        metrics_section = after_metrics

    # Must mention duration/operation concepts
    metrics_lower = metrics_section.lower()
    assert "duration" in metrics_lower, (
        "Metrics section should describe duration measurement"
    )
    assert "operation" in metrics_lower or "request" in metrics_lower, (
        "Metrics section should describe what operations are measured"
    )
    assert "session" in metrics_lower, (
        "Metrics section should describe session measurement"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — existing functionality preserved
# ---------------------------------------------------------------------------

def test_mcpservice_still_has_core_api():
    """McpService must still export create() and getServer() methods."""
    content = (PLUGIN / "src" / "services" / "McpService.ts").read_text()
    assert "static async create(" in content, "McpService.create() must exist"
    assert "getServer(" in content, "McpService.getServer() must exist"
    assert "class McpService" in content, "McpService class must exist"


