"""
Task: bun-webcore-memory-safety-fixes
Repo: oven-sh/bun @ 639bc4351cd7b5daa38b99d47a506dec68e95353
PR:   28494

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
WEBCORE = f"{REPO}/src/bun.js/bindings/webcore"


# ---------------------------------------------------------------------------
# Helpers — C++ source analysis
# AST-only because: Bun's C++ requires Zig toolchain + custom build system;
# cannot compile or link individual translation units in the test container.
# ---------------------------------------------------------------------------

def strip_comments(code: str) -> str:
    """Remove C/C++ comments, preserving string literals."""
    result = []
    i = 0
    in_string = None
    while i < len(code):
        c = code[i]
        if in_string:
            result.append(c)
            if c == '\\' and i + 1 < len(code):
                result.append(code[i + 1])
                i += 2
                continue
            if c == in_string:
                in_string = None
            i += 1
            continue
        if c in ('"', "'"):
            in_string = c
            result.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < len(code) and code[i + 1] == '/':
            while i < len(code) and code[i] != '\n':
                i += 1
            continue
        if c == '/' and i + 1 < len(code) and code[i + 1] == '*':
            i += 2
            while i + 1 < len(code) and not (code[i] == '*' and code[i + 1] == '/'):
                i += 1
            i += 2
            continue
        result.append(c)
        i += 1
    return ''.join(result)


def extract_function(text: str, name: str) -> str | None:
    """Extract function body using brace matching."""
    pat = re.escape(name) + r'[^{]*\{'
    m = re.search(pat, text)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[m.end():i]
    return None


def read_stripped(path: str) -> str:
    return strip_comments(Path(path).read_text())


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — source files must exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """All five WebCore source files must exist and be non-empty."""
    files = [
        "MessagePortChannel.cpp",
        "JSAbortController.cpp",
        "BroadcastChannel.cpp",
        "EventListenerMap.cpp",
        "EventListenerMap.h",
    ]
    for f in files:
        p = Path(f"{WEBCORE}/{f}")
        assert p.exists() and p.stat().st_size > 0, f"{f} missing or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_message_port_closed_guard():
    """postMessageToRemote must check m_isClosed before appending to m_pendingMessages."""
    text = read_stripped(f"{WEBCORE}/MessagePortChannel.cpp")
    body = extract_function(text, 'postMessageToRemote')
    assert body, "postMessageToRemote function not found"

    guard = re.search(
        r'if\s*\([^)]*m_isClosed\b[^)]*\)\s*(?:\{[^}]*)?return\s+false',
        body, re.DOTALL,
    )
    assert guard, "No conditional m_isClosed guard with return false"

    first_pending = body.find('m_pendingMessages')
    assert first_pending >= 0, "m_pendingMessages not found in function"
    assert guard.start() < first_pending, "m_isClosed guard must appear before m_pendingMessages"


# [pr_diff] fail_to_pass
def test_message_port_variable_index():
    """m_isClosed guard must use a computed index, not a hardcoded literal."""
    text = read_stripped(f"{WEBCORE}/MessagePortChannel.cpp")
    body = extract_function(text, 'postMessageToRemote')
    assert body, "postMessageToRemote function not found"

    match = re.search(r'm_isClosed\s*\[\s*([^\]]+)\s*\]', body)
    if match:
        index_expr = match.group(1).strip()
        assert not re.match(r'^\d+$', index_expr), \
            f"m_isClosed uses hardcoded index '{index_expr}' — must use variable"
    else:
        # Plain bool member (no array) is also acceptable
        assert re.search(r'if\s*\([^)]*m_isClosed\b', body), \
            "m_isClosed guard not found"


# [pr_diff] fail_to_pass
def test_abort_signal_reason_visited():
    """visitChildrenImpl must visit signal().reason() via a chained call."""
    text = read_stripped(f"{WEBCORE}/JSAbortController.cpp")
    body = extract_function(text, 'visitChildrenImpl')
    assert body, "visitChildrenImpl function not found"

    assert re.search(r'signal\(\)\s*(?:->|\.\s*)reason\(\)', body), \
        "signal() and reason() must be chained in the same expression"

    visited = (
        re.search(r'reason\(\)\s*(?:->|\.\s*)visit\s*\(', body)
        or re.search(r'visitor\s*\.\s*append\s*\(', body)
        or re.search(r'\.visit\s*\(', body)
    )
    assert visited, "signal().reason() result must be visited/appended"


# [pr_diff] fail_to_pass
def test_broadcast_channel_weak_ptr():
    """allBroadcastChannels map must use a template pointer wrapper, not a raw pointer."""
    text = read_stripped(f"{WEBCORE}/BroadcastChannel.cpp")

    # Match either the function return type or the NeverDestroyed static variable
    # Use [^<>]+ to avoid greedy consumption through nested angle brackets
    map_decl = re.search(
        r'UncheckedKeyHashMap\s*<\s*BroadcastChannelIdentifier\s*,\s*([^<>]+(?:<[^>]+>)?)\s*>',
        text,
    )
    assert map_decl, "allBroadcastChannels map declaration not found"

    val_type = map_decl.group(1).strip()
    stripped = re.sub(r'\b(const|volatile|mutable)\s*', '', val_type).strip()
    assert not stripped.endswith('*'), \
        f"Map value type is raw pointer '{val_type}' — must use smart/weak pointer"
    assert re.search(r'\w+\s*<\s*BroadcastChannel\s*>', val_type), \
        f"Map value type '{val_type}' must be a template wrapper like WeakPtr<BroadcastChannel>"


# [pr_diff] fail_to_pass
def test_event_listener_map_thread_affinity():
    """At least 4 of 5 EventListenerMap mutators must have thread affinity checks before Locker."""
    text = read_stripped(f"{WEBCORE}/EventListenerMap.cpp")

    mutators = [
        'EventListenerMap::clear',
        'EventListenerMap::replace',
        'EventListenerMap::add',
        'EventListenerMap::remove',
        'EventListenerMap::removeFirstEventListenerCreatedFromMarkup',
    ]
    count = 0
    for name in mutators:
        pat = re.escape(name) + r'\s*\([^)]*\)\s*(?:const\s*)?\{(.*?)(?=\n(?:void|bool|static|unsigned)\s|\Z)'
        fn = re.search(pat, text, re.DOTALL)
        if not fn:
            continue
        body = fn.group(1)
        lock_pos = body.find('Locker')
        if lock_pos < 0:
            lock_pos = len(body)
        pre_lock = body[:lock_pos]

        # Option A: function name contains "thread" (e.g. releaseAssertOrSetThreadUID())
        call_a = re.search(r'\w*[Tt]hread\w*\s*\(', pre_lock)

        # Option B: ASSERT with thread-related argument
        call_b = re.search(r'(?:releaseAssert|RELEASE_ASSERT|ASSERT)\s*\(([^)]*)\)', pre_lock)
        b_ok = call_b and re.search(r'[Tt]hread|m_thread', call_b.group(1))

        if call_a or b_ok:
            count += 1

    assert count >= 4, \
        f"Only {count}/5 mutators have thread affinity checks — need at least 4"


# [pr_diff] fail_to_pass
def test_event_listener_map_thread_uid_member():
    """EventListenerMap.h must declare a thread UID member variable."""
    text = read_stripped(f"{WEBCORE}/EventListenerMap.h")
    assert re.search(
        r'(?:uint\d+_t|ThreadIdentifier|Thread::uid_t|unsigned)\s+m_thread\w*\s*[;={]', text,
    ), "EventListenerMap.h must have a thread UID member (e.g. uint32_t m_threadUID)"


# [pr_diff] fail_to_pass
def test_event_listener_map_gc_thread_exemption():
    """Thread affinity helper must exempt GC threads via a function call."""
    text = read_stripped(f"{WEBCORE}/EventListenerMap.h")
    assert re.search(r'mayBeGCThread\s*\(', text) or re.search(r'isGCThread\s*\(', text), \
        "Thread affinity helper must call mayBeGCThread() or isGCThread()"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / agent_config) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_broadcast_channel_still_registers():
    """BroadcastChannel constructor must still register in the global map."""
    text = read_stripped(f"{WEBCORE}/BroadcastChannel.cpp")
    assert 'allBroadcastChannels().add' in text or 'allBroadcastChannels().set' in text, \
        "BroadcastChannel no longer registers in global map — regression"


# [pr_diff] pass_to_pass
def test_visit_children_retains_base_calls():
    """visitChildrenImpl must retain Base::visitChildren and addWebCoreOpaqueRoot."""
    text = read_stripped(f"{WEBCORE}/JSAbortController.cpp")
    assert 'Base::visitChildren' in text, "Base::visitChildren call removed — regression"
    assert 'addWebCoreOpaqueRoot' in text, "addWebCoreOpaqueRoot call removed — regression"


# [agent_config] pass_to_pass — CLAUDE.md:228 @ 639bc4351cd7b5daa38b99d47a506dec68e95353
def test_broadcast_channel_locker_style():
    """BroadcastChannel.cpp must follow existing Locker pattern (CLAUDE.md: 'Follow existing code style')."""
    text = read_stripped(f"{WEBCORE}/BroadcastChannel.cpp")
    assert re.search(r'Locker\s+\w+\s*\{\s*allBroadcastChannelsLock', text), \
        "BroadcastChannel.cpp must use 'Locker name { allBroadcastChannelsLock }' pattern"
