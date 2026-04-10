#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

# Write the complete correct provider-models.ts
cat > extensions/google/provider-models.ts << 'MODELEOF'
import type {
  ProviderResolveDynamicModelContext,
  ProviderRuntimeModel,
} from "openclaw/plugin-sdk/plugin-entry";
import { cloneFirstTemplateModel } from "openclaw/plugin-sdk/provider-model-shared";

const GEMINI_3_1_PRO_PREFIX = "gemini-3.1-pro";
const GEMINI_3_1_FLASH_LITE_PREFIX = "gemini-3.1-flash-lite";
const GEMINI_3_1_FLASH_PREFIX = "gemini-3.1-flash";
const GEMINI_3_1_PRO_TEMPLATE_IDS = ["gemini-3-pro-preview"] as const;
const GEMINI_3_1_FLASH_LITE_TEMPLATE_IDS = [
  "gemini-3.1-flash-lite-preview",
] as const;
const GEMINI_3_1_FLASH_TEMPLATE_IDS = ["gemini-3-flash-preview"] as const;

function cloneFirstGoogleTemplateModel(params: {
  providerId: string;
  templateProviderId?: string;
  modelId: string;
  templateIds: readonly string[];
  ctx: ProviderResolveDynamicModelContext;
  patch?: Partial<ProviderRuntimeModel>;
}): ProviderRuntimeModel | undefined {
  const templateProviderIds = [params.providerId, params.templateProviderId]
    .map((providerId) => providerId?.trim())
    .filter((providerId): providerId is string => Boolean(providerId));

  for (const templateProviderId of new Set(templateProviderIds)) {
    const model = cloneFirstTemplateModel({
      providerId: templateProviderId,
      modelId: params.modelId,
      templateIds: params.templateIds,
      ctx: params.ctx,
      patch: {
        ...params.patch,
        provider: params.providerId,
      },
    });
    if (model) {
      return model;
    }
  }

  return undefined;
}

export function resolveGoogle31ForwardCompatModel(params: {
  providerId: string;
  templateProviderId?: string;
  ctx: ProviderResolveDynamicModelContext;
}): ProviderRuntimeModel | undefined {
  const trimmed = params.ctx.modelId.trim();
  const lower = trimmed.toLowerCase();

  let templateIds: readonly string[];
  if (lower.startsWith(GEMINI_3_1_PRO_PREFIX)) {
    templateIds = GEMINI_3_1_PRO_TEMPLATE_IDS;
  } else if (lower.startsWith(GEMINI_3_1_FLASH_LITE_PREFIX)) {
    templateIds = GEMINI_3_1_FLASH_LITE_TEMPLATE_IDS;
  } else if (lower.startsWith(GEMINI_3_1_FLASH_PREFIX)) {
    templateIds = GEMINI_3_1_FLASH_TEMPLATE_IDS;
  } else {
    return undefined;
  }

  return cloneFirstGoogleTemplateModel({
    providerId: params.providerId,
    templateProviderId: params.templateProviderId,
    modelId: trimmed,
    templateIds,
    ctx: params.ctx,
    patch: { reasoning: true },
  });
}

export function isModernGoogleModel(modelId: string): boolean {
  return modelId.trim().toLowerCase().startsWith("gemini-3");
}
MODELEOF

# Format the provider-models.ts file
npx oxfmt --write extensions/google/provider-models.ts

# Fix index.ts: use ctx.provider instead of hardcoded "google"
sed -i 's/resolveGoogle31ForwardCompatModel({ providerId: "google", ctx })/resolveGoogle31ForwardCompatModel({\n          providerId: ctx.provider,\n          templateProviderId: GOOGLE_GEMINI_CLI_PROVIDER_ID,\n          ctx,\n        })/' extensions/google/index.ts

# Create the test file for provider-models
cat > extensions/google/provider-models.test.ts << 'TESTEOF'
import { describe, expect, it, vi } from "vitest";
import {
  resolveGoogle31ForwardCompatModel,
  isModernGoogleModel,
} from "./provider-models.js";
import type {
  ProviderResolveDynamicModelContext,
  ProviderRuntimeModel,
} from "openclaw/plugin-sdk/plugin-entry";

