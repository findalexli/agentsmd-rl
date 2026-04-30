#!/usr/bin/env python3
"""
Task: bun-webcore-memory-safety-fixes
Repo: oven-sh/bun @ 639bc4351cd7b5daa38b99d47a506dec68e95353
PR:   28494

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Bun's WebCore C++ requires Zig toolchain + custom build system,
so full compilation is not possible in the test container. Tests use:
  1. subprocess to compile standalone C++ concept programs (behavioral)
  2. subprocess to verify git diff against base commit (proves changes applied)
  3. Inline source analysis (verifies fix patterns are correct, without gold-specific details)
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
WEBCORE = f"{REPO}/src/bun.js/bindings/webcore"
BASE_COMMIT = "639bc4351cd7b5daa38b99d47a506dec68e95353"


def _compile_run_cpp(name: str, code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    src = Path(f"{REPO}/_eval_{name}.cpp")
    exe = Path(f"{REPO}/_eval_{name}")
    src.write_text(code)
    try:
        r = subprocess.run(["g++", "-std=c++17", "-o", str(exe), str(src)],
            capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            return r
        return subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout)
    finally:
        src.unlink(missing_ok=True)
        exe.unlink(missing_ok=True)


def _git_diff(filepath: str) -> str:
    r = subprocess.run(["git", "diff", BASE_COMMIT, "--", filepath],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    return r.stdout


def strip_comments(code: str) -> str:
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
                i += 2
            continue
        result.append(c)
        i += 1
    return ''.join(result)


def extract_function(text: str, name: str) -> str | None:
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


def test_message_port_closed_guard():
    """postMessageToRemote must check port closed state before appending to pending messages."""
    r = _compile_run_cpp("msgport", R"""
#include <vector>
#include <cstdio>
struct MockChannel {
    bool m_isClosed[2] = {false, false};
    std::vector<int> m_pendingMessages[2];
    bool postMessageToRemote(int msg, size_t i) {
        if (m_isClosed[i])
            return false;
        m_pendingMessages[i].push_back(msg);
        return true;
    }
};
int main() {
    MockChannel ch;
    ch.m_isClosed[1] = true;
    if (ch.postMessageToRemote(42, 1) != false) return 1;
    if (!ch.m_pendingMessages[1].empty()) return 2;
    if (ch.postMessageToRemote(42, 0) != true) return 3;
    if (ch.m_pendingMessages[0].size() != 1) return 4;
    std::printf("PASS\n");
    return 0;
}
""")
    assert r.returncode == 0, f"C++ concept test failed: {r.stderr}"
    assert "PASS" in r.stdout

    diff = _git_diff("src/bun.js/bindings/webcore/MessagePortChannel.cpp")
    has_closed_check = ("m_isClosed" in diff or "isClosed" in diff or "closed" in diff.lower())
    assert has_closed_check, "MessagePortChannel diff does not include closed-state check"
    assert "return false" in diff, "MessagePortChannel diff does not include 'return false' guard behavior"

    text = read_stripped(f"{WEBCORE}/MessagePortChannel.cpp")
    body = extract_function(text, 'MessagePortChannel::postMessageToRemote')
    assert body, "postMessageToRemote function not found"

    guard_patterns = [
        r'if\s*\([^)]*(?:m_isClosed|isClosed|closed)[^)]*\)\s*(?:\{[^}]*)?\s*return\s+false',
        r'return\s+false\s*;\s*[^}]*?(?:m_isClosed|isClosed|closed)',
    ]
    guard = None
    for pattern in guard_patterns:
        guard = re.search(pattern, body, re.DOTALL)
        if guard:
            break
    assert guard, "No closed-state guard with return false found"

    first_pending = body.find('m_pendingMessages')
    assert first_pending >= 0, "m_pendingMessages not found in function"
    assert guard.start() < first_pending, "Closed-state guard must appear before m_pendingMessages"


def test_message_port_variable_index():
    """Closed-state guard uses computed index, not hardcoded literal."""
    diff = _git_diff("src/bun.js/bindings/webcore/MessagePortChannel.cpp")
    text = read_stripped(f"{WEBCORE}/MessagePortChannel.cpp")
    body = extract_function(text, 'MessagePortChannel::postMessageToRemote')
    assert body, "postMessageToRemote function not found"

    match = re.search(r'(?:m_isClosed|isClosed)\s*\[\s*([^\]]+)\s*\]', body)
    if match:
        index_expr = match.group(1).strip()
        assert not re.match(r'^(?:0|1)$', index_expr), \
            f"Closed-state guard uses hardcoded index '{index_expr}' — must use variable"
    else:
        assert re.search(r'if\s*\([^)]*(?:m_isClosed|isClosed)\b', body), \
            "Closed-state guard not found"


def test_abort_signal_reason_visited():
    """visitChildrenImpl visits the signal's reason (GC-visited to prevent collection)."""
    diff = _git_diff("src/bun.js/bindings/webcore/JSAbortController.cpp")
    assert "reason" in diff, "JSAbortController diff does not include reason() visit"

    text = read_stripped(f"{WEBCORE}/JSAbortController.cpp")
    body = extract_function(text, 'visitChildrenImpl')
    assert body, "visitChildrenImpl function not found"

    reason_visited = (
        re.search(r'signal\s*\(\s*\)\s*(?:->|\.\s*)\s*reason\s*\(\s*\)\s*(?:->|\.\s*)\s*visit\s*\(\s*visitor\s*\)', body) or
        re.search(r'signal\s*\(?\s*\)\s*(?:->|\.)\s*reason\s*\(?\s*\)\s*(?:->|\.)\s*visit\s*\(\s*visitor\s*\)', body) or
        re.search(r'reason\s*\(\s*\)\s*(?:->|\.\s*)\s*visit\s*\(\s*visitor', body) or
        re.search(r'reason\s*\(\s*\)\s*\.\s*visit\s*\(', body)
    )
    assert reason_visited, "signal's reason must be visited in visitChildrenImpl"


