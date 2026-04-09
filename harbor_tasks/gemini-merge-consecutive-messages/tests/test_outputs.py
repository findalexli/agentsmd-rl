"""Tests for Gemini consecutive message merging fix.

This test suite verifies that the Gemini API integration correctly merges
consecutive messages with the same role to comply with Gemini's strict
role alternation requirement.
"""

import subprocess
import sys
import json
import os

REPO = "/workspace/continue"


def run_typescript_test(test_code: str, cwd: str = None) -> tuple[int, str, str]:
    """Run TypeScript test code using tsx or node."""
    if cwd is None:
        cwd = REPO

    # Write test code to a temporary file
    test_file = "/tmp/test_gemini.ts"
    with open(test_file, "w") as f:
        f.write(test_code)

    # Try using npx tsx first, fall back to npx ts-node
    for runner in ["tsx", "ts-node"]:
        try:
            result = subprocess.run(
                ["npx", runner, test_file],
                cwd=cwd,
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0 or runner == "ts-node":
                return result.returncode, result.stdout.decode(), result.stderr.decode()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return 1, "", f"Failed to run TypeScript test with both tsx and ts-node"


def test_merge_function_exists_in_openai_adapters():
    """Fail-to-pass: mergeConsecutiveGeminiMessages function must exist in openai-adapters."""
    test_code = '''
import { mergeConsecutiveGeminiMessages } from "/workspace/continue/packages/openai-adapters/src/util/gemini-types.js";

// Test basic merging
const messages = [
  { role: "user", parts: [{ text: "hello" }] },
  { role: "user", parts: [{ text: "world" }] },
];

const result = mergeConsecutiveGeminiMessages(messages);
if (result.length !== 1) {
  console.error(`Expected 1 message, got ${result.length}`);
  process.exit(1);
}
if (result[0].parts.length !== 2) {
  console.error(`Expected 2 parts, got ${result[0].parts.length}`);
  process.exit(1);
}
console.log("PASS: mergeConsecutiveGeminiMessages exists and works");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"mergeConsecutiveGeminiMessages function not working: {stderr}\n{stdout}"


def test_merge_function_exists_in_core():
    """Fail-to-pass: mergeConsecutiveGeminiMessages function must exist in core."""
    test_code = '''
import { mergeConsecutiveGeminiMessages } from "/workspace/continue/core/llm/llms/gemini-types.js";

// Test basic merging
const messages = [
  { role: "model", parts: [{ text: "first" }] },
  { role: "model", parts: [{ text: "second" }] },
];

const result = mergeConsecutiveGeminiMessages(messages);
if (result.length !== 1) {
  console.error(`Expected 1 message, got ${result.length}`);
  process.exit(1);
}
if (result[0].parts.length !== 2) {
  console.error(`Expected 2 parts, got ${result[0].parts.length}`);
  process.exit(1);
}
console.log("PASS: mergeConsecutiveGeminiMessages exists in core and works");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/core")
    assert returncode == 0, f"mergeConsecutiveGeminiMessages in core not working: {stderr}\n{stdout}"


def test_merge_consecutive_tool_responses():
    """Fail-to-pass: Multiple consecutive tool responses must be merged into single user turn."""
    test_code = '''
import { GeminiApi } from "/workspace/continue/packages/openai-adapters/src/apis/Gemini.js";

const api = new GeminiApi({ provider: "gemini", apiKey: "test" });

const result = api._convertBody(
  {
    model: "gemini-2.5-flash",
    messages: [
      { role: "user", content: "Use the tools" },
      {
        role: "assistant",
        content: null,
        tool_calls: [
          { id: "call_1", type: "function", function: { name: "tool_a", arguments: "{}" } },
          { id: "call_2", type: "function", function: { name: "tool_b", arguments: "{}" } },
        ],
      },
      { role: "tool", content: "result_a", tool_call_id: "call_1" },
      { role: "tool", content: "result_b", tool_call_id: "call_2" },
    ],
  },
  false,
  true,
);

// Should be: user, model(functionCalls), user(functionResponses merged) = 3 messages
if (result.contents.length !== 3) {
  console.error(`Expected 3 messages, got ${result.contents.length}`);
  process.exit(1);
}

// Last message (user) should have 2 parts (both function responses)
const lastMessage = result.contents[result.contents.length - 1];
if (lastMessage.role !== "user") {
  console.error(`Expected last role to be user, got ${lastMessage.role}`);
  process.exit(1);
}
if (lastMessage.parts.length !== 2) {
  console.error(`Expected 2 parts in merged message, got ${lastMessage.parts.length}`);
  process.exit(1);
}

console.log("PASS: Consecutive tool responses merged correctly");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"Consecutive tool responses not merged: {stderr}\n{stdout}"


def test_merge_tool_response_with_following_user_message():
    """Fail-to-pass: Tool response followed by user message must be merged."""
    test_code = '''
import { GeminiApi } from "/workspace/continue/packages/openai-adapters/src/apis/Gemini.js";

const api = new GeminiApi({ provider: "gemini", apiKey: "test" });

const result = api._convertBody(
  {
    model: "gemini-2.5-flash",
    messages: [
      { role: "user", content: "Use the tool" },
      {
        role: "assistant",
        content: null,
        tool_calls: [
          { id: "call_1", type: "function", function: { name: "tool_a", arguments: "{}" } },
        ],
      },
      { role: "tool", content: "result_a", tool_call_id: "call_1" },
      { role: "user", content: "Now do something else" },
    ],
  },
  false,
  true,
);

// tool response (maps to user) + user message should merge into single user message
// Total: user, model, merged-user = 3 messages
if (result.contents.length !== 3) {
  console.error(`Expected 3 messages, got ${result.contents.length}`);
  process.exit(1);
}

const lastMessage = result.contents[result.contents.length - 1];
if (lastMessage.role !== "user") {
  console.error(`Expected last role to be user, got ${lastMessage.role}`);
  process.exit(1);
}
if (lastMessage.parts.length !== 2) {
  console.error(`Expected 2 parts (functionResponse + text), got ${lastMessage.parts.length}`);
  process.exit(1);
}

console.log("PASS: Tool response merged with following user message");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"Tool response not merged with user message: {stderr}\n{stdout}"


def test_merge_consecutive_model_messages():
    """Fail-to-pass: Consecutive assistant messages must be merged into single model message."""
    test_code = '''
import { GeminiApi } from "/workspace/continue/packages/openai-adapters/src/apis/Gemini.js";

const api = new GeminiApi({ provider: "gemini", apiKey: "test" });

const result = api._convertBody(
  {
    model: "gemini-2.5-flash",
    messages: [
      { role: "user", content: "Hello" },
      { role: "assistant", content: "First response" },
      { role: "assistant", content: "Second response" },
    ],
  },
  false,
  true,
);

// Two assistant messages should merge into one model message
// Total: user, merged-model = 2 messages
if (result.contents.length !== 2) {
  console.error(`Expected 2 messages, got ${result.contents.length}`);
  process.exit(1);
}

const modelMessage = result.contents[1];
if (modelMessage.role !== "model") {
  console.error(`Expected model role, got ${modelMessage.role}`);
  process.exit(1);
}
if (modelMessage.parts.length !== 2) {
  console.error(`Expected 2 parts in merged model message, got ${modelMessage.parts.length}`);
  process.exit(1);
}

console.log("PASS: Consecutive model messages merged correctly");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"Consecutive model messages not merged: {stderr}\n{stdout}"


def test_preserves_already_alternating_messages():
    """Pass-to-pass: Already-alternating messages should remain unchanged."""
    test_code = '''
import { GeminiApi } from "/workspace/continue/packages/openai-adapters/src/apis/Gemini.js";

const api = new GeminiApi({ provider: "gemini", apiKey: "test" });

const result = api._convertBody(
  {
    model: "gemini-2.5-flash",
    messages: [
      { role: "user", content: "Hello" },
      { role: "assistant", content: "Hi there" },
      { role: "user", content: "How are you?" },
    ],
  },
  false,
  true,
);

// Already alternating, should stay as 3 messages
if (result.contents.length !== 3) {
  console.error(`Expected 3 messages for already-alternating, got ${result.contents.length}`);
  process.exit(1);
}

if (result.contents[0].role !== "user") {
  console.error(`Expected role user at index 0, got ${result.contents[0].role}`);
  process.exit(1);
}
if (result.contents[1].role !== "model") {
  console.error(`Expected role model at index 1, got ${result.contents[1].role}`);
  process.exit(1);
}
if (result.contents[2].role !== "user") {
  console.error(`Expected role user at index 2, got ${result.contents[2].role}`);
  process.exit(1);
}

console.log("PASS: Already alternating messages preserved");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"Already alternating messages not preserved: {stderr}\n{stdout}"


def test_merge_function_handles_empty_array():
    """Fail-to-pass: mergeConsecutiveGeminiMessages must handle empty array."""
    test_code = '''
import { mergeConsecutiveGeminiMessages } from "/workspace/continue/packages/openai-adapters/src/util/gemini-types.js";

const result = mergeConsecutiveGeminiMessages([]);
if (result.length !== 0) {
  console.error(`Expected empty array, got ${result.length} items`);
  process.exit(1);
}
console.log("PASS: Empty array handled correctly");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"Empty array not handled: {stderr}\n{stdout}"


def test_merge_function_handles_single_message():
    """Fail-to-pass: mergeConsecutiveGeminiMessages must handle single message."""
    test_code = '''
import { mergeConsecutiveGeminiMessages } from "/workspace/continue/packages/openai-adapters/src/util/gemini-types.js";

const messages = [{ role: "user", parts: [{ text: "hello" }] }];
const result = mergeConsecutiveGeminiMessages(messages);
if (result.length !== 1) {
  console.error(`Expected 1 message, got ${result.length}`);
  process.exit(1);
}
if (result[0].parts.length !== 1) {
  console.error(`Expected 1 part, got ${result[0].parts.length}`);
  process.exit(1);
}
console.log("PASS: Single message handled correctly");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"Single message not handled: {stderr}\n{stdout}"


def test_merge_function_three_consecutive_same_role():
    """Fail-to-pass: Must merge three consecutive same-role messages."""
    test_code = '''
import { mergeConsecutiveGeminiMessages } from "/workspace/continue/packages/openai-adapters/src/util/gemini-types.js";

const messages = [
  { role: "user", parts: [{ text: "a" }] },
  { role: "user", parts: [{ text: "b" }] },
  { role: "user", parts: [{ text: "c" }] },
];

const result = mergeConsecutiveGeminiMessages(messages);
if (result.length !== 1) {
  console.error(`Expected 1 message, got ${result.length}`);
  process.exit(1);
}
if (result[0].parts.length !== 3) {
  console.error(`Expected 3 parts, got ${result[0].parts.length}`);
  process.exit(1);
}
console.log("PASS: Three consecutive messages merged correctly");
'''
    returncode, stdout, stderr = run_typescript_test(test_code, cwd=f"{REPO}/packages/openai-adapters")
    assert returncode == 0, f"Three consecutive messages not merged: {stderr}\n{stdout}"


def test_repo_unit_tests_pass():
    """Pass-to-pass: The repository's own unit tests for openai-adapters must pass."""
    result = subprocess.run(
        ["npm", "test", "--", "--run"],
        cwd=f"{REPO}/packages/openai-adapters",
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Repository unit tests failed: {result.stderr.decode()[-500:]}"


def test_repo_typecheck_pass():
    """Pass-to-pass: TypeScript typecheck for openai-adapters must pass."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=f"{REPO}/packages/openai-adapters",
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript typecheck failed: {result.stderr.decode()[-500:]}"


def test_repo_build_pass():
    """Pass-to-pass: Build for openai-adapters must pass."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=f"{REPO}/packages/openai-adapters",
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Build failed: {result.stderr.decode()[-500:]}"
