"""
Task: mimir-mimirmixin-add-grafana-dashboard-urls
Repo: grafana/mimir @ 1ab789daf1b3d9393386b302622d2906bc08b2dc
PR:   14458

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/mimir"
ALERTS_UTILS = Path(REPO) / "operations/mimir-mixin/alerts/alerts-utils.libsonnet"
CONFIG = Path(REPO) / "operations/mimir-mixin/config.libsonnet"
ALERTS = Path(REPO) / "operations/mimir-mixin/alerts/alerts.libsonnet"
ALERTMANAGER = Path(REPO) / "operations/mimir-mixin/alerts/alertmanager.libsonnet"
COMPACTOR = Path(REPO) / "operations/mimir-mixin/alerts/compactor.libsonnet"
BLOCKS = Path(REPO) / "operations/mimir-mixin/alerts/blocks.libsonnet"
INGEST = Path(REPO) / "operations/mimir-mixin/alerts/ingest-storage.libsonnet"
CONTRIBUTING = Path(REPO) / "docs/internal/contributing/README.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_external_dashboard_url_helper():
    """alerts-utils.libsonnet defines externalDashboardURL that generates
    absolute dashboard URLs using std.md5 for UID and maps cluster_labels
    to URL var params."""
    content = ALERTS_UTILS.read_text()

    # Function must be defined
    assert "externalDashboardURL" in content, \
        "alerts-utils.libsonnet must define externalDashboardURL function"

    # Must compute dashboard UID via std.md5
    assert "std.md5" in content, \
        "externalDashboardURL must use std.md5 to compute dashboard UID"

    # Must reference the config prefix
    assert "externalGrafanaURLPrefix" in content, \
        "externalDashboardURL must reference externalGrafanaURLPrefix config"

    # Must generate var params from cluster_labels
    assert "cluster_labels" in content, \
        "externalDashboardURL must map cluster_labels to dashboard var params"

    # Must return null when prefix is empty (opt-out behavior)
    assert "null" in content, \
        "externalDashboardURL must return null when prefix is empty"


# [pr_diff] fail_to_pass
def test_dashboard_url_annotation_helper():
    """alerts-utils.libsonnet defines dashboardURLAnnotation that returns
    an object with dashboard_url field for use in alert annotations."""
    content = ALERTS_UTILS.read_text()

    assert "dashboardURLAnnotation" in content, \
        "alerts-utils.libsonnet must define dashboardURLAnnotation function"

    # Must produce a dashboard_url key
    assert "dashboard_url" in content, \
        "dashboardURLAnnotation must produce a dashboard_url annotation field"


# [pr_diff] fail_to_pass
def test_with_dashboard_url_helper():
    """alerts-utils.libsonnet defines withDashboardURL that applies a
    default dashboard URL to all alerts in groups that lack one."""
    content = ALERTS_UTILS.read_text()

    assert "withDashboardURL" in content, \
        "alerts-utils.libsonnet must define withDashboardURL function"

    # Must iterate over groups and rules
    assert "for rule in" in content or "for group in" in content, \
        "withDashboardURL must iterate over groups/rules to apply URLs"

    # Must check if dashboard_url already exists (skip if present)
    assert "dashboard_url" in content, \
        "withDashboardURL must handle existing dashboard_url annotations"


# [pr_diff] fail_to_pass
def test_config_external_grafana_url_prefix():
    """config.libsonnet declares externalGrafanaURLPrefix config field
    defaulting to empty string (opt-out by default)."""
    content = CONFIG.read_text()

    assert "externalGrafanaURLPrefix" in content, \
        "config.libsonnet must declare externalGrafanaURLPrefix field"

    # Default should be empty string (disabled by default)
    # Match patterns like: externalGrafanaURLPrefix: ''
    assert re.search(r"externalGrafanaURLPrefix\s*:\s*''\s*,?", content), \
        "externalGrafanaURLPrefix must default to empty string ''"


# [pr_diff] fail_to_pass
def test_alerts_apply_dashboard_urls():
    """Multiple alert files must use dashboardURLAnnotation or
    withDashboardURL to add dashboard links to alerts."""
    files_using_dashboard = 0

    for alert_file in [ALERTS, ALERTMANAGER, COMPACTOR, BLOCKS, INGEST]:
        content = alert_file.read_text()
        if "dashboardURLAnnotation" in content or "withDashboardURL" in content:
            files_using_dashboard += 1

    assert files_using_dashboard >= 3, \
        f"At least 3 alert files must use dashboard URL helpers, found {files_using_dashboard}"


# [pr_diff] fail_to_pass
def test_alertmanager_uses_with_dashboard_url():
    """alertmanager.libsonnet must use withDashboardURL to apply a default
    dashboard URL to all alerts in the file."""
    content = ALERTMANAGER.read_text()

    assert "withDashboardURL" in content, \
        "alertmanager.libsonnet must use withDashboardURL for bulk URL application"

    # Should reference the alertmanager dashboard
    assert "mimir-alertmanager" in content, \
        "alertmanager.libsonnet should link alerts to the alertmanager dashboard"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/doc update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a Jsonnet section
    assert re.search(r"(?i)jsonnet", content), \
        "Contributing README must document jsonnet formatting"

    # Must reference the mixin formatting command
    assert "format-mixin" in content, \
        "Contributing docs must mention make format-mixin for jsonnet files"

    # Must reference building the mixin to verify compiled output
    assert "build-mixin" in content, \
        "Contributing docs must mention make build-mixin to verify compiled output"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_alerts_utils_valid_structure():
    """alerts-utils.libsonnet must be a valid non-empty jsonnet file
    with balanced braces."""
    content = ALERTS_UTILS.read_text()
    assert len(content) > 100, "alerts-utils.libsonnet should not be empty"

    # Basic structural check: braces should be roughly balanced
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, \
        f"Unbalanced braces in alerts-utils.libsonnet: {open_braces} open vs {close_braces} close"
