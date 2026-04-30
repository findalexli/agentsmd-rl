"""Behavioral tests for opencode PR #23093.

We extract the body of the `assistantMessages` createMemo from
`packages/ui/src/components/session-turn.tsx` and execute it under Node
with controlled inputs. The bug surfaces when the user message's ID does
not sort first within its turn (clock skew between client and server),
so an assistant whose `parentID` matches the user appears at an array
index *before* the user. The pre-fix code scans only `index+1..end` and
breaks at the next `user`, so it loses that assistant.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
TARGET = REPO / "packages/ui/src/components/session-turn.tsx"


def _extract_body() -> str:
    src = TARGET.read_text()
    m = re.search(
        r"const\s+assistantMessages\s*=\s*createMemo\(\s*\(\)\s*=>\s*\{([\s\S]*?)\n\s*\},\s*emptyAssistant",
        src,
    )
    assert m is not None, "Could not locate the assistantMessages createMemo body"
    body = m.group(1)
    body = re.sub(r":\s*AssistantMessage\[\]", "", body)
    body = re.sub(r"\s+as\s+AssistantMessage", "", body)
    return body


def _run(messages, msg, index):
    body = _extract_body()
    script = f"""
const __INPUT_MSG__ = {json.dumps(msg)};
const __INPUT_MESSAGES__ = {json.dumps(messages)};
const __INPUT_INDEX__ = {json.dumps(index)};
const fn = () => {{
  const message = () => __INPUT_MSG__;
  const allMessages = () => __INPUT_MESSAGES__;
  const messageIndex = () => __INPUT_INDEX__;
  const emptyAssistant = [];
  const emptyMessages = [];
  {body}
}};
const out = fn();
process.stdout.write(JSON.stringify(out.map(m => m.id)));
"""
    node = shutil.which("node")
    assert node, "node binary missing from PATH"
    r = subprocess.run(
        [node, "-e", script], capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"node exited {r.returncode}\nSTDERR:\n{r.stderr}"
    return json.loads(r.stdout)


def test_clock_skew_assistant_visible():
    """When client clock is ahead of server, an assistant message can land at
    an array index before its user (sorted by ID). The function must still
    return that assistant by matching parentID across the whole array."""
    user = {"id": "msg_user", "role": "user"}
    a1 = {"id": "msg_a1_skew_before", "role": "assistant", "parentID": "msg_user"}
    a2 = {"id": "msg_a2_after", "role": "assistant", "parentID": "msg_user"}
    a3 = {"id": "msg_a3_after", "role": "assistant", "parentID": "msg_user"}
    messages = [a1, user, a2, a3]
    ids = _run(messages, user, 1)
    assert ids == ["msg_a1_skew_before", "msg_a2_after", "msg_a3_after"], (
        f"Expected all three assistants for the user; got {ids}. The skewed assistant "
        "(at index 0, before the user at index 1) was likely dropped."
    )


def test_no_skew_normal_order():
    """Regression: the normal case (user first, assistants after) still works."""
    user = {"id": "msg_u", "role": "user"}
    a1 = {"id": "msg_a1", "role": "assistant", "parentID": "msg_u"}
    a2 = {"id": "msg_a2", "role": "assistant", "parentID": "msg_u"}
    messages = [user, a1, a2]
    ids = _run(messages, user, 0)
    assert ids == ["msg_a1", "msg_a2"], ids


def test_assistants_filtered_by_parentid():
    """Only assistants whose parentID matches the queried user must be returned,
    regardless of array order."""
    u1 = {"id": "msg_u1", "role": "user"}
    u2 = {"id": "msg_u2", "role": "user"}
    a_for_u1 = {"id": "msg_a_u1", "role": "assistant", "parentID": "msg_u1"}
    a_for_u2 = {"id": "msg_a_u2", "role": "assistant", "parentID": "msg_u2"}
    messages = [u1, a_for_u1, u2, a_for_u2]

    ids1 = _run(messages, u1, 0)
    assert ids1 == ["msg_a_u1"], f"For u1 expected only its assistant; got {ids1}"

    ids2 = _run(messages, u2, 2)
    assert ids2 == ["msg_a_u2"], f"For u2 expected only its assistant; got {ids2}"


def test_skewed_assistant_with_other_users_present():
    """A more realistic conversation: prior turn (u_prev with its assistant),
    then current turn where current user's clock-skewed assistant lands BEFORE
    the current user in the sorted array, then more assistants for current
    user. The fix must include the skewed assistant and exclude assistants
    belonging to the prior turn."""
    u_prev = {"id": "msg_u_prev", "role": "user"}
    a_prev = {"id": "msg_a_prev", "role": "assistant", "parentID": "msg_u_prev"}
    a_curr_skew = {
        "id": "msg_a_curr_skew",
        "role": "assistant",
        "parentID": "msg_u_curr",
    }
    u_curr = {"id": "msg_u_curr", "role": "user"}
    a_curr_after = {
        "id": "msg_a_curr_after",
        "role": "assistant",
        "parentID": "msg_u_curr",
    }
    messages = [u_prev, a_prev, a_curr_skew, u_curr, a_curr_after]
    ids = _run(messages, u_curr, 3)
    assert ids == ["msg_a_curr_skew", "msg_a_curr_after"], ids


def test_no_user_break_short_circuit():
    """Even though the immediate next message after the queried user is a
    different user, the function must still scan for the queried user's
    assistants elsewhere in the array (the pre-fix code break-on-user
    short-circuits and misses them)."""
    u1 = {"id": "msg_u1", "role": "user"}
    u2 = {"id": "msg_u2", "role": "user"}
    a_for_u1_late = {
        "id": "msg_a_u1_late",
        "role": "assistant",
        "parentID": "msg_u1",
    }
    messages = [u1, u2, a_for_u1_late]
    ids = _run(messages, u1, 0)
    assert ids == ["msg_a_u1_late"], (
        f"Expected u1's late assistant to be included; got {ids}. "
        "Pre-fix code breaks at the next 'user' role and misses it."
    )


def test_negative_index_returns_empty():
    """When messageIndex() < 0, the memo should return an empty array."""
    user = {"id": "msg_u", "role": "user"}
    a1 = {"id": "msg_a", "role": "assistant", "parentID": "msg_u"}
    messages = [user, a1]
    ids = _run(messages, user, -1)
    assert ids == [], ids

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_storybook_build_build_storybook():
    """pass_to_pass | CI job 'storybook build' → step 'Build Storybook'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/storybook build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Storybook' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_prepare():
    """pass_to_pass | CI job 'build-electron' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")