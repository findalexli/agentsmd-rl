/* eslint-disable @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from "vitest";

import { InstanceType } from "@app/ee/services/license/license-types";

const mockGroupIdentify = vi.fn();
const mockCapture = vi.fn();
const mockShutdownAsync = vi.fn().mockResolvedValue(undefined);
const mockIdentify = vi.fn();

vi.mock("posthog-node", () => ({
  PostHog: vi.fn().mockImplementation(() => ({
    groupIdentify: mockGroupIdentify,
    capture: mockCapture,
    identify: mockIdentify,
    shutdownAsync: mockShutdownAsync
  }))
}));

vi.mock("@app/lib/config/env", () => ({
  getConfig: () => ({
    isProductionMode: false,
    TELEMETRY_ENABLED: true,
    POSTHOG_HOST: "https://test.posthog.example",
    POSTHOG_PROJECT_API_KEY: "test-key",
    LOOPS_API_KEY: undefined
  })
}));

vi.mock("@app/lib/logger", () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
    debug: vi.fn()
  }
}));

vi.mock("@app/lib/config/request", () => ({
  request: { post: vi.fn() }
}));

vi.mock("@fastify/request-context", () => ({
  requestContext: { get: vi.fn().mockReturnValue(undefined) }
}));

// Import AFTER vi.mock so mocks are applied
// eslint-disable-next-line import/first
import { telemetryServiceFactory } from "@app/services/telemetry/telemetry-service";

type MakeOpts = {
  instanceType?: InstanceType;
  findOrgById?: any;
  getPlan?: any;
};

const makeDeps = (opts: MakeOpts = {}) => {
  const keyStore: any = {
    incrementBy: vi.fn().mockResolvedValue(undefined),
    deleteItemsByKeyIn: vi.fn().mockResolvedValue(undefined),
    setItemWithExpiry: vi.fn().mockResolvedValue(undefined),
    getKeysByPattern: vi.fn().mockResolvedValue([]),
    getItems: vi.fn().mockResolvedValue([])
  };
  const licenseService: any = {
    getInstanceType: vi.fn().mockReturnValue(opts.instanceType ?? InstanceType.Cloud),
    getPlan:
      opts.getPlan ??
      vi.fn().mockResolvedValue({
        slug: "pro",
        membersUsed: 7
      })
  };
  const orgDAL: any = {
    findOrgById:
      opts.findOrgById ??
      vi.fn().mockResolvedValue({
        id: "org-1",
        name: "Acme",
        createdAt: new Date("2024-01-15T12:34:56.000Z")
      })
  };
  return { keyStore, licenseService, orgDAL };
};

const seedBucket = (
  deps: ReturnType<typeof makeDeps>,
  events: Array<{ distinctId: string; organizationId: string; organizationName?: string }>
) => {
  // Only return keys when the requested pattern targets bucket-00 so the
  // 30-bucket loop in processAggregatedEvents sees data exactly once.
  deps.keyStore.getKeysByPattern = vi.fn().mockImplementation((pattern: string) => {
    if (pattern.includes("bucket-00")) {
      return Promise.resolve(events.map((_, i) => `telemetry-event-secrets pulled-bucket-00-${i}-uuid`));
    }
    return Promise.resolve([]);
  });
  deps.keyStore.getItems = vi.fn().mockResolvedValue(
    events.map((e) =>
      JSON.stringify({
        distinctId: e.distinctId,
        event: "secrets pulled",
        properties: { numberOfSecrets: 1 },
        organizationId: e.organizationId,
        ...(e.organizationName ? { organizationName: e.organizationName } : {})
      })
    )
  );
};

describe("telemetryServiceFactory groupIdentify enrichment (PR #5653)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("processBucketEvents groupIdentify includes is_cloud, plan, seat_count, created_at, name", async () => {
    const deps = makeDeps({ instanceType: InstanceType.Cloud });
    seedBucket(deps, [{ distinctId: "user-1", organizationId: "org-1", organizationName: "Acme" }]);

    const svc = telemetryServiceFactory(deps as any);
    await svc.processAggregatedEvents();

    expect(mockGroupIdentify).toHaveBeenCalled();
    const call = mockGroupIdentify.mock.calls[0][0];
    expect(call.groupType).toBe("organization");
    expect(call.groupKey).toBe("org-1");
    expect(call.properties).toBeDefined();
    expect(call.properties.is_cloud).toBe(true);
    expect(call.properties.plan).toBe("pro");
    expect(call.properties.seat_count).toBe(7);
    expect(call.properties.created_at).toBe("2024-01-15T12:34:56.000Z");
    expect(call.properties.name).toBe("Acme");
  });

  it("self-hosted instance has is_cloud=false and plan defaults to 'free' when slug is null", async () => {
    const deps = makeDeps({ instanceType: InstanceType.OnPrem });
    deps.licenseService.getPlan = vi.fn().mockResolvedValue({ slug: null, membersUsed: 0 });
    deps.orgDAL.findOrgById = vi.fn().mockResolvedValue({
      id: "org-self-hosted",
      name: "Self-Hosted Co",
      createdAt: new Date("2023-06-01T00:00:00.000Z")
    });
    seedBucket(deps, [{ distinctId: "user-1", organizationId: "org-self-hosted" }]);

    const svc = telemetryServiceFactory(deps as any);
    await svc.processAggregatedEvents();

    const call = mockGroupIdentify.mock.calls[0][0];
    expect(call.properties.is_cloud).toBe(false);
    expect(call.properties.plan).toBe("free");
    expect(call.properties.seat_count).toBe(0);
    expect(call.properties.name).toBe("Self-Hosted Co");
    expect(call.properties.created_at).toBe("2023-06-01T00:00:00.000Z");
  });

  it("processBucketEvents caches per-orgId so findOrgById/getPlan called once per org", async () => {
    const deps = makeDeps({ instanceType: InstanceType.Cloud });
    seedBucket(deps, [
      { distinctId: "user-A", organizationId: "org-shared", organizationName: "Shared Co" },
      { distinctId: "user-B", organizationId: "org-shared", organizationName: "Shared Co" },
      { distinctId: "user-C", organizationId: "org-shared", organizationName: "Shared Co" }
    ]);

    const svc = telemetryServiceFactory(deps as any);
    await svc.processAggregatedEvents();

    expect(deps.orgDAL.findOrgById).toHaveBeenCalledTimes(1);
    expect(deps.licenseService.getPlan).toHaveBeenCalledTimes(1);
    // groupIdentify is still emitted per distinctId/org grouping
    expect(mockGroupIdentify.mock.calls.length).toBeGreaterThanOrEqual(3);
    // every call has the enriched properties
    for (const call of mockGroupIdentify.mock.calls) {
      const props = call[0].properties;
      expect(props.plan).toBe("pro");
      expect(props.seat_count).toBe(7);
      expect(props.is_cloud).toBe(true);
    }
  });

  it("sendPostHogEvents enriches groupIdentify (fire-and-forget) with full org properties", async () => {
    const deps = makeDeps({ instanceType: InstanceType.Cloud });
    const svc = telemetryServiceFactory(deps as any);

    // UserSignedUp triggers the non-aggregated path on cloud
    await svc.sendPostHogEvents({
      event: "User Signed Up",
      distinctId: "user-1",
      properties: {},
      organizationId: "org-1",
      organizationName: "Acme"
    } as any);

    // Wait for the fire-and-forget promise to resolve
    for (let i = 0; i < 20; i += 1) {
      // eslint-disable-next-line no-await-in-loop
      await new Promise((r) => setTimeout(r, 25));
      if (mockGroupIdentify.mock.calls.length > 0) break;
    }

    expect(mockGroupIdentify).toHaveBeenCalled();
    const call = mockGroupIdentify.mock.calls.at(-1)![0];
    expect(call.groupKey).toBe("org-1");
    expect(call.properties.is_cloud).toBe(true);
    expect(call.properties.plan).toBe("pro");
    expect(call.properties.seat_count).toBe(7);
    expect(call.properties.created_at).toBe("2024-01-15T12:34:56.000Z");
    expect(call.properties.name).toBe("Acme");
  });

  it("getOrgGroupProperties handles findOrgById failure gracefully — still emits is_cloud and plan", async () => {
    const deps = makeDeps({ instanceType: InstanceType.Cloud });
    deps.orgDAL.findOrgById = vi.fn().mockRejectedValue(new Error("DB down"));
    seedBucket(deps, [{ distinctId: "user-1", organizationId: "org-1", organizationName: "Acme" }]);

    const svc = telemetryServiceFactory(deps as any);
    await svc.processAggregatedEvents();

    expect(mockGroupIdentify).toHaveBeenCalled();
    const call = mockGroupIdentify.mock.calls[0][0];
    expect(call.properties.is_cloud).toBe(true);
    // plan still resolved
    expect(call.properties.plan).toBe("pro");
    // org name from event still present (since orgName passed to fn)
    expect(call.properties.name).toBe("Acme");
    // created_at absent because findOrgById failed
    expect(call.properties.created_at).toBeUndefined();
  });
});
