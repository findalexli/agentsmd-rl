"""
test_outputs.py - Benchmark tests for continue#11889

Tests that the OpenAI adapter correctly maps max_tokens to max_completion_tokens
for DeepSeek reasoner models.
"""
import os
import subprocess
import textwrap
import shutil

import pytest

REPO = "/workspace/continue"
PACKAGE_DIR = os.path.join(REPO, "packages/openai-adapters")
TSX = os.path.join(PACKAGE_DIR, "node_modules", ".bin", "tsx")


def run_ts_test(script_content: str, timeout: int = 60) -> tuple[int, str, str]:
    """Write a TypeScript test script and run it with tsx. Returns (rc, stdout, stderr)."""
    script_path = os.path.join(PACKAGE_DIR, "_test_script.mjs")
    with open(script_path, "w") as f:
        f.write(script_content)
    try:
        result = subprocess.run(
            [TSX, script_path],
            cwd=PACKAGE_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


# ---------------------------------------------------------------------------
# F2P: max_completion_tokens mapping for DeepSeek apiBase
# ---------------------------------------------------------------------------

def test_deepseek_api_base_maps_max_tokens():
    """
    Fail-to-pass: when apiBase includes api.deepseek.com, max_tokens
    must be remapped to max_completion_tokens in the request body.
    """
    script = textwrap.dedent("""
        import { constructLlmApi } from "./src/index.js";

        async function run() {
            let capturedRequest = null;

            const mockFetch = async (url, options) => {
                capturedRequest = { url: url.toString(), options };
                return new Response(JSON.stringify({
                    id: "test-id",
                    object: "chat.completion",
                    created: 1234567890,
                    model: "deepseek-reasoner",
                    choices: [{ index: 0, message: { role: "assistant", content: "OK" }, finish_reason: "stop" }],
                    usage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 }
                }), {
                    headers: { "Content-Type": "application/json" }
                });
            };

            const api = constructLlmApi({
                provider: "openai",
                model: "deepseek-reasoner",
                apiKey: "test-key",
                apiBase: "https://api.deepseek.com/v1/"
            });

            api.openai.fetch = mockFetch;

            const ac = new AbortController();
            await api.chatCompletionNonStream({
                model: "deepseek-reasoner",
                messages: [{ role: "user", content: "hello" }],
                max_tokens: 1024
            }, ac.signal);

            const body = JSON.parse(capturedRequest.options.body);

            if (body.max_tokens !== undefined) {
                console.error("FAIL: max_tokens should be undefined but was:", body.max_tokens);
                process.exit(1);
            }
            if (body.max_completion_tokens !== 1024) {
                console.error("FAIL: max_completion_tokens should be 1024 but was:", body.max_completion_tokens);
                process.exit(2);
            }
            console.log("PASS");
        }

        run().catch(e => {
            console.error("Error:", e);
            process.exit(1);
        });
    """)
    rc, stdout, stderr = run_ts_test(script)
    assert rc == 0, f"DeepSeek apiBase mapping test failed:\nstdout: {stdout}\nstderr: {stderr[-500:]}"


# ---------------------------------------------------------------------------
# F2P: max_completion_tokens mapping for deepseek-reasoner model name
# ---------------------------------------------------------------------------

def test_deepseek_model_name_maps_max_tokens():
    """
    Fail-to-pass: when model name includes 'deepseek-reasoner', max_tokens
    must be remapped to max_completion_tokens even without DeepSeek apiBase.
    """
    script = textwrap.dedent("""
        import { constructLlmApi } from "./src/index.js";

        async function run() {
            let capturedRequest = null;

            const mockFetch = async (url, options) => {
                capturedRequest = { url: url.toString(), options };
                return new Response(JSON.stringify({
                    id: "test-id",
                    object: "chat.completion",
                    created: 1234567890,
                    model: "deepseek-reasoner",
                    choices: [{ index: 0, message: { role: "assistant", content: "OK" }, finish_reason: "stop" }],
                    usage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 }
                }), {
                    headers: { "Content-Type": "application/json" }
                });
            };

            // Use a custom base (not deepseek.com) so we test model-name detection
            const api = constructLlmApi({
                provider: "openai",
                model: "deepseek-reasoner",
                apiKey: "test-key",
                apiBase: "https://custom.example.com/v1/"
            });

            api.openai.fetch = mockFetch;

            const ac = new AbortController();
            await api.chatCompletionNonStream({
                model: "deepseek-reasoner",
                messages: [{ role: "user", content: "hello" }],
                max_tokens: 512
            }, ac.signal);

            const body = JSON.parse(capturedRequest.options.body);

            if (body.max_tokens !== undefined) {
                console.error("FAIL: max_tokens should be undefined but was:", body.max_tokens);
                process.exit(1);
            }
            if (body.max_completion_tokens !== 512) {
                console.error("FAIL: max_completion_tokens should be 512 but was:", body.max_completion_tokens);
                process.exit(2);
            }
            console.log("PASS");
        }

        run().catch(e => {
            console.error("Error:", e);
            process.exit(1);
        });
    """)
    rc, stdout, stderr = run_ts_test(script)
    assert rc == 0, f"DeepSeek model-name mapping test failed:\nstdout: {stdout}\nstderr: {stderr[-500:]}"


# ---------------------------------------------------------------------------
# F2P: no mapping when max_tokens is not set
# ---------------------------------------------------------------------------

def test_no_mapping_without_max_tokens():
    """
    Fail-to-pass: when max_tokens is NOT set, neither max_tokens nor
    max_completion_tokens should be in the body (no spurious params).
    """
    script = textwrap.dedent("""
        import { constructLlmApi } from "./src/index.js";

        async function run() {
            let capturedRequest = null;

            const mockFetch = async (url, options) => {
                capturedRequest = { url: url.toString(), options };
                return new Response(JSON.stringify({
                    id: "test-id",
                    object: "chat.completion",
                    created: 1234567890,
                    model: "deepseek-reasoner",
                    choices: [{ index: 0, message: { role: "assistant", content: "OK" }, finish_reason: "stop" }],
                    usage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 }
                }), {
                    headers: { "Content-Type": "application/json" }
                });
            };

            const api = constructLlmApi({
                provider: "openai",
                model: "deepseek-reasoner",
                apiKey: "test-key",
                apiBase: "https://api.deepseek.com/v1/"
            });

            api.openai.fetch = mockFetch;

            const ac = new AbortController();
            await api.chatCompletionNonStream({
                model: "deepseek-reasoner",
                messages: [{ role: "user", content: "hello" }]
                // NO max_tokens
            }, ac.signal);

            const body = JSON.parse(capturedRequest.options.body);

            if (body.max_tokens !== undefined) {
                console.error("FAIL: max_tokens should not be present but was:", body.max_tokens);
                process.exit(1);
            }
            if (body.max_completion_tokens !== undefined) {
                console.error("FAIL: max_completion_tokens should not be present but was:", body.max_completion_tokens);
                process.exit(2);
            }
            console.log("PASS");
        }

        run().catch(e => {
            console.error("Error:", e);
            process.exit(1);
        });
    """)
    rc, stdout, stderr = run_ts_test(script)
    assert rc == 0, f"No-mapping test failed:\nstdout: {stdout}\nstderr: {stderr[-500:]}"


# ---------------------------------------------------------------------------
# F2P: non-DeepSeek models are unaffected
# ---------------------------------------------------------------------------

def test_non_deepseek_model_unchanged():
    """
    Fail-to-pass: standard OpenAI models should keep max_tokens unchanged.
    """
    script = textwrap.dedent("""
        import { constructLlmApi } from "./src/index.js";

        async function run() {
            let capturedRequest = null;

            const mockFetch = async (url, options) => {
                capturedRequest = { url: url.toString(), options };
                return new Response(JSON.stringify({
                    id: "test-id",
                    object: "chat.completion",
                    created: 1234567890,
                    model: "gpt-4o",
                    choices: [{ index: 0, message: { role: "assistant", content: "OK" }, finish_reason: "stop" }],
                    usage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 }
                }), {
                    headers: { "Content-Type": "application/json" }
                });
            };

            const api = constructLlmApi({
                provider: "openai",
                model: "gpt-4o",
                apiKey: "test-key",
                apiBase: "https://api.openai.com/v1/"
            });

            api.openai.fetch = mockFetch;

            const ac = new AbortController();
            await api.chatCompletionNonStream({
                model: "gpt-4o",
                messages: [{ role: "user", content: "hello" }],
                max_tokens: 256
            }, ac.signal);

            const body = JSON.parse(capturedRequest.options.body);

            if (body.max_tokens !== 256) {
                console.error("FAIL: max_tokens should remain 256 for non-DeepSeek but was:", body.max_tokens);
                process.exit(1);
            }
            if (body.max_completion_tokens !== undefined) {
                console.error("FAIL: max_completion_tokens should not be present for non-DeepSeek but was:", body.max_completion_tokens);
                process.exit(2);
            }
            console.log("PASS");
        }

        run().catch(e => {
            console.error("Error:", e);
            process.exit(1);
        });
    """)
    rc, stdout, stderr = run_ts_test(script)
    assert rc == 0, f"Non-DeepSeek unchanged test failed:\nstdout: {stdout}\nstderr: {stderr[-500:]}"


# ---------------------------------------------------------------------------
# F2P: streaming also maps max_tokens correctly
# ---------------------------------------------------------------------------

def test_deepseek_streaming_maps_max_tokens():
    """
    Fail-to-pass: streaming chatCompletionStream also maps max_tokens.
    """
    script = textwrap.dedent("""
        import { constructLlmApi } from "./src/index.js";

        async function run() {
            let capturedRequest = null;

            const encoder = new TextEncoder();
            const stream = new ReadableStream({
                start(controller) {
                    controller.enqueue(encoder.encode(
                        `data: ${JSON.stringify({
                            id: "test-id",
                            object: "chat.completion.chunk",
                            created: 1234567890,
                            model: "deepseek-reasoner",
                            choices: [{ index: 0, delta: { content: "Hi" }, finish_reason: null }],
                        })}\\n\\n`
                    ));
                    controller.close();
                }
            });

            const mockFetch = async (url, options) => {
                capturedRequest = { url: url.toString(), options };
                return new Response(stream, { headers: { "Content-Type": "text/event-stream" } });
            };

            const api = constructLlmApi({
                provider: "openai",
                model: "deepseek-reasoner",
                apiKey: "test-key",
                apiBase: "https://api.deepseek.com/v1/"
            });

            api.openai.fetch = mockFetch;

            const ac = new AbortController();
            const gen = await api.chatCompletionStream({
                model: "deepseek-reasoner",
                messages: [{ role: "user", content: "hello" }],
                max_tokens: 2048
            }, ac.signal);

            // Consume the stream
            for await (const _ of gen) {}

            const body = JSON.parse(capturedRequest.options.body);

            if (body.max_tokens !== undefined) {
                console.error("FAIL: max_tokens should be undefined in streaming but was:", body.max_tokens);
                process.exit(1);
            }
            if (body.max_completion_tokens !== 2048) {
                console.error("FAIL: max_completion_tokens should be 2048 but was:", body.max_completion_tokens);
                process.exit(2);
            }
            console.log("PASS");
        }

        run().catch(e => {
            console.error("Error:", e);
            process.exit(1);
        });
    """)
    rc, stdout, stderr = run_ts_test(script)
    assert rc == 0, f"DeepSeek streaming mapping test failed:\nstdout: {stdout}\nstderr: {stderr[-500:]}"


# ---------------------------------------------------------------------------
# P2P: Repo CI tests — openai-adapters package
# ---------------------------------------------------------------------------


def test_repo_vitest_openai_adapters():
    """
    Pass-to-pass: repo's vitest suite for openai-adapters passes (pass_to_pass).
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=PACKAGE_DIR,
    )
    assert r.returncode == 0, f"vitest run failed:\n{r.stderr[-500:]}"


def test_repo_vitest_openai_adapter():
    """
    Pass-to-pass: repo's OpenAI adapter vitest tests pass (pass_to_pass).
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "src/test/openai-adapter.vitest.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PACKAGE_DIR,
    )
    assert r.returncode == 0, f"vitest openai-adapter test failed:\n{r.stderr[-500:]}"