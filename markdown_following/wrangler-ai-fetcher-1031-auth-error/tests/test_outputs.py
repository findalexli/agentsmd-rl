"""Behavioral tests for cloudflare/workers-sdk PR #13160.

The PR adds a 403 auth-error handler to wrangler's AI fetcher: when the proxy
returns 403 with `errors[].code == 1031`, wrangler must log a specific message
suggesting `wrangler login`. We verify this by running the wrangler vitest
suite against an injected test file that exercises the new behavior, plus the
two existing AI-fetcher tests as pass-to-pass.
"""

import json
import os
import pathlib
import subprocess

import pytest

REPO = pathlib.Path("/workspace/workers-sdk")
WRANGLER = REPO / "packages/wrangler"
TEST_FILE = WRANGLER / "src/__tests__/ai.local.test.ts"
VITEST_JSON = pathlib.Path("/tmp/vitest-ai.json")

PATCHED_TEST_TS = r'''import { COMPLIANCE_REGION_CONFIG_UNKNOWN } from "@cloudflare/workers-utils";
import { Request } from "miniflare";
import { Headers, Response } from "undici";
import { afterEach, describe, it, vi } from "vitest";
import { getAIFetcher } from "../ai/fetcher";
import * as internal from "../cfetch/internal";
import { logger } from "../logger";
import * as user from "../user";

const AIFetcher = getAIFetcher(COMPLIANCE_REGION_CONFIG_UNKNOWN);

describe("ai", () => {
	describe("fetcher", () => {
		afterEach(() => {
			vi.restoreAllMocks();
		});

		describe("local", () => {
			it("should send x-forwarded header", async ({ expect }) => {
				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
				vi.spyOn(internal, "performApiFetch").mockImplementation(
					async (config, resource, init = {}) => {
						const headers = new Headers(init.headers);
						return Response.json({
							xForwarded: headers.get("X-Forwarded"),
							method: init.method,
						});
					}
				);

				const url = "http://internal.ai/ai/test/path?version=123";
				const resp = await AIFetcher(
					new Request(url, {
						method: "PATCH",
						headers: {
							"x-example": "test",
						},
					})
				);

				expect(await resp.json()).toEqual({
					xForwarded: url,
					method: "PATCH",
				});
			});

			it("account id should be set", async ({ expect }) => {
				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
				vi.spyOn(internal, "performApiFetch").mockImplementation(
					async (config, resource) => {
						return Response.json({
							resource: resource,
						});
					}
				);

				const url = "http://internal.ai/ai/test/path?version=123";
				const resp = await AIFetcher(
					new Request(url, {
						method: "PATCH",
						headers: {
							"x-example": "test",
						},
					})
				);

				expect(await resp.json()).toEqual({
					resource: "/accounts/123/ai/run/proxy",
				});
			});
		});

		describe("403 auth error handling", () => {
			it("should log error on 403 with auth error code 1031", async ({
				expect,
			}) => {
				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
					return new Response(
						JSON.stringify({
							errors: [{ code: 1031, message: "Forbidden" }],
						}),
						{ status: 403 }
					);
				});
				const errorSpy = vi.spyOn(logger, "error");

				const resp = await AIFetcher(
					new Request("http://internal.ai/ai/test/path", { method: "POST" })
				);

				expect(resp.status).toBe(403);
				expect(errorSpy).toHaveBeenCalledWith(
					"Authentication error (code 1031): Your API token may have expired or lacks the required permissions. Please refresh your token by running `wrangler login`."
				);
			});

			it("should not log error on 403 without auth error code 1031", async ({
				expect,
			}) => {
				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
					return new Response(
						JSON.stringify({
							errors: [{ code: 9999, message: "Other error" }],
						}),
						{ status: 403 }
					);
				});
				const errorSpy = vi.spyOn(logger, "error");

				const resp = await AIFetcher(
					new Request("http://internal.ai/ai/test/path", { method: "POST" })
				);

				expect(resp.status).toBe(403);
				expect(errorSpy).not.toHaveBeenCalled();
			});

			it("should not throw on 403 with unparseable body", async ({
				expect,
			}) => {
				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
					return new Response("not json", { status: 403 });
				});
				const errorSpy = vi.spyOn(logger, "error");

				const resp = await AIFetcher(
					new Request("http://internal.ai/ai/test/path", { method: "POST" })
				);

				expect(resp.status).toBe(403);
				expect(errorSpy).not.toHaveBeenCalled();
			});

			it("should log error when 1031 code appears alongside other error codes", async ({
				expect,
			}) => {
				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
					return new Response(
						JSON.stringify({
							errors: [
								{ code: 9999, message: "Other" },
								{ code: 1031, message: "Forbidden" },
							],
						}),
						{ status: 403 }
					);
				});
				const errorSpy = vi.spyOn(logger, "error");

				const resp = await AIFetcher(
					new Request("http://internal.ai/ai/test/path", { method: "POST" })
				);

				expect(resp.status).toBe(403);
				expect(errorSpy).toHaveBeenCalledWith(
					"Authentication error (code 1031): Your API token may have expired or lacks the required permissions. Please refresh your token by running `wrangler login`."
				);
			});

			it("should preserve the response body when handling 403 with code 1031", async ({
				expect,
			}) => {
				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
					return new Response(
						JSON.stringify({
							errors: [{ code: 1031, message: "Forbidden" }],
						}),
						{ status: 403 }
					);
				});
				vi.spyOn(logger, "error").mockImplementation(() => {});

				const resp = await AIFetcher(
					new Request("http://internal.ai/ai/test/path", { method: "POST" })
				);

				expect(resp.status).toBe(403);
				const parsed = (await resp.json()) as {
					errors?: Array<{ code?: number }>;
				};
				expect(parsed.errors?.[0]?.code).toBe(1031);
			});
		});
	});
});
'''