def test_broadcast_channel_weak_ptr():
    """allBroadcastChannels map uses smart pointer (weak pointer wrapper), not raw pointer."""
    r = _compile_run_cpp("weakptr", R"""
#include <memory>
#include <cstdio>
int main() {
    std::weak_ptr<int> wp;
    {
        auto sp = std::make_shared<int>(42);
        wp = sp;
        if (wp.expired()) return 1;
        if (*wp.lock() != 42) return 2;
    }
    if (!wp.expired()) return 3;
    if (wp.lock() != nullptr) return 4;
    std::printf("PASS\n");
    return 0;
}
""")
    assert r.returncode == 0, f"C++ weak_ptr concept test failed: {r.stderr}"
    assert "PASS" in r.stdout

    diff = _git_diff("src/bun.js/bindings/webcore/BroadcastChannel.cpp")
    has_smart_ptr = ("ThreadSafeWeakPtr" in diff or "WeakPtr" in diff or "weak_ptr" in diff)
    assert has_smart_ptr, "BroadcastChannel diff does not show smart pointer introduction"

    text = read_stripped(f"{WEBCORE}/BroadcastChannel.cpp")
    map_decl = re.search(
        r'UncheckedKeyHashMap\s*<\s*BroadcastChannelIdentifier\s*,\s*([^<>]+(?:<[^>]+>)?)\s*>', text)
    assert map_decl, "allBroadcastChannels map declaration not found"

    val_type = map_decl.group(1).strip()
    stripped = re.sub(r'\b(const|volatile|mutable)\s*', '', val_type).strip()
    assert not stripped.endswith('*'), \
        f"Map value type is raw pointer '{val_type}' — must use smart/weak pointer"
    has_template_wrapper = re.search(r'\w+\s*<\s*BroadcastChannel\s*>', val_type)
    assert has_template_wrapper, \
        f"Map value type '{val_type}' must be a template wrapper (smart/weak pointer)"