describe("google provider-models", () => {
  const createMockCtx = (modelId: string, findMock?: (providerId: string, modelId: string) => ProviderRuntimeModel | undefined): ProviderResolveDynamicModelContext => {
    const mockFind = findMock || vi.fn(() => undefined);
    return {
      modelId,
      provider: "google-gemini-cli",
      config: {},
      modelRegistry: {
        find: mockFind,
      },
    } as unknown as ProviderResolveDynamicModelContext;
  };

  describe("resolveGoogle31ForwardCompatModel", () => {
    it("resolves gemini 3.1 pro for alias provider via cross-provider lookup", () => {
      const mockFind = vi.fn((providerId: string, modelId: string) => {
        if (providerId === "google" && modelId === "gemini-3-pro-preview") {
          return {
            id: "gemini-3.1-pro-preview",
            provider: "google",
            name: "Gemini 3 Pro Preview",
          } as ProviderRuntimeModel;
        }
        return undefined;
      });

      const ctx = createMockCtx("gemini-3.1-pro-preview", mockFind);

      const result = resolveGoogle31ForwardCompatModel({
        providerId: "google-gemini-cli",
        templateProviderId: "google",
        ctx,
      });

      expect(result).toBeDefined();
      expect(result?.id).toBe("gemini-3.1-pro-preview");
      expect(mockFind).toHaveBeenCalledWith("google-gemini-cli", "gemini-3-pro-preview");
      expect(mockFind).toHaveBeenCalledWith("google", "gemini-3-pro-preview");
    });

    it("resolves gemini 3.1 flash from direct google templates", () => {
      const mockFind = vi.fn((providerId: string, modelId: string) => {
        if (providerId === "google" && modelId === "gemini-3-flash-preview") {
          return {
            id: "gemini-3.1-flash-preview",
            provider: "google",
            name: "Gemini 3 Flash Preview",
          } as ProviderRuntimeModel;
        }
        return undefined;
      });

      const ctx = createMockCtx("gemini-3.1-flash-preview", mockFind);

      const result = resolveGoogle31ForwardCompatModel({
        providerId: "google",
        ctx,
      });

      expect(result).toBeDefined();
      expect(result?.id).toBe("gemini-3.1-flash-preview");
      expect(mockFind).toHaveBeenCalledWith("google", "gemini-3-flash-preview");
    });

    it("flash-lite models resolve to their own template, not the broader flash prefix", () => {
      const mockFind = vi.fn((providerId: string, modelId: string) => {
        if (providerId === "google" && modelId === "gemini-3.1-flash-lite-preview") {
          return {
            id: "gemini-3.1-flash-lite-preview-001",
            provider: "google",
            name: "Gemini 3.1 Flash Lite Preview 001",
          } as ProviderRuntimeModel;
        }
        return undefined;
      });

      const ctx = createMockCtx("gemini-3.1-flash-lite-preview-001", mockFind);

      const result = resolveGoogle31ForwardCompatModel({
        providerId: "google",
        ctx,
      });

      expect(result).toBeDefined();
      expect(result?.id).toBe("gemini-3.1-flash-lite-preview-001");
      expect(mockFind).toHaveBeenCalledWith("google", "gemini-3.1-flash-lite-preview");
      const flashTemplateCalls = mockFind.mock.calls.filter(
        ([, modelId]) => modelId === "gemini-3-flash-preview"
      );
      expect(flashTemplateCalls.length).toBe(0);
    });

    it("returns undefined for non-matching model IDs", () => {
      const ctx = createMockCtx("some-other-model");

      const result = resolveGoogle31ForwardCompatModel({
        providerId: "google",
        ctx,
      });

      expect(result).toBeUndefined();
    });
  });

  describe("isModernGoogleModel", () => {
    it("returns true for gemini-3 models", () => {
      expect(isModernGoogleModel("gemini-3.1-pro")).toBe(true);
      expect(isModernGoogleModel("gemini-3.1-flash")).toBe(true);
      expect(isModernGoogleModel("gemini-3.5-pro")).toBe(true);
    });

    it("returns false for older gemini models", () => {
      expect(isModernGoogleModel("gemini-1.5-pro")).toBe(false);
      expect(isModernGoogleModel("gemini-1.0-pro")).toBe(false);
      expect(isModernGoogleModel("gemini-pro")).toBe(false);
    });
  });
});
TESTEOF

# Format the test file too
npx oxfmt --write extensions/google/provider-models.test.ts

echo "Solve applied successfully"
