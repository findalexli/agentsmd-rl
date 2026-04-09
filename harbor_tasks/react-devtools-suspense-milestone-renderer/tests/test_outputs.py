"""
Task: react-devtools-suspense-milestone-renderer
Repo: react @ e0cc7202e14418b453c69c4f06dc00c64151f202
PR:   35927

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agent_targets_single_renderer():
    """overrideSuspenseMilestone must only call the renderer matching rendererID,
    not iterate all renderer interfaces."""
    test_content = textwrap.dedent("""\
        'use strict';

        describe('Agent.overrideSuspenseMilestone', () => {
          let Agent;

          beforeEach(() => {
            Agent = require('../backend/agent').default;
          });

          it('should only call the renderer specified by rendererID', () => {
            const EventEmitter = require('events');
            const bridge = new EventEmitter();
            bridge.send = jest.fn();

            const agent = new Agent(bridge);

            const calls1 = [];
            const calls2 = [];
            agent._rendererInterfaces[1] = {
              supportsTogglingSuspense: true,
              overrideSuspenseMilestone: (s) => calls1.push(s),
            };
            agent._rendererInterfaces[2] = {
              supportsTogglingSuspense: true,
              overrideSuspenseMilestone: (s) => calls2.push(s),
            };

            agent.overrideSuspenseMilestone({
              rendererID: 1,
              suspendedSet: [10, 20],
            });

            // Only renderer 1 should have been called
            expect(calls1).toHaveLength(1);
            expect(calls1[0]).toEqual([10, 20]);
            // Renderer 2 must NOT be called (the old bug called all renderers)
            expect(calls2).toHaveLength(0);
          });

          it('should work with a different rendererID', () => {
            const EventEmitter = require('events');
            const bridge = new EventEmitter();
            bridge.send = jest.fn();

            const agent = new Agent(bridge);

            const calls1 = [];
            const calls2 = [];
            agent._rendererInterfaces[1] = {
              supportsTogglingSuspense: true,
              overrideSuspenseMilestone: (s) => calls1.push(s),
            };
            agent._rendererInterfaces[2] = {
              supportsTogglingSuspense: true,
              overrideSuspenseMilestone: (s) => calls2.push(s),
            };

            agent.overrideSuspenseMilestone({
              rendererID: 2,
              suspendedSet: [30],
            });

            expect(calls1).toHaveLength(0);
            expect(calls2).toHaveLength(1);
            expect(calls2[0]).toEqual([30]);
          });
        });
    """)

    test_path = os.path.join(
        REPO,
        "packages/react-devtools-shared/src/__tests__/"
        "agent-milestone-targeting-test.js",
    )

    # config.source.js excludes react-devtools-shared via modulePathIgnorePatterns,
    # so we must use a custom config that re-includes it.
    jest_config_path = "/tmp/jest-devtools-source-config.js"
    jest_config_content = textwrap.dedent("""\
        'use strict';
        const baseConfig = require('/workspace/react/scripts/jest/config.source.js');
        module.exports = Object.assign({}, baseConfig, {
          modulePathIgnorePatterns: baseConfig.modulePathIgnorePatterns.filter(
            p => !p.includes('react-devtools-shared')
          ),
        });
    """)

    try:
        with open(test_path, "w") as f:
            f.write(test_content)
        with open(jest_config_path, "w") as f:
            f.write(jest_config_content)

        r = subprocess.run(
            [
                "node", "scripts/jest/jest.js",
                "--config", jest_config_path,
                "--no-watchman",
                "agent-milestone-targeting-test",
            ],
            cwd=REPO,
            capture_output=True,
            timeout=90,
            env={**os.environ,
                 "NODE_ENV": "development",
                 "RELEASE_CHANNEL": "experimental"},
        )
        stdout = r.stdout.decode(errors="replace")
        stderr = r.stderr.decode(errors="replace")
        assert r.returncode == 0, (
            f"Jest test failed (rc={r.returncode}):\n{stdout}\n{stderr}"
        )
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)
        if os.path.exists(jest_config_path):
            os.remove(jest_config_path)


# [pr_diff] fail_to_pass
def test_suspense_step_type_has_renderer_id():
    """SuspenseTimelineStep type must include a rendererID field."""
    src = Path(
        f"{REPO}/packages/react-devtools-shared/src/frontend/types.js"
    ).read_text()

    match = re.search(
        r"type\s+SuspenseTimelineStep\s*=\s*\{([\s\S]*?)\}", src
    )
    assert match, "SuspenseTimelineStep type definition not found in types.js"
    type_body = match.group(1)
    assert "rendererID" in type_body, (
        "SuspenseTimelineStep type must include rendererID field"
    )


# [pr_diff] fail_to_pass
def test_bridge_milestone_type_has_renderer_id():
    """OverrideSuspenseMilestone bridge type must include rendererID."""
    src = Path(
        f"{REPO}/packages/react-devtools-shared/src/bridge.js"
    ).read_text()

    match = re.search(
        r"type\s+OverrideSuspenseMilestone\s*=\s*\{([\s\S]*?)\}", src
    )
    assert match, "OverrideSuspenseMilestone type not found in bridge.js"
    type_body = match.group(1)
    assert "rendererID" in type_body, (
        "OverrideSuspenseMilestone type must include rendererID field"
    )


# [pr_diff] fail_to_pass
def test_store_passes_renderer_id():
    """Store timeline methods must thread rendererID through step construction."""
    src = Path(
        f"{REPO}/packages/react-devtools-shared/src/devtools/store.js"
    ).read_text()

    # pushTimelineStepsInDocumentOrder must accept rendererID as a parameter
    match = re.search(
        r"pushTimelineStepsInDocumentOrder\s*\(([\s\S]*?)\)\s*(?::\s*void)?\s*\{",
        src,
    )
    assert match, "pushTimelineStepsInDocumentOrder method not found in store.js"
    params = match.group(1)
    assert "rendererID" in params, (
        "pushTimelineStepsInDocumentOrder must accept rendererID parameter"
    )

    # getSuspendableDocumentOrderSuspenseTransition must also accept rendererID
    match2 = re.search(
        r"getSuspendableDocumentOrderSuspenseTransition\s*\(([\s\S]*?)\)",
        src,
    )
    assert match2, (
        "getSuspendableDocumentOrderSuspenseTransition not found in store.js"
    )
    params2 = match2.group(1)
    assert "rendererID" in params2, (
        "getSuspendableDocumentOrderSuspenseTransition must accept rendererID"
    )


# [pr_diff] fail_to_pass
def test_timeline_groups_by_renderer_id():
    """SuspenseTimeline must group suspended set per renderer, not send one bulk message."""
    src = Path(
        f"{REPO}/packages/react-devtools-shared/src/devtools/views/"
        "SuspenseTab/SuspenseTimeline.js"
    ).read_text()

    # The fix introduces a Map to group suspended sets by rendererID
    assert "suspendedSetByRendererID" in src, (
        "SuspenseTimeline must use a suspendedSetByRendererID Map "
        "to group suspensions per renderer"
    )

    # bridge.send must include rendererID in the overrideSuspenseMilestone message
    assert re.search(
        r"bridge\.send\(\s*'overrideSuspenseMilestone'\s*,\s*\{[^}]*rendererID",
        src,
    ), "bridge.send overrideSuspenseMilestone must include rendererID"
