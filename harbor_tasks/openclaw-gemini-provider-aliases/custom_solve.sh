#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

# First run the original solve.sh
bash /solution/solve.sh

# Fix formatting
npx oxfmt --write extensions/google/provider-models.ts

# Create the test file for provider-models
cat > extensions/google/provider-models.test.ts << 'TESTFILE'
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
        // First call with google-gemini-cli fails, second with google succeeds
        // Template lookup uses "gemini-3-pro-preview"
        if (providerId === "google" && modelId === "gemini-3-pro-preview") {
          return {
            id: "gemini-3.1-pro-preview",  // Returned model has input modelId
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
      // The result ID is the input modelId, not the template ID
      expect(result?.id).toBe("gemini-3.1-pro-preview");
      // Cross-provider lookup: first tries the alias provider, then the template provider
      expect(mockFind).toHaveBeenCalledWith("google-gemini-cli", "gemini-3-pro-preview");
      expect(mockFind).toHaveBeenCalledWith("google", "gemini-3-pro-preview");
    });

    it("resolves gemini 3.1 flash from direct google templates", () => {
      const mockFind = vi.fn((providerId: string, modelId: string) => {
        // Template lookup uses "gemini-3-flash-preview"
        if (providerId === "google" && modelId === "gemini-3-flash-preview") {
          return {
            id: "gemini-3.1-flash-preview",  // Returned model has input modelId
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
        // flash-lite uses GEMINI_3_1_FLASH_LITE_TEMPLATE_IDS = ["gemini-3.1-flash-lite-preview"]
        // NOT "gemini-3-flash-preview" (flash template)
        if (providerId === "google" && modelId === "gemini-3.1-flash-lite-preview") {
          return {
            id: "gemini-3.1-flash-lite-preview-001",  // Returned model has input modelId
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
      // Should look for the flash-lite template ID
      expect(mockFind).toHaveBeenCalledWith("google", "gemini-3.1-flash-lite-preview");
      // Should NOT look for the flash template ID
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
TESTFILE

# Format the test file too
npx oxfmt --write extensions/google/provider-models.test.ts

echo "Custom fix applied successfully"
