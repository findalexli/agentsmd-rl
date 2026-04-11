"""
Task: supabase-header-upgrade-button
Repo: supabase/supabase @ cccae29569c129e52178837d6d4662baa11f5986
PR:   44494

Add an always-visible "Upgrade to Pro" button in the dashboard header for
free-plan users, gated behind a PostHog experiment (headerUpgradeCta).
The button reuses UpgradePlanButton (which needs a new onClick prop) and
tracks a click telemetry event.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/supabase"

HEADER_BUTTON_PATH = (
    "apps/studio/components/layouts/Navigation/LayoutHeader/HeaderUpgradeButton.tsx"
)
LAYOUT_HEADER_PATH = (
    "apps/studio/components/layouts/Navigation/LayoutHeader/LayoutHeader.tsx"
)
MOBILE_NAV_PATH = (
    "apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx"
)
UPGRADE_BUTTON_PATH = "apps/studio/components/ui/UpgradePlanButton.tsx"
TELEMETRY_PATH = "packages/common/telemetry-constants.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_header_upgrade_button_component():
    """HeaderUpgradeButton component exists with experiment gating and free-plan check."""
    # Use node subprocess to validate component structure
    script = f"""
    const fs = require('fs');
    const path = '{REPO}/{HEADER_BUTTON_PATH}';
    if (!fs.existsSync(path)) {{
        console.error('HeaderUpgradeButton.tsx does not exist');
        process.exit(1);
    }}
    const content = fs.readFileSync(path, 'utf8');

    if (!content.includes('export const HeaderUpgradeButton') &&
        !content.includes('export function HeaderUpgradeButton') &&
        !content.includes('export default')) {{
        console.error('HeaderUpgradeButton must be exported');
        process.exit(2);
    }}

    if (!content.includes('headerUpgradeCta')) {{
        console.error('Must reference headerUpgradeCta experiment ID');
        process.exit(3);
    }}

    // Must gate on free plan
    if (!content.includes("'free'") && !content.includes('"free"')) {{
        console.error('Must check for free plan');
        process.exit(4);
    }}

    // Must use UpgradePlanButton
    if (!content.includes('UpgradePlanButton')) {{
        console.error('Must render UpgradePlanButton');
        process.exit(5);
    }}

    console.log('OK');
    """
    r = subprocess.run(["node", "-e", script], capture_output=True, timeout=15)
    assert r.returncode == 0, f"Component validation failed: {r.stderr.decode()}"


def test_header_upgrade_tracks_click_event():
    """HeaderUpgradeButton tracks header_upgrade_cta_clicked on click via useTrack."""
    path = Path(REPO) / HEADER_BUTTON_PATH
    assert path.exists(), "HeaderUpgradeButton.tsx must exist"
    content = path.read_text()

    # Must use useTrack hook (not deprecated useSendEventMutation)
    assert "useTrack" in content, "Must import and use useTrack hook for telemetry"
    assert "useSendEventMutation" not in content, (
        "Must NOT use deprecated useSendEventMutation"
    )

    # Must track the click event
    assert "header_upgrade_cta_clicked" in content, (
        "Must track 'header_upgrade_cta_clicked' event"
    )

    # Must have a click handler that calls track
    lines = content.split("\n")
    has_handler = False
    for i, line in enumerate(lines):
        if "handle" in line.lower() and "click" in line.lower():
            # Check that track is called nearby (within 5 lines)
            nearby = "\n".join(lines[i : i + 5])
            if "track(" in nearby and "header_upgrade_cta_clicked" in nearby:
                has_handler = True
                break
    assert has_handler, (
        "Must have a click handler that calls track('header_upgrade_cta_clicked')"
    )


def test_upgrade_plan_button_accepts_onclick():
    """UpgradePlanButton must accept an onClick callback prop and forward it to Button."""
    # Use node subprocess to validate the prop addition
    script = f"""
    const fs = require('fs');
    const content = fs.readFileSync('{REPO}/{UPGRADE_BUTTON_PATH}', 'utf8');

    // Check onClick is in the props interface
    const interfaceMatch = content.match(/interface\\s+UpgradePlanButtonProps[\\s\\S]*?\\}}/);
    if (!interfaceMatch || !interfaceMatch[0].includes('onClick')) {{
        console.error('onClick must be in UpgradePlanButtonProps interface');
        process.exit(1);
    }}

    // Check onClick is destructured in the component params
    const funcMatch = content.match(/UpgradePlanButton\\s*=\\s*\\([\\s\\S]*?\\)\\s*=>/);
    if (!funcMatch || !funcMatch[0].includes('onClick')) {{
        console.error('onClick must be destructured in component params');
        process.exit(2);
    }}

    // Check onClick is passed to the rendered Button element
    const lines = content.split('\\n');
    let found = false;
    for (const line of lines) {{
        if (line.includes('<Button') && line.includes('onClick')) {{
            found = true;
            break;
        }}
        if (line.includes('onClick={{onClick}}') || line.includes('onClick=\\{{onClick\\}}')) {{
            found = true;
            break;
        }}
    }}
    // Also check multi-line Button with onClick on next line
    for (let i = 0; i < lines.length; i++) {{
        if (lines[i].includes('<Button') && i + 1 < lines.length) {{
            // Check next few lines for onClick
            for (let j = i; j < Math.min(i + 5, lines.length); j++) {{
                if (lines[j].includes('onClick')) {{
                    found = true;
                    break;
                }}
            }}
        }}
    }}
    if (!found) {{
        console.error('onClick must be forwarded to the rendered Button');
        process.exit(3);
    }}

    console.log('OK');
    """
    r = subprocess.run(["node", "-e", script], capture_output=True, timeout=15)
    assert r.returncode == 0, f"onClick prop validation failed: {r.stderr.decode()}"


def test_telemetry_event_interface_defined():
    """HeaderUpgradeCtaClickedEvent interface defined with correct action in telemetry-constants.ts."""
    path = Path(REPO) / TELEMETRY_PATH
    content = path.read_text()

    assert "HeaderUpgradeCtaClickedEvent" in content, (
        "Must define HeaderUpgradeCtaClickedEvent interface"
    )

    # Check the action field has correct value
    match = re.search(
        r"interface\s+HeaderUpgradeCtaClickedEvent\s*\{[^}]*"
        r"action:\s*['\"]([^'\"]+)['\"]",
        content,
        re.DOTALL,
    )
    assert match, "HeaderUpgradeCtaClickedEvent must have an action field"
    assert match.group(1) == "header_upgrade_cta_clicked", (
        f"Action must be 'header_upgrade_cta_clicked', got '{match.group(1)}'"
    )

    # Must have JSDoc with @group Events
    idx = content.index("HeaderUpgradeCtaClickedEvent")
    preceding = content[max(0, idx - 300) : idx]
    assert "@group Events" in preceding or "@group events" in preceding.lower(), (
        "HeaderUpgradeCtaClickedEvent must have @group Events JSDoc"
    )


def test_layout_header_renders_upgrade_button():
    """LayoutHeader must import and render HeaderUpgradeButton."""
    path = Path(REPO) / LAYOUT_HEADER_PATH
    content = path.read_text()

    assert "HeaderUpgradeButton" in content, (
        "LayoutHeader must reference HeaderUpgradeButton"
    )

    # Must appear in both import and JSX
    has_import = bool(re.search(r"import\s.*HeaderUpgradeButton", content))
    has_jsx = "<HeaderUpgradeButton" in content
    assert has_import, "Must import HeaderUpgradeButton"
    assert has_jsx, "Must render <HeaderUpgradeButton /> in JSX"


def test_mobile_nav_renders_upgrade_button():
    """MobileNavigationBar must import and render HeaderUpgradeButton."""
    path = Path(REPO) / MOBILE_NAV_PATH
    content = path.read_text()

    assert "HeaderUpgradeButton" in content, (
        "MobileNavigationBar must reference HeaderUpgradeButton"
    )

    has_import = bool(re.search(r"import\s.*HeaderUpgradeButton", content))
    has_jsx = "<HeaderUpgradeButton" in content
    assert has_import, "Must import HeaderUpgradeButton"
    assert has_jsx, "Must render <HeaderUpgradeButton /> in JSX"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — rules from telemetry-standards SKILL.md
# ---------------------------------------------------------------------------


def test_telemetry_event_naming_convention():
    """Telemetry event name follows [object]_[verb] snake_case with approved verb.

    Source: .claude/skills/telemetry-standards/SKILL.md lines 15-19
    """
    path = Path(REPO) / HEADER_BUTTON_PATH
    assert path.exists(), "HeaderUpgradeButton.tsx must exist"
    content = path.read_text()

    # Extract event names from track() calls
    matches = re.findall(r"track\(\s*['\"]([^'\"]+)['\"]\s*[,)]", content)
    assert matches, "Must have at least one track() call with event name"

    approved_verbs = {
        "opened", "clicked", "submitted", "created", "removed", "updated",
        "intended", "evaluated", "added", "enabled", "disabled", "copied",
        "exposed", "failed", "converted", "closed", "completed", "applied",
        "sent", "moved",
    }

    for event_name in matches:
        # Must be snake_case
        assert event_name == event_name.lower(), (
            f"Event '{event_name}' must be snake_case"
        )
        assert re.match(r"^[a-z][a-z0-9_]*$", event_name), (
            f"Event '{event_name}' must be snake_case alphanumeric"
        )
        # Must follow [object]_[verb] pattern — verb is the last word
        parts = event_name.rsplit("_", 1)
        assert len(parts) == 2, (
            f"Event '{event_name}' must follow [object]_[verb] format"
        )
        last_word = parts[-1]
        assert last_word in approved_verbs, (
            f"Event '{event_name}' uses unapproved verb '{last_word}'. "
            f"Approved verbs: {sorted(approved_verbs)}"
        )


def test_telemetry_event_in_union_type():
    """HeaderUpgradeCtaClickedEvent must be added to the TelemetryEvent union type.

    Source: .claude/skills/telemetry-standards/SKILL.md line 158
    """
    path = Path(REPO) / TELEMETRY_PATH
    content = path.read_text()

    # Find the TelemetryEvent type definition
    union_start = content.rfind("export type TelemetryEvent")
    assert union_start != -1, (
        "TelemetryEvent type must exist in telemetry-constants.ts"
    )

    union_section = content[union_start:]
    assert "HeaderUpgradeCtaClickedEvent" in union_section, (
        "HeaderUpgradeCtaClickedEvent must be added to the TelemetryEvent union type"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file integrity
# ---------------------------------------------------------------------------


def test_node_parses_modified_files():
    """All modified TypeScript files must be readable and non-empty."""
    files = [
        UPGRADE_BUTTON_PATH,
        LAYOUT_HEADER_PATH,
        MOBILE_NAV_PATH,
        TELEMETRY_PATH,
    ]
    for f in files:
        full_path = Path(REPO) / f
        assert full_path.exists(), f"{f} must exist"
        r = subprocess.run(
            [
                "node", "-e",
                f"const c = require('fs').readFileSync('{full_path}', 'utf8');"
                f"if (c.length < 100) {{ process.exit(1); }}"
                f"console.log('{f}: ' + c.length + ' chars');",
            ],
            capture_output=True,
            timeout=10,
        )
        assert r.returncode == 0, (
            f"File {f} failed validation: {r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------


def test_repo_lint():
    """Repo's ESLint passes on studio app (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_navigation_bar_utils():
    """Repo's unit tests for NavigationBar utils pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "NavigationBar.utils"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"NavigationBar utils tests failed:\n{r.stderr[-500:]}"


def test_repo_navigation_bar_branch_selector():
    """Repo's unit tests for NavigationBar ProjectBranchSelector pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "ProjectBranchSelector.utils"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"ProjectBranchSelector tests failed:\n{r.stderr[-500:]}"