def test_event_listener_map_thread_affinity():
    """At least 4/5 EventListenerMap mutators have thread affinity checks before Locker."""
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
        body = extract_function(text, name)
        if not body:
            continue
        lock_pos = body.find('Locker')
        if lock_pos < 0:
            lock_pos = len(body)
        pre_lock = body[:lock_pos]

        # The original code has nothing before Locker in any mutator.
        # Any function call or assertion added before Locker is the thread
        # affinity check.  Accept broad patterns so alternative helper names,
        # inline assertions, or different naming conventions all pass.
        has_thread_check = (
            # Named helper containing thread/uid/owner/affinity keywords
            re.search(r'\w*(?:[Tt]hread|[Uu]id|[Oo]wner|[Aa]ffinity)\w*\s*\(', pre_lock) or
            # Any assertion macro (ASSERT / RELEASE_ASSERT / releaseAssert)
            re.search(r'(?:releaseAssert|RELEASE_ASSERT|ASSERT)\s*\(', pre_lock) or
            # Any standalone function call on its own line (original has none)
            re.search(r'^\s+\w[\w:]*\s*\(', pre_lock, re.MULTILINE)
        )
        if has_thread_check:
            count += 1

    assert count >= 4, f"Only {count}/5 mutators have thread affinity checks — need at least 4"


def test_event_listener_map_thread_uid_member():
    """EventListenerMap.h declares a member variable for tracking thread identity."""
    diff = _git_diff("src/bun.js/bindings/webcore/EventListenerMap.h")
    assert diff, "EventListenerMap.h has no changes in diff"

    text = read_stripped(f"{WEBCORE}/EventListenerMap.h")
    # Accept various type/name combinations for a thread identity member.
    # Types: uint*_t, unsigned, long, size_t, int, ThreadIdentifier,
    #        std::thread::id, std::atomic<...>, Thread::uid_t
    type_pat = r'(?:uint\d+_t|ThreadIdentifier|Thread::uid_t|unsigned|long|size_t|int|std::atomic\s*<[^>]+>|std::thread::id)'
    # Names: m_*thread*, m_*uid*, m_*owner*, m_*affinity*, m_*tid*
    name_pat = r'm_\w*(?:uid|thread|owner|affinity|tid)\w*'
    has_thread_member = (
        re.search(type_pat + r'\s+' + name_pat + r'\s*[;={]', text, re.IGNORECASE) or
        # Fallback: any new m_ member added in the diff (not m_entries or m_lock)
        re.search(r'^\+.*\bm_(?!entries\b|lock\b)\w+\s*[;={]', diff, re.MULTILINE)
    )
    assert has_thread_member, "EventListenerMap.h must have a member variable for thread identity tracking"


def test_event_listener_map_gc_thread_exemption():
    """Thread affinity helper exempts GC threads via function call."""
    diff = _git_diff("src/bun.js/bindings/webcore/EventListenerMap.h")
    assert diff, "EventListenerMap.h has no changes in diff"

    text = read_stripped(f"{WEBCORE}/EventListenerMap.h")
    has_gc_check = (
        re.search(r'mayBeGCThread\s*\(', text) or
        re.search(r'isGCThread\s*\(', text) or
        re.search(r'gcThread\s*\(', text, re.IGNORECASE) or
        re.search(r'GCThread\s*\(', text) or
        re.search(r'isCollectorThread\s*\(', text) or
        re.search(r'isSweep\w*Thread\s*\(', text) or
        re.search(r'isGarbageCollect\w*\s*\(', text, re.IGNORECASE) or
        # GC-related keyword near thread-related keyword in the diff
        re.search(r'(?:[Gg][Cc]|[Gg]arbage|[Cc]ollect|[Ss]weep)\w*.*[Tt]hread', diff)
    )
    assert has_gc_check, "Thread affinity helper must exempt GC/sweeper threads"


def test_broadcast_channel_still_registers():
    """BroadcastChannel constructor must still register in the global map."""
    text = read_stripped(f"{WEBCORE}/BroadcastChannel.cpp")
    assert 'allBroadcastChannels().add' in text or 'allBroadcastChannels().set' in text, \
        "BroadcastChannel no longer registers in global map — regression"


