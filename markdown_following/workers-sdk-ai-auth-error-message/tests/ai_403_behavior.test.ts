import { COMPLIANCE_REGION_CONFIG_UNKNOWN } from "@cloudflare/workers-utils";
import { Request } from "miniflare";
import { Headers, Response } from "undici";
import { describe, it, vi } from "vitest";
import { getAIFetcher } from "../ai/fetcher";
import * as internal from "../cfetch/internal";
import { logger } from "../logger";
import * as user from "../user";

const AIFetcher = getAIFetcher(COMPLIANCE_REGION_CONFIG_UNKNOWN);

describe("403 auth error handling (behavioral)", () => {
	it("should log error on 403 with auth error code 1031", async ({ expect }) => {
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
});
