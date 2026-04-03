"""
Task: workers-sdk-chromedevtoolspatches-migrate-deployment-from-cl
Repo: cloudflare/workers-sdk @ 3b81fc6a75857d5c158824f17d9316adc55878fc
PR:   12928

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/workers-sdk"

CONTROLLER_PATH = (
    "packages/miniflare/src/plugins/core/inspector-proxy/"
    "inspector-proxy-controller.ts"
)
WORKER_PATH = (
    "packages/wrangler/templates/startDevWorker/InspectorProxyWorker.ts"
)
README_PATH = "packages/chrome-devtools-patches/README.md"
WRANGLER_JSONC_PATH = "packages/chrome-devtools-patches/wrangler.jsonc"
MAKEFILE_PATH = "packages/chrome-devtools-patches/Makefile"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(relpath: str) -> str:
    return (Path(REPO) / relpath).read_text()


def _extract_allowed_origins(source: str) -> str:
    """Extract the ALLOWED_ORIGIN_HOSTNAMES array text from a TS file."""
    match = re.search(
        r"ALLOWED_ORIGIN_HOSTNAMES\s*=\s*\[(.*?)\];",
        source,
        re.DOTALL,
    )
    assert match, "Could not find ALLOWED_ORIGIN_HOSTNAMES array"
    return match.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    for fpath in [CONTROLLER_PATH, WORKER_PATH]:
        full = Path(REPO) / fpath
        assert full.exists(), f"{fpath} does not exist"
        content = full.read_text()
        # Basic sanity: file is non-empty and has the expected array
        assert "ALLOWED_ORIGIN_HOSTNAMES" in content, (
            f"{fpath} missing ALLOWED_ORIGIN_HOSTNAMES"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — inspector proxy allowlist tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_controller_allows_workers_dev():
    """Inspector proxy controller must allow cloudflare-devtools.devprod.workers.dev."""
    origins = _extract_allowed_origins(_read(CONTROLLER_PATH))
    assert "cloudflare-devtools.devprod.workers.dev" in origins, (
        "inspector-proxy-controller.ts must include "
        "'cloudflare-devtools.devprod.workers.dev' in ALLOWED_ORIGIN_HOSTNAMES"
    )


# [pr_diff] fail_to_pass
def test_worker_allows_workers_dev():
    """InspectorProxyWorker must allow cloudflare-devtools.devprod.workers.dev."""
    origins = _extract_allowed_origins(_read(WORKER_PATH))
    assert "cloudflare-devtools.devprod.workers.dev" in origins, (
        "InspectorProxyWorker.ts must include "
        "'cloudflare-devtools.devprod.workers.dev' in ALLOWED_ORIGIN_HOSTNAMES"
    )


# [pr_diff] fail_to_pass
def test_controller_versioned_preview_pattern():
    """Inspector proxy controller must have a regex for versioned workers.dev previews."""
    origins = _extract_allowed_origins(_read(CONTROLLER_PATH))
    # The regex should match patterns like abc123-cloudflare-devtools.devprod.workers.dev
    assert re.search(
        r"cloudflare-devtools\\\.devprod\\\.workers\\\.dev",
        origins,
    ), (
        "inspector-proxy-controller.ts must include a regex pattern "
        "for versioned workers.dev preview URLs"
    )


# [pr_diff] fail_to_pass
def test_worker_versioned_preview_pattern():
    """InspectorProxyWorker must have a regex for versioned workers.dev previews."""
    origins = _extract_allowed_origins(_read(WORKER_PATH))
    assert re.search(
        r"cloudflare-devtools\\\.devprod\\\.workers\\\.dev",
        origins,
    ), (
        "InspectorProxyWorker.ts must include a regex pattern "
        "for versioned workers.dev preview URLs"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — backward compatibility
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_pages_dev_backward_compat():
    """Both inspector proxy files must still allow legacy pages.dev origins."""
    for fpath in [CONTROLLER_PATH, WORKER_PATH]:
        origins = _extract_allowed_origins(_read(fpath))
        assert "cloudflare-devtools.pages.dev" in origins, (
            f"{fpath} must retain 'cloudflare-devtools.pages.dev' for backward compat"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — wrangler.jsonc
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_wrangler_config_exists():
    """wrangler.jsonc must exist with Workers + Assets config."""
    fpath = Path(REPO) / WRANGLER_JSONC_PATH
    assert fpath.exists(), "packages/chrome-devtools-patches/wrangler.jsonc must exist"
    content = fpath.read_text()
    # Strip JSONC comments for parsing
    stripped = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    # Remove trailing commas (JSONC allows them, JSON doesn't)
    stripped = re.sub(r",\s*([\]}])", r"\1", stripped)
    data = json.loads(stripped)
    assert "assets" in data, "wrangler.jsonc must configure 'assets'"
    assert data.get("name") == "cloudflare-devtools", (
        "wrangler.jsonc must set name to 'cloudflare-devtools'"
    )


# [pr_diff] fail_to_pass
def test_makefile_uses_wrangler_deploy():
    """Makefile publish target must use 'wrangler deploy' not 'wrangler pages deploy'."""
    content = _read(MAKEFILE_PATH)
    # Find the publish target body (lines after "publish:" until next target or EOF)
    publish_match = re.search(
        r"^publish:.*?\n((?:\t.*\n)*)",
        content,
        re.MULTILINE,
    )
    assert publish_match, "Makefile must have a 'publish' target"
    publish_body = publish_match.group(1)
    assert "wrangler deploy" in publish_body, (
        "publish target must use 'wrangler deploy'"
    )
    assert "wrangler pages deploy" not in publish_body, (
        "publish target must NOT use 'wrangler pages deploy'"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Agent config (agent_config) — changeset required
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:changesets
