"""
Task: tuist-featserver-add-shared-http-failure
Repo: tuist/tuist @ 10f2ade970563161cd32699f45d87c8b891417e0
PR:   9935

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/tuist"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_elixir_syntax_transport():
    """transport.ex must be valid Elixir (balanced do/end, defmodule present)."""
    path = Path(REPO) / "tuist_common" / "lib" / "tuist_common" / "http" / "transport.ex"
    src = path.read_text()
    assert "defmodule TuistCommon.HTTP.Transport do" in src, \
        "transport.ex must define TuistCommon.HTTP.Transport module"
    # Basic balance check: every 'do' has matching 'end'
    do_count = len(re.findall(r'\bdo\b', src))
    end_count = len(re.findall(r'\bend\b', src))
    assert do_count == end_count, \
        f"Unbalanced do/end in transport.ex: {do_count} do vs {end_count} end"


# [static] pass_to_pass
def test_elixir_syntax_prom_ex_plugin():
    """transport_prom_ex_plugin.ex must be valid Elixir."""
    path = Path(REPO) / "tuist_common" / "lib" / "tuist_common" / "http" / "transport_prom_ex_plugin.ex"
    src = path.read_text()
    assert "defmodule TuistCommon.HTTP.TransportPromExPlugin do" in src, \
        "Must define TuistCommon.HTTP.TransportPromExPlugin module"
    do_count = len(re.findall(r'\bdo\b', src))
    end_count = len(re.findall(r'\bend\b', src))
    assert do_count == end_count, \
        f"Unbalanced do/end in transport_prom_ex_plugin.ex: {do_count} do vs {end_count} end"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_transport_classifies_body_read_timeout():
    """Transport module must classify Bandit body read timeouts."""
    path = Path(REPO) / "tuist_common" / "lib" / "tuist_common" / "http" / "transport.ex"
    src = path.read_text()
    assert "bandit_request_timeout?" in src, \
        "Transport must define bandit_request_timeout? function"
    assert '"Body read timeout"' in src, \
        "Must check for 'Body read timeout' error string"
    # Must also classify failure reasons
    assert "bandit_request_failure_reason" in src, \
        "Transport must define bandit_request_failure_reason function"
    assert '"server_error"' in src, \
        "Must classify server errors (status >= 500)"
    assert '"protocol_error"' in src, \
        "Must classify protocol errors"


# [pr_diff] fail_to_pass
def test_transport_classifies_thousand_island_drops():
    """Transport module must classify Thousand Island connection drop reasons."""
    path = Path(REPO) / "tuist_common" / "lib" / "tuist_common" / "http" / "transport.ex"
    src = path.read_text()
    assert "thousand_island_connection_drop_reason" in src, \
        "Transport must define thousand_island_connection_drop_reason"
    # Must handle multiple drop reasons
    for reason in [":timeout", ":closed", ":shutdown"]:
        assert reason in src, f"Must handle {reason} drop reason"


# [pr_diff] fail_to_pass
def test_prom_ex_plugin_defines_event_metrics():
    """TransportPromExPlugin must implement PromEx event_metrics callback with counters."""
    path = Path(REPO) / "tuist_common" / "lib" / "tuist_common" / "http" / "transport_prom_ex_plugin.ex"
    src = path.read_text()
    assert "use PromEx.Plugin" in src, \
        "Must use PromEx.Plugin"
    assert "def event_metrics" in src, \
        "Must implement event_metrics/1 callback"
    # Must define counters for all four metric groups
    assert "tuist_http_request_timeout" in src or "request_timeout_metrics" in src, \
        "Must define request timeout metrics"
    assert "tuist_http_request_failure" in src or "request_failure_metrics" in src, \
        "Must define request failure metrics"
    assert "tuist_http_connection_drop" in src or "connection_drop_metrics" in src, \
        "Must define connection drop metrics"
    assert "tuist_http_connection_error" in src or "connection_error_metrics" in src, \
        "Must define connection error metrics"


# [pr_diff] fail_to_pass
def test_transport_logger_attaches_to_telemetry():
    """TransportLogger must attach to Bandit and Thousand Island telemetry events."""
    path = Path(REPO) / "tuist_common" / "lib" / "tuist_common" / "http" / "transport_logger.ex"
    src = path.read_text()
    assert "defmodule TuistCommon.HTTP.TransportLogger do" in src, \
        "Must define TuistCommon.HTTP.TransportLogger module"
    assert "def attach" in src, \
        "Must define attach function"
    # Must subscribe to both Bandit and Thousand Island events
    assert "[:bandit, :request, :stop]" in src, \
        "Must subscribe to bandit request stop events"
    assert "[:thousand_island, :connection, :stop]" in src, \
        "Must subscribe to thousand_island connection stop events"
    assert ":recv_error" in src and ":send_error" in src, \
        "Must handle recv_error and send_error events"


# [pr_diff] fail_to_pass
def test_server_wires_transport_logger():
    """server/lib/tuist/application.ex must attach TransportLogger on startup."""
    path = Path(REPO) / "server" / "lib" / "tuist" / "application.ex"
    src = path.read_text()
    assert "TransportLogger" in src, \
        "Server application.ex must reference TransportLogger"
    assert re.search(r"TransportLogger\.attach", src), \
        "Server must call TransportLogger.attach"


# [pr_diff] fail_to_pass
def test_server_wires_prom_ex_plugin():
    """server/lib/tuist/prom_ex.ex must include TransportPromExPlugin."""
    path = Path(REPO) / "server" / "lib" / "tuist" / "prom_ex.ex"
    src = path.read_text()
    assert "TransportPromExPlugin" in src, \
        "Server prom_ex.ex must include TransportPromExPlugin"


# [pr_diff] fail_to_pass
def test_cache_wires_transport_logger():
    """cache/lib/cache/application.ex must attach TransportLogger on startup."""
    path = Path(REPO) / "cache" / "lib" / "cache" / "application.ex"
    src = path.read_text()
    assert "TransportLogger" in src, \
        "Cache application.ex must reference TransportLogger"
    assert re.search(r"TransportLogger\.attach", src), \
        "Cache must call TransportLogger.attach"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit — AGENTS.md update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from root AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass


# [agent_config] pass_to_pass