def test_repo_telemetry_first_touch_store():
    """Repo's telemetry-first-touch-store tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "telemetry-first-touch-store"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/packages/common",
    )
    assert r.returncode == 0, f"Telemetry first touch store tests failed:\n{r.stderr[-500:]}"


def test_repo_posthog_tests():
    """Repo's posthog tracking tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "posthog"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Posthog tests failed:\n{r.stderr[-500:]}"


def test_repo_local_version_popover():
    """Repo's LocalVersionPopover tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "LocalVersionPopover"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"LocalVersionPopover tests failed:\n{r.stderr[-500:]}"


def test_repo_layout_header_local_version():
    """Repo's LayoutHeader LocalVersionPopover tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "LayoutHeader/LocalVersionPopover"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"LayoutHeader LocalVersionPopover tests failed:\n{r.stderr[-500:]}"


def test_repo_common_package_consent_state():
    """Repo's common package consent-state tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "consent-state"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/packages/common",
    )
    assert r.returncode == 0, f"Common package consent-state tests failed:\n{r.stderr[-500:]}"


def test_repo_common_package_first_referrer():
    """Repo's common package first-referrer-cookie tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "first-referrer-cookie"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/packages/common",
    )
    assert r.returncode == 0, f"Common package first-referrer-cookie tests failed:\n{r.stderr[-500:]}"


def test_repo_instrumentation_client():
    """Repo's instrumentation-client tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "instrumentation-client"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Instrumentation client tests failed:\n{r.stderr[-500:]}"
