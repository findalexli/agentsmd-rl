"""
Task: openclaw-msteams-thread-history-authz
Repo: openclaw/openclaw @ 7e086697152920c48651276ed8ae9c27354c092d
PR:   57723

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = "/workspace/openclaw"
HANDLER = f"{REPO}/extensions/msteams/src/monitor-handler/message-handler.ts"
VITEST_FILE = f"{REPO}/extensions/msteams/src/monitor-handler/_harbor_thread_filter.test.ts"

# Marker files written by vitest tests on success
F2P_PARENT_MARKER = "/tmp/harbor_f2p_parent_pass"
F2P_REPLY_MARKER = "/tmp/harbor_f2p_reply_pass"
F2P_NAME_MATCH_MARKER = "/tmp/harbor_f2p_name_match_pass"
P2P_ALL_MARKER = "/tmp/harbor_p2p_all_pass"


VITEST_SRC = textwrap.dedent(r'''
import { describe, expect, it, vi } from "vitest";
import { writeFileSync } from "node:fs";
import type { OpenClawConfig, PluginRuntime, RuntimeEnv } from "../../runtime-api.js";
import type { GraphThreadMessage } from "../graph-thread.js";
import type { MSTeamsMessageHandlerDeps } from "../monitor-handler.js";
import { setMSTeamsRuntime } from "../runtime.js";
import { createMSTeamsMessageHandler } from "./message-handler.js";

const runtimeApiMock = vi.hoisted(() => ({
  dispatchReplyFromConfigWithSettledDispatcher: vi.fn(async (params: { ctxPayload: unknown }) => ({
    queuedFinal: false,
    counts: {},
    capturedCtxPayload: params.ctxPayload,
  })),
}));

const graphThreadMock = vi.hoisted(() => ({
  resolveTeamGroupId: vi.fn(async () => "group-1"),
  fetchChannelMessage: vi.fn<
    (t: string, g: string, c: string, m: string) => Promise<GraphThreadMessage | undefined>
  >(async () => undefined),
  fetchThreadReplies: vi.fn<
    (t: string, g: string, c: string, m: string, l?: number) => Promise<GraphThreadMessage[]>
  >(async () => []),
}));

vi.mock("../../runtime-api.js", async () => {
  const actual = await vi.importActual<typeof import("../../runtime-api.js")>("../../runtime-api.js");
  return {
    ...actual,
    dispatchReplyFromConfigWithSettledDispatcher: runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher,
  };
});

vi.mock("../graph-thread.js", async () => {
  const actual = await vi.importActual<typeof import("../graph-thread.js")>("../graph-thread.js");
  return {
    ...actual,
    resolveTeamGroupId: graphThreadMock.resolveTeamGroupId,
    fetchChannelMessage: graphThreadMock.fetchChannelMessage,
    fetchThreadReplies: graphThreadMock.fetchThreadReplies,
  };
});

vi.mock("../reply-dispatcher.js", () => ({
  createMSTeamsReplyDispatcher: () => ({
    dispatcher: {},
    replyOptions: {},
    markDispatchIdle: vi.fn(),
  }),
}));

function makeDeps(cfg: OpenClawConfig) {
  const readAllowFromStore = vi.fn(async () => ["store-allowed-aad"]);
  const upsertPairingRequest = vi.fn(async () => null);
  const recordInboundSession = vi.fn(async () => undefined);
  setMSTeamsRuntime({
    logging: { shouldLogVerbose: () => false },
    system: { enqueueSystemEvent: vi.fn() },
    channel: {
      debounce: { resolveInboundDebounceMs: () => 0 },
      threadHistory: { resolveMaxFetchMessages: () => 25 },
      pairing: { readAllowFromStore, upsertPairingRequest },
      tokenProvider: { getAccessToken: async () => "fake-graph-token" },
      inbound: {
        formatSenderId: (id: string) => id,
        resolveGroupPolicyFields: (c: OpenClawConfig) => ({
          groupPolicy: c.channels?.msteams?.groupPolicy ?? "disabled",
          groupAllowFrom: c.channels?.msteams?.groupAllowFrom ?? [],
          dangerouslyAllowNameMatching: c.channels?.msteams?.dangerouslyAllowNameMatching ?? false,
        }),
      },
      text: { hasControlCommand: () => false },
      routing: {
        resolveAgentRoute: ({ peer }: { peer: { kind: string; id: string } }) => ({
          sessionKey: `msteams:${peer.kind}:${peer.id}`,
          agentId: "default",
          accountId: "default",
        }),
      },
      reply: {
        formatAgentEnvelope: ({ body }: { body: string }) => body,
        finalizeInboundContext: <T extends Record<string, unknown>>(ctx: T) => ctx,
      },
      session: { recordInboundSession },
    },
  } as unknown as PluginRuntime);

  const conversationStore = {
    get: vi.fn(async () => ({
      conversation: { id: "19:channel@thread.tacv2", conversationType: "channel" },
      serviceUrl: "https://smba.trafficmanager.net/teams/",
      bot: { id: "bot-id", name: "Bot" },
    })),
    set: vi.fn(async () => undefined),
  };

  const deps: MSTeamsMessageHandlerDeps = {
    cfg,
    env: { OPENCLAW_MSTEAMS_APP_ID: "app-id" } as RuntimeEnv,
    conversationStore,
    log: {
      info: vi.fn(), warn: vi.fn(), error: vi.fn(), debug: vi.fn(),
    } as unknown as MSTeamsMessageHandlerDeps["log"],
  };

  return { conversationStore, deps };
}

function makeActivity(overrides: Record<string, unknown> = {}) {
  return {
    id: "current-msg",
    type: "message",
    text: "Hey can you help me?",
    from: { id: "bob-bf-id", aadObjectId: "bob-aad", name: "Bob" },
    recipient: { id: "bot-id", name: "Bot" },
    conversation: { id: "19:channel@thread.tacv2", conversationType: "channel" },
    channelData: { team: { id: "team456", name: "Team" }, channel: { name: "General" } },
    replyToId: "parent-msg",
    attachments: [],
    ...overrides,
  };
}

function makeAllowlistCfg(extra: Record<string, unknown> = {}): OpenClawConfig {
  return {
    channels: {
      msteams: {
        groupPolicy: "allowlist",
        groupAllowFrom: ["bob-aad"],
        requireMention: false,
        teams: { team456: { channels: { "19:channel@thread.tacv2": { requireMention: false } } } },
        ...extra,
      },
    },
  } as OpenClawConfig;
}

function extractBody(mock: typeof runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher): string {
  const dispatched = mock.mock.calls[0]?.[0];
  expect(dispatched).toBeTruthy();
  return String((dispatched?.ctxPayload as { BodyForAgent?: string }).BodyForAgent ?? "");
}

describe("harbor: thread history allowlist filtering", () => {
  // ── F2P: Non-allowlisted PARENT message excluded ──
  it("excludes non-allowlisted parent sender from thread context", async () => {
    runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mockClear();
    graphThreadMock.fetchChannelMessage.mockReset();
    graphThreadMock.fetchThreadReplies.mockReset();

    graphThreadMock.fetchChannelMessage.mockResolvedValue({
      id: "parent-msg",
      from: { user: { id: "eve-aad", displayName: "Eve" } },
      body: { content: "Injected payload from attacker", contentType: "text" },
    });
    graphThreadMock.fetchThreadReplies.mockResolvedValue([
      {
        id: "bob-reply",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Legitimate context from Bob", contentType: "text" },
      },
      {
        id: "current-msg",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Hey can you help me?", contentType: "text" },
      },
    ]);

    const { deps } = makeDeps(makeAllowlistCfg());
    const handler = createMSTeamsMessageHandler(deps);
    await handler({
      activity: makeActivity(),
      sendActivity: vi.fn(async () => undefined),
    } as unknown as Parameters<typeof handler>[0]);

    const body = extractBody(runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher);
    expect(body).not.toContain("Eve");
    expect(body).not.toContain("Injected payload");
    expect(body).toContain("Bob");
    expect(body).toContain("Legitimate context");
    writeFileSync("''' + F2P_PARENT_MARKER + r'''", "1");
  });

  // ── F2P: Non-allowlisted REPLY sender excluded ──
  it("excludes non-allowlisted reply sender from thread context", async () => {
    runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mockClear();
    graphThreadMock.fetchChannelMessage.mockReset();
    graphThreadMock.fetchThreadReplies.mockReset();

    graphThreadMock.fetchChannelMessage.mockResolvedValue({
      id: "parent-msg",
      from: { user: { id: "bob-aad", displayName: "Bob" } },
      body: { content: "Original question from Bob", contentType: "text" },
    });
    graphThreadMock.fetchThreadReplies.mockResolvedValue([
      {
        id: "mallory-reply",
        from: { user: { id: "mallory-aad", displayName: "Mallory" } },
        body: { content: "Sneaky injection from Mallory", contentType: "text" },
      },
      {
        id: "current-msg",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Hey can you help me?", contentType: "text" },
      },
    ]);

    const { deps } = makeDeps(makeAllowlistCfg());
    const handler = createMSTeamsMessageHandler(deps);
    await handler({
      activity: makeActivity(),
      sendActivity: vi.fn(async () => undefined),
    } as unknown as Parameters<typeof handler>[0]);

    const body = extractBody(runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher);
    expect(body).not.toContain("Mallory");
    expect(body).not.toContain("Sneaky injection");
    expect(body).toContain("Bob");
    expect(body).toContain("Original question");
    writeFileSync("''' + F2P_REPLY_MARKER + r'''", "1");
  });

  // ── F2P: dangerouslyAllowNameMatching works in filter ──
  // A naive ID-only filter would exclude name-matched users; the correct fix
  // must use resolveMSTeamsAllowlistMatch which honours display-name matching.
  it("includes name-matched user and excludes non-matched via dangerouslyAllowNameMatching", async () => {
    runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mockClear();
    graphThreadMock.fetchChannelMessage.mockReset();
    graphThreadMock.fetchThreadReplies.mockReset();

    // Parent: Alice has no AAD id, only display name — matched via name matching
    graphThreadMock.fetchChannelMessage.mockResolvedValue({
      id: "parent-msg",
      from: { user: { displayName: "Alice" } },
      body: { content: "Allowlisted by display name", contentType: "text" },
    });
    graphThreadMock.fetchThreadReplies.mockResolvedValue([
      {
        id: "mallory-reply",
        from: { user: { id: "mallory-aad", displayName: "Mallory" } },
        body: { content: "Attack payload from Mallory", contentType: "text" },
      },
      {
        id: "current-msg",
        from: { user: { id: "alice-aad", displayName: "Alice" } },
        body: { content: "Current message from Alice", contentType: "text" },
      },
    ]);

    const { deps } = makeDeps({
      channels: {
        msteams: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["alice-aad", "alice"],
          dangerouslyAllowNameMatching: true,
          requireMention: false,
          teams: { team456: { channels: { "19:channel@thread.tacv2": { requireMention: false } } } },
        },
      },
    } as OpenClawConfig);

    const handler = createMSTeamsMessageHandler(deps);
    await handler({
      activity: makeActivity({
        from: { id: "alice-bf-id", aadObjectId: "alice-aad", name: "Alice" },
      }),
      sendActivity: vi.fn(async () => undefined),
    } as unknown as Parameters<typeof handler>[0]);

    const body = extractBody(runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher);
    // Alice's parent message (matched by display name) should be included
    expect(body).toContain("Allowlisted by display name");
    // Mallory (no ID or name match) should be excluded
    expect(body).not.toContain("Mallory");
    expect(body).not.toContain("Attack payload");
    writeFileSync("''' + F2P_NAME_MATCH_MARKER + r'''", "1");
  });

  // ── P2P: All-allowlisted senders' messages still included ──
  it("includes all messages when all senders are on the allowlist", async () => {
    runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mockClear();
    graphThreadMock.fetchChannelMessage.mockReset();
    graphThreadMock.fetchThreadReplies.mockReset();

    graphThreadMock.fetchChannelMessage.mockResolvedValue({
      id: "parent-msg",
      from: { user: { id: "alice-aad", displayName: "Alice" } },
      body: { content: "Original question from Alice", contentType: "text" },
    });
    graphThreadMock.fetchThreadReplies.mockResolvedValue([
      {
        id: "bob-reply",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Reply from Bob with details", contentType: "text" },
      },
      {
        id: "current-msg",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Follow-up from Bob", contentType: "text" },
      },
    ]);

    const { deps } = makeDeps({
      channels: {
        msteams: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["bob-aad", "alice-aad"],
          requireMention: false,
          teams: { team456: { channels: { "19:channel@thread.tacv2": { requireMention: false } } } },
        },
      },
    } as OpenClawConfig);

    const handler = createMSTeamsMessageHandler(deps);
    await handler({
      activity: makeActivity(),
      sendActivity: vi.fn(async () => undefined),
    } as unknown as Parameters<typeof handler>[0]);

    const body = extractBody(runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher);
    expect(body).toContain("Alice");
    expect(body).toContain("Original question");
    expect(body).toContain("Bob");
    expect(body).toContain("Reply from Bob");
    writeFileSync("''' + P2P_ALL_MARKER + r'''", "1");
  });
});
''')


@pytest.fixture(scope="module")
def vitest_results():
    """Write vitest test file, run it, return marker-file results, then clean up."""
    for m in (F2P_PARENT_MARKER, F2P_REPLY_MARKER, F2P_NAME_MATCH_MARKER, P2P_ALL_MARKER):
        try:
            os.remove(m)
        except FileNotFoundError:
            pass

    Path(VITEST_FILE).write_text(VITEST_SRC)

    try:
        r = subprocess.run(
            ["pnpm", "exec", "vitest", "run",
             "extensions/msteams/src/monitor-handler/_harbor_thread_filter.test.ts",
             "--reporter=verbose", "--no-color"],
            cwd=REPO, capture_output=True, timeout=180,
        )
        output = r.stdout.decode() + "\n" + r.stderr.decode()
    except subprocess.TimeoutExpired:
        output = "vitest timed out"
    finally:
        try:
            os.remove(VITEST_FILE)
        except FileNotFoundError:
            pass

    return {
        "f2p_parent": os.path.exists(F2P_PARENT_MARKER),
        "f2p_reply": os.path.exists(F2P_REPLY_MARKER),
        "f2p_name_match": os.path.exists(F2P_NAME_MATCH_MARKER),
        "p2p_all": os.path.exists(P2P_ALL_MARKER),
        "output": output,
    }


def _read_handler():
    p = Path(HANDLER)
    assert p.exists(), f"Handler file not found: {HANDLER}"
    return p.read_text()


def _added_lines():
    """Return only '+' lines from git diff of the handler file."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--",
         "extensions/msteams/src/monitor-handler/message-handler.ts"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    return [l for l in r.stdout.decode().splitlines()
            if l.startswith("+") and not l.startswith("+++")]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_thread_filter_excludes_nonallowlisted_parent(vitest_results):
    """Non-allowlisted parent message content must not appear in BodyForAgent."""
    assert vitest_results["f2p_parent"], (
        "Vitest F2P (parent) failed — non-allowlisted parent message was not excluded "
        f"from thread context.\n{vitest_results['output'][-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_thread_filter_excludes_nonallowlisted_reply(vitest_results):
    """Non-allowlisted reply sender content must not appear in BodyForAgent."""
    assert vitest_results["f2p_reply"], (
        "Vitest F2P (reply) failed — non-allowlisted reply message was not excluded "
        f"from thread context.\n{vitest_results['output'][-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_thread_filter_name_matching(vitest_results):
    """Filter must use resolveMSTeamsAllowlistMatch (not naive ID comparison)
    so that dangerouslyAllowNameMatching is honoured for thread history."""
    assert vitest_results["f2p_name_match"], (
        "Vitest F2P (name matching) failed — dangerouslyAllowNameMatching not honoured "
        f"in thread history filter.\n{vitest_results['output'][-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_thread_filter_includes_all_allowlisted(vitest_results):
    """When all thread senders are allowlisted, all messages appear in BodyForAgent."""
    assert vitest_results["p2p_all"], (
        "Vitest P2P failed — allowlisted messages were incorrectly excluded "
        f"from thread context.\n{vitest_results['output'][-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_handler_export_exists():
    """createMSTeamsMessageHandler must still be exported."""
    src = _read_handler()
    assert re.search(
        r"export\s+function\s+createMSTeamsMessageHandler", src
    ), "createMSTeamsMessageHandler export not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_handler_modified():
    """Handler file must be modified from base commit (anti-stub)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--",
         "extensions/msteams/src/monitor-handler/message-handler.ts"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    diff = r.stdout.decode()
    assert len(diff.strip()) > 0, "Handler file is unchanged from base commit"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md / extensions/CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:146 @ 7e086697152920c48651276ed8ae9c27354c092d
def test_no_ts_nocheck():
    """Must not add @ts-nocheck or @ts-ignore."""
    src = _read_handler()
    assert "@ts-nocheck" not in src, "Found @ts-nocheck — fix root cause instead"
    added = _added_lines()
    for line in added:
        assert "@ts-ignore" not in line, (
            f"New code adds @ts-ignore — use proper types instead: {line.strip()}"
        )


# [agent_config] pass_to_pass — CLAUDE.md:144 @ 7e086697152920c48651276ed8ae9c27354c092d
def test_no_new_any_type():
    """New code must not introduce explicit 'any' type annotations."""
    for line in _added_lines():
        assert not re.search(r":\s*any\b|as\s+any\b|<any>", line), (
            f"New code introduces 'any' type: {line.strip()}"
        )


# [agent_config] pass_to_pass — CLAUDE.md:146 @ 7e086697152920c48651276ed8ae9c27354c092d
def test_no_inline_lint_suppression():
    """New code must not add eslint-disable or oxlint-ignore inline suppressions."""
    for line in _added_lines():
        assert not re.search(r"eslint-disable|oxlint-ignore|@ts-expect-error", line), (
            f"New code adds lint suppression: {line.strip()}"
        )


# [agent_config] pass_to_pass — extensions/CLAUDE.md:29-30 @ 7e086697152920c48651276ed8ae9c27354c092d
def test_no_extension_boundary_violation():
    """Extension code must not import from src/**, src/plugin-sdk-internal/**, or
    escape the package root via deep relative imports."""
    for line in _added_lines():
        if "import" not in line and "require" not in line:
            continue
        assert not re.search(r'''from\s+['"]src/''', line), (
            f"Extension imports from src/ — use openclaw/plugin-sdk/* instead: {line.strip()}"
        )
        assert not re.search(r'''from\s+['"]\.\.\/\.\.\/\.\.\/\.\.\/?''', line), (
            f"Import escapes extension package root: {line.strip()}"
        )