def _install_patched_test_file() -> None:
    TEST_FILE.write_text(PATCHED_TEST_TS)


@pytest.fixture(scope="session")
def vitest_results():
    _install_patched_test_file()

    if VITEST_JSON.exists():
        VITEST_JSON.unlink()

    env = os.environ.copy()
    env["NODE_OPTIONS"] = ""
    env["LC_ALL"] = "C"
    env["TZ"] = "UTC"

    cmd = [
        "pnpm",
        "exec",
        "vitest",
        "run",
        "src/__tests__/ai.local.test.ts",
        "--reporter=json",
        f"--outputFile={VITEST_JSON}",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(WRANGLER),
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )

    if not VITEST_JSON.exists():
        pytest.fail(
            "vitest did not produce a JSON report.\n"
            f"exit={proc.returncode}\n"
            f"stdout (last 2000 chars):\n{proc.stdout[-2000:]}\n"
            f"stderr (last 2000 chars):\n{proc.stderr[-2000:]}\n"
        )

    data = json.loads(VITEST_JSON.read_text())
    return {
        "data": data,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


def _find_assertion(results, full_name_substring: str):
    for tr in results["data"].get("testResults", []):
        for a in tr.get("assertionResults", []):
            full = a.get("fullName") or " > ".join(
                a.get("ancestorTitles", []) + [a.get("title", "")]
            )
            if full_name_substring in full:
                return a
    return None


def _assert_passed(results, name: str) -> None:
    a = _find_assertion(results, name)
    if a is None:
        names = []
        for tr in results["data"].get("testResults", []):
            for x in tr.get("assertionResults", []):
                names.append(x.get("fullName") or x.get("title"))
        pytest.fail(
            f"vitest did not report a test matching {name!r}.\n"
            f"available tests: {names}\n"
            f"vitest stdout (last 3000):\n{results['stdout'][-3000:]}\n"
            f"vitest stderr (last 1500):\n{results['stderr'][-1500:]}"
        )
    if a.get("status") != "passed":
        msg = "\n".join(a.get("failureMessages", []))[-3000:]
        pytest.fail(
            f"test {name!r} did not pass: status={a.get('status')!r}\n"
            f"failureMessages:\n{msg}\n"
            f"vitest stderr tail:\n{results['stderr'][-1500:]}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass tests — these only pass once the agent has implemented the
# 403 + code 1031 → logger.error("Authentication error...") behavior.
# ---------------------------------------------------------------------------


def test_403_with_code_1031_logs_authentication_error(vitest_results):
    _assert_passed(
        vitest_results,
        "should log error on 403 with auth error code 1031",
    )


def test_403_with_code_1031_alongside_other_codes(vitest_results):
    _assert_passed(
        vitest_results,
        "should log error when 1031 code appears alongside other error codes",
    )


# ---------------------------------------------------------------------------
# Pass-to-pass tests — confirm existing behavior is preserved and that the
# new code paths don't fire spuriously.
# ---------------------------------------------------------------------------


def test_403_with_code_1031_preserves_response_body(vitest_results):
    _assert_passed(
        vitest_results,
        "should preserve the response body when handling 403 with code 1031",
    )


def test_existing_x_forwarded_header_still_sent(vitest_results):
    _assert_passed(vitest_results, "should send x-forwarded header")


def test_existing_account_id_still_set(vitest_results):
    _assert_passed(vitest_results, "account id should be set")


def test_403_without_code_1031_does_not_log(vitest_results):
    _assert_passed(
        vitest_results,
        "should not log error on 403 without auth error code 1031",
    )


def test_403_with_unparseable_body_does_not_throw(vitest_results):
    _assert_passed(
        vitest_results,
        "should not throw on 403 with unparseable body",
    )


# ---------------------------------------------------------------------------
# Repository CI/CD pass-to-pass: TypeScript typecheck of the wrangler
# package. The repo's check:type runs `tsc -p ./tsconfig.json` (no emit) and
# is part of the standard `pnpm check`. Catches `any` / non-null assertion
# / floating-promise violations introduced by an under-disciplined fix.
# ---------------------------------------------------------------------------


def test_wrangler_typecheck(vitest_results):
    """Run wrangler's TypeScript typecheck on the patched source.

    Depends on vitest_results so the patched test file is in place when this
    runs (it imports from "../logger" via the new code path). Passes on the
    base commit and must continue to pass after the fix.
    """
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-p", "./tsconfig.json", "--noEmit"],
        cwd=str(WRANGLER),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"tsc failed (exit {r.returncode}):\n"
        f"stdout tail:\n{r.stdout[-3000:]}\n"
        f"stderr tail:\n{r.stderr[-1500:]}"
    )