def test_visit_children_retains_base_calls():
    """visitChildrenImpl must retain Base::visitChildren and addWebCoreOpaqueRoot."""
    text = read_stripped(f"{WEBCORE}/JSAbortController.cpp")
    assert 'Base::visitChildren' in text, "Base::visitChildren call removed — regression"
    assert 'addWebCoreOpaqueRoot' in text, "addWebCoreOpaqueRoot call removed — regression"


def test_broadcast_channel_locker_style():
    """BroadcastChannel.cpp follows existing Locker pattern."""
    text = read_stripped(f"{WEBCORE}/BroadcastChannel.cpp")
    assert re.search(r'Locker\s+\w+\s*\{\s*allBroadcastChannelsLock', text), \
        "BroadcastChannel.cpp must use 'Locker name { allBroadcastChannelsLock }' pattern"


def test_repo_source_structure():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        p = Path(filepath)
        assert p.exists() and p.stat().st_size > 100, f"{filepath} missing or too small"
        content = p.read_text()
        assert "#include" in content, f"{filepath} missing includes"
        assert "namespace WebCore" in content, f"{filepath} missing WebCore namespace"


def test_repo_headers_valid():
    headers = [f"{WEBCORE}/EventListenerMap.h", f"{WEBCORE}/BroadcastChannel.h"]
    for filepath in headers:
        content = Path(filepath).read_text()
        has_guard = ("#pragma once" in content or ("#ifndef" in content and "#define" in content))
        assert has_guard, f"{filepath} missing include guard"
        assert any(inc in content for inc in ["<wtf/", '"wtf/', "<WebKit/", "config.h"]), \
            f"{filepath} missing expected WTF/WebKit includes"


def test_repo_git_valid():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 0, f"Git repository check failed: {r.stderr}"
    head_commit = r.stdout.strip()
    assert head_commit == BASE_COMMIT, f"HEAD ({head_commit}) != expected base ({BASE_COMMIT})"


def test_repo_line_endings():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        content = Path(filepath).read_bytes()
        assert b'\r\n' not in content, f"{filepath} has CRLF line endings"


def test_repo_cpp_toolchain():
    code = R"""
#include <vector>
#include <memory>
#include <cstdio>
int main() {
    std::weak_ptr<int> wp;
    { auto sp = std::make_shared<int>(42); wp = sp; if (wp.expired()) return 1; }
    if (!wp.expired()) return 2;
    std::vector<int> vec; vec.push_back(1);
    if (vec.size() != 1) return 3;
    std::printf("PASS\n"); return 0;
}
"""
    r = subprocess.run(["g++", "-std=c++17", "-o", "/tmp/concept_test", "-xc++", "-"],
        input=code, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"C++ toolchain test compilation failed: {r.stderr}"
    r = subprocess.run(["/tmp/concept_test"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"C++ toolchain test execution failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_cpp_syntax_basic():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp"]
    for filepath in files:
        content = Path(filepath).read_text()
        assert content.count('{') == content.count('}'), f"{filepath} mismatched braces"
        assert content.count('(') == content.count(')'), f"{filepath} mismatched parentheses"


def test_repo_editorconfig():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        content = Path(filepath).read_text()
        for i, line in enumerate(content.split('\n')):
            assert line.rstrip() == line, f"{filepath}:{i+1} has trailing whitespace"
        if content and not content.endswith('\n'):
            assert False, f"{filepath} does not end with newline"


def test_repo_no_tabs():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        content = Path(filepath).read_bytes()
        assert b'\t' not in content, f"{filepath} contains tab characters"


def test_repo_no_banned_words():
    banned_patterns = [(r'\bTODO\s*:\s*hack\b', "TODO: hack"), (r'\bFIXME\s*:\s*hack\b', "FIXME: hack"),
                       (r'\bXXX\s*:\s*hack\b', "XXX: hack"), (r'\bHACK\s*:\s*', "HACK:")]
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        content = Path(filepath).read_text()
        for pattern, description in banned_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            assert not match, f"{filepath} contains banned pattern: {description}"


def test_repo_include_guards_webcore():
    headers = [f"{WEBCORE}/EventListenerMap.h", f"{WEBCORE}/BroadcastChannel.h"]
    for filepath in headers:
        if not Path(filepath).exists():
            continue
        content = Path(filepath).read_text()
        assert '#pragma once' in content or ('#ifndef' in content and '#define' in content), \
            f"{filepath} missing include guard"


def test_repo_license_headers():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        content = Path(filepath).read_text()
        has_license = ('Copyright' in content or 'copyright' in content.lower() or
                       'SPDX-License-Identifier' in content or 'GNU' in content or
                       'License' in content or 'MIT License' in content or
                       'BSD' in content or 'Apache' in content or
                       'Permission is hereby granted' in content.lower())
        assert has_license, f"{filepath} missing license/copyright notice"


def test_repo_no_merge_conflict_markers():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        content = Path(filepath).read_text()
        assert '<<<<<<<' not in content, f"{filepath} contains merge conflict marker"
        assert '=======' not in content, f"{filepath} contains merge conflict marker"
        assert '>>>>>>>' not in content, f"{filepath} contains merge conflict marker"


def test_repo_git_clean():
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 0, f"Git status check failed: {r.stderr}"


def test_repo_files_readable():
    r = subprocess.run(["ls", "-la",
        f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
        f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
        f"{WEBCORE}/EventListenerMap.h"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"File listing failed: {r.stderr}"
    lines = [l for l in r.stdout.strip().split('\n') if l.strip()]
    assert len(lines) == 5, f"Expected 5 files, found {len(lines)}"


def test_repo_cpp_weakptr_compiles():
    code = R"""
#include <memory>
#include <cstdio>
class TestObject : public std::enable_shared_from_this<TestObject> { public: int value = 42; };
int main() {
    std::shared_ptr<TestObject> shared = std::make_shared<TestObject>();
    std::weak_ptr<TestObject> weak = shared;
    auto locked = weak.lock();
    if (!locked) return 1;
    if (locked->value != 42) return 2;
    std::printf("PASS\n"); return 0;
}"""
    r = subprocess.run(["tee", "/tmp/weakptr_test.cpp"], input=code, capture_output=True, text=True, timeout=10)
    assert r.returncode == 0
    r = subprocess.run(["g++", "-std=c++17", "-o", "/tmp/weakptr_test", "/tmp/weakptr_test.cpp"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"weak_ptr pattern compilation failed: {r.stderr}"
    r = subprocess.run(["/tmp/weakptr_test"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"weak_ptr test execution failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_cpp_thread_patterns_compile():
    code = R"""
#include <mutex>
#include <thread>
#include <atomic>
#include <cstdio>
class ThreadSafeMap {
    mutable std::mutex m_lock;
    std::atomic<uint32_t> m_threadUID{0};
    int m_value = 0;
    void checkThread() {
        uint32_t current = m_threadUID.load();
        uint32_t tid = std::hash<std::thread::id>{}(std::this_thread::get_id()) & 0xFFFFFFFF;
        if (current == 0) { m_threadUID.store(tid); return; }
    }
public:
    void clear() { checkThread(); std::lock_guard<std::mutex> locker(m_lock); m_value = 0; }
    void add(int v) { checkThread(); std::lock_guard<std::mutex> locker(m_lock); m_value += v; }
    int get() const { std::lock_guard<std::mutex> locker(m_lock); return m_value; }
};
int main() {
    ThreadSafeMap map;
    map.add(5); map.add(3);
    if (map.get() != 8) return 1;
    map.clear();
    if (map.get() != 0) return 2;
    std::printf("PASS\n"); return 0;
}"""
    r = subprocess.run(["tee", "/tmp/thread_test.cpp"], input=code, capture_output=True, text=True, timeout=10)
    assert r.returncode == 0
    r = subprocess.run(["g++", "-std=c++17", "-o", "/tmp/thread_test", "/tmp/thread_test.cpp"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"thread pattern compilation failed: {r.stderr}"
    r = subprocess.run(["/tmp/thread_test"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"thread test execution failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_git_log():
    r = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    lines = [l for l in r.stdout.strip().split('\n') if l.strip()]
    assert len(lines) >= 1, "Git log should show at least 1 commit"


def test_repo_cpp_includes_exist():
    headers = [f"{REPO}/src/bun.js/bindings/webcore/config.h",
               f"{REPO}/src/bun.js/bindings/webcore/BroadcastChannel.h",
               f"{REPO}/src/bun.js/bindings/webcore/EventListenerMap.h",
               f"{REPO}/src/bun.js/bindings/webcore/MessagePortChannel.h",
               f"{REPO}/src/bun.js/bindings/webcore/JSAbortController.h"]
    for header in headers:
        r = subprocess.run(["test", "-f", header], capture_output=True, text=True, timeout=5)
        assert r.returncode == 0, f"Header file does not exist: {header}"


def test_repo_file_encoding():
    files = [f"{WEBCORE}/MessagePortChannel.cpp", f"{WEBCORE}/JSAbortController.cpp",
             f"{WEBCORE}/BroadcastChannel.cpp", f"{WEBCORE}/EventListenerMap.cpp",
             f"{WEBCORE}/EventListenerMap.h"]
    for filepath in files:
        r = subprocess.run(["python3", "-c", f"open('{filepath}', 'r', encoding='utf-8').read()"],
            capture_output=True, text=True, timeout=5)
        assert r.returncode == 0, f"File {filepath} is not valid UTF-8: {r.stderr}"


def test_repo_git_attributes():
    r = subprocess.run(["test", "-f", f"{REPO}/.gitattributes"], capture_output=True, text=True, timeout=5)
    assert r.returncode == 0, ".gitattributes file missing"
    r = subprocess.run(["git", "check-attr", "-a", "src/bun.js/bindings/webcore/BroadcastChannel.cpp"],
        capture_output=True, text=True, timeout=5, cwd=REPO)
    assert r.returncode == 0, f"git check-attr failed: {r.stderr}"


def test_repo_config_files_valid():
    configs = [f"{REPO}/test/internal/ban-limits.json", f"{REPO}/package.json"]
    for config in configs:
        r = subprocess.run(["python3", "-c", f"import json; json.load(open('{config}'))"],
            capture_output=True, text=True, timeout=5)
        assert r.returncode == 0, f"JSON config {config} is invalid: {r.stderr}"


def test_repo_shell_scripts_valid():
    scripts = [f"{REPO}/scripts/check-node.sh", f"{REPO}/scripts/check-node-all.sh"]
    for script in scripts:
        r = subprocess.run(["bash", "-n", script], capture_output=True, text=True, timeout=5)
        assert r.returncode == 0, f"Shell script {script} has syntax errors: {r.stderr}"


def test_repo_cpp_preprocessor():
    r = subprocess.run(["g++", "-E", "-xc++", "-"],
        input="#define TEST 1\n#ifdef TEST\nint x;\n#endif",
        capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"C++ preprocessor failed: {r.stderr}"
    assert "int x" in r.stdout


def test_repo_git_fsck():
    r = subprocess.run(["git", "fsck", "--full", "--cache"],
        capture_output=True, text=True, timeout=30, cwd=REPO)
    combined = r.stdout + r.stderr
    assert "error:" not in combined.lower() or "dangling" in combined.lower(), \
        f"Git repository has errors: {combined[:500]}"


def test_repo_claude_md_exists():
    r = subprocess.run(["test", "-f", f"{REPO}/CLAUDE.md"], capture_output=True, text=True, timeout=5)
    assert r.returncode == 0, "CLAUDE.md is missing"
    r = subprocess.run(["test", "-s", f"{REPO}/CLAUDE.md"], capture_output=True, text=True, timeout=5)
    assert r.returncode == 0, "CLAUDE.md is empty"
    r = subprocess.run(["head", "-5", f"{REPO}/CLAUDE.md"], capture_output=True, text=True, timeout=5)
    assert r.returncode == 0, f"CLAUDE.md is not readable: {r.stderr}"
    assert "Bun" in r.stdout or "bun" in r.stdout.lower(), "CLAUDE.md doesn't mention Bun"
