#!/bin/bash
set -e

cd /workspace/oxc/apps/oxfmt

# Idempotency check - if the distinctive line exists, patch is already applied
if grep -q "import.meta.vitest" src-js/cli/js_config/node_version.ts 2>/dev/null; then
    echo "Patch already applied (found import.meta.vitest in node_version.ts)"
    exit 0
fi

# Create js_config directory if it doesn't exist
mkdir -p src-js/cli/js_config

# Create node_version.ts with inline tests
cat > src-js/cli/js_config/node_version.ts << 'PATCH'
import { extname as pathExtname } from "node:path";
import { fileURLToPath } from "node:url";

const NODE_TYPESCRIPT_SUPPORT_RANGE = "^20.19.0 || >=22.12.0";
const TS_MODULE_EXTENSIONS = new Set([".ts", ".mts", ".cts"]);

export function getUnsupportedTypeScriptModuleLoadHint(
  err: unknown,
  specifier: string,
  nodeVersion: string = process.version,
): string | null {
  if (!isTypeScriptModuleSpecifier(specifier) || !isUnknownFileExtensionError(err)) return null;

  return `TypeScript config files require Node.js ${NODE_TYPESCRIPT_SUPPORT_RANGE}.\nDetected Node.js ${nodeVersion}.\nPlease upgrade Node.js or use a JSON config file instead.`;
}

// ---

function isTypeScriptModuleSpecifier(specifier: string): boolean {
  const ext = pathExtname(normalizeModuleSpecifierPath(specifier)).toLowerCase();
  return TS_MODULE_EXTENSIONS.has(ext);
}

function normalizeModuleSpecifierPath(specifier: string): string {
  if (!specifier.startsWith("file:")) return specifier;

  try {
    return fileURLToPath(specifier);
  } catch {
    return specifier;
  }
}

function isUnknownFileExtensionError(err: unknown): boolean {
  if ((err as { code?: unknown })?.code === "ERR_UNKNOWN_FILE_EXTENSION") return true;

  const message = (err as { message?: unknown })?.message;
  return typeof message === "string" && /unknown(?: or unsupported)? file extension/i.test(message);
}

// ---

if (import.meta.vitest) {
  const { it, expect } = import.meta.vitest;

  it("detects supported TypeScript config specifiers", () => {
    expect(isTypeScriptModuleSpecifier("/tmp/oxfmt.config.ts")).toBe(true);
    expect(isTypeScriptModuleSpecifier("/tmp/oxfmt.config.mts")).toBe(true);
    expect(isTypeScriptModuleSpecifier("/tmp/oxfmt.config.cts")).toBe(true);
    expect(isTypeScriptModuleSpecifier("file:///tmp/oxfmt.config.ts")).toBe(true);
    expect(isTypeScriptModuleSpecifier("/tmp/oxfmt.config.js")).toBe(false);
  });

  it("returns a node version hint for unsupported TypeScript module loading", () => {
    const err = new TypeError(
      'Unknown file extension ".ts" for /tmp/oxfmt.config.ts',
    ) as TypeError & {
      code?: string;
    };
    err.code = "ERR_UNKNOWN_FILE_EXTENSION";

    expect(getUnsupportedTypeScriptModuleLoadHint(err, "/tmp/oxfmt.config.ts", "v22.11.0")).toBe(
      `TypeScript config files require Node.js ${NODE_TYPESCRIPT_SUPPORT_RANGE}.\nDetected Node.js v22.11.0.\nPlease upgrade Node.js or use a JSON config file instead.`,
    );
  });

  it("does not add the hint for non-TypeScript specifiers or unrelated errors", () => {
    const err = new Error("Cannot find package");
    expect(getUnsupportedTypeScriptModuleLoadHint(err, "/tmp/oxfmt.config.ts")).toBeNull();

    const unknownExtension = new TypeError('Unknown file extension ".ts"');
    expect(
      getUnsupportedTypeScriptModuleLoadHint(unknownExtension, "/tmp/oxfmt.config.js"),
    ).toBeNull();
  });
}
PATCH

# Move js_config.ts to js_config/index.ts with updated import
cat > src-js/cli/js_config/index.ts << 'PATCH'
import { basename as pathBasename } from "node:path";
import { pathToFileURL } from "node:url";
import { getUnsupportedTypeScriptModuleLoadHint } from "./node_version";

const isObject = (v: unknown) => typeof v === "object" && v !== null && !Array.isArray(v);

const VITE_CONFIG_NAME = "vite.config.ts";
const VITE_OXFMT_CONFIG_FIELD = "fmt";

/**
 * Load a JavaScript/TypeScript config file.
 *
 * Uses native Node.js `import()` to evaluate the config file.
 * The config file should have a default export containing the oxfmt configuration object.
 *
 * For `vite.config.ts`, extracts the `.fmt` field from the default export.
 * Returns `null` if the field is missing, signaling "skip this config" to the Rust side.
 *
 * @param path - Absolute path to the JavaScript/TypeScript config file
 * @returns Config object, or `null` to signal "skip"
 */
export async function loadJsConfig(path: string): Promise<object | null> {
  // Bypass Node.js module cache to allow reloading changed config files (used for LSP)
  const fileUrl = pathToFileURL(path);
  fileUrl.searchParams.set("cache", Date.now().toString());

  const { default: config } = await import(fileUrl.href).catch((err) => {
    const hint = getUnsupportedTypeScriptModuleLoadHint(err, path);
    if (hint && err instanceof Error) err.message += `\n\n${hint}`;
    throw err;
  });

  if (config === undefined) throw new Error("Configuration file has no default export.");

  // Vite config: extract `.fmt` field
  if (pathBasename(path) === VITE_CONFIG_NAME) {
    // NOTE: Vite configs may export a function via `defineConfig(() => ({ ... }))`,
    // but we don't know the arguments to call the function.
    // Treat non-object exports as "no config" and skip.
    if (!isObject(config)) return null;

    const fmtConfig = (config as Record<string, unknown>)[VITE_OXFMT_CONFIG_FIELD];
    // NOTE: return `null` if missing (signals "skip" to Rust side)
    if (fmtConfig === undefined) return null;

    if (!isObject(fmtConfig)) {
      throw new Error(
        `The \`${VITE_OXFMT_CONFIG_FIELD}\` field in the default export must be an object.`,
      );
    }
    return fmtConfig;
  }

  if (!isObject(config)) {
    throw new Error("Configuration file must have a default export that is an object.");
  }

  return config;
}
PATCH

# Update cli.ts - change import from ./cli/js_config to ./cli/js_config/index
sed -i 's|import { loadJsConfig } from "./cli/js_config";|import { loadJsConfig } from "./cli/js_config/index";|' src-js/cli.ts

# Remove old node_version.ts
rm -f src-js/cli/node_version.ts

# Remove old js_config.ts (it was moved to js_config/index.ts)
rm -f src-js/cli/js_config.ts

# Remove old test file
rm -f test/cli/js_config/node_version.test.ts

# Update package.json - change test command
cat > package.json << 'PATCH'
{
  "name": "oxfmt-app",
  "version": "0.43.0",
  "private": true,
  "description": "Internal development package for oxfmt. For the published package.json template, see `npm/oxfmt/package.json`.",
  "license": "MIT",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "pnpm run build-napi-release && pnpm run build-js",
    "build-dev": "pnpm run build-napi && pnpm run build-js",
    "build-test": "pnpm run build-napi-test && pnpm run build-js",
    "build-napi": "napi build --esm --platform --js ./bindings.js --dts ./bindings.d.ts --output-dir src-js --no-dts-cache",
    "build-napi-test": "pnpm run build-napi --profile coverage",
    "build-napi-release": "pnpm run build-napi --release --features allocator",
    "build-js": "node scripts/build.js",
    "test": "vitest run",
    "conformance": "node conformance/run.ts",
    "download-fixtures": "node conformance/download-fixtures.js",
    "generate-config-types": "node scripts/generate-config-types.ts"
  },
  "dependencies": {
    "prettier": "3.8.1",
    "prettier-plugin-tailwindcss": "0.0.0-insiders.3997fbd",
    "tinypool": "2.1.0"
  },
  "devDependencies": {
    "@arethetypeswrong/core": "catalog:",
    "@napi-rs/cli": "catalog:",
    "@types/node": "catalog:",
    "degit": "^2.8.4",
    "diff": "^8.0.3",
    "execa": "^9.6.0",
    "json-schema-to-typescript": "catalog:",
    "tsdown": "catalog:",
    "vitest": "catalog:",
    "vscode-languageserver-protocol": "^3.17.5",
    "vscode-languageserver-textdocument": "^1.0.12"
  },
  "napi": {
    "binaryName": "oxfmt",
    "packageName": "@oxfmt/binding",
    "targets": [
      "aarch64-apple-darwin",
      "aarch64-linux-android",
      "aarch64-pc-windows-msvc",
      "aarch64-unknown-linux-gnu",
      "aarch64-unknown-linux-musl",
      "aarch64-unknown-linux-ohos",
      "armv7-linux-androideabi",
      "armv7-unknown-linux-gnueabihf",
      "armv7-unknown-linux-musleabihf",
      "i686-pc-windows-msvc",
      "powerpc64le-unknown-linux-gnu",
      "x86_64-apple-darwin",
      "x86_64-pc-windows-msvc",
      "x86_64-unknown-freebsd",
      "x86_64-unknown-linux-gnu",
      "x86_64-unknown-linux-musl"
    ]
  },
  "engines": {
    "node": "^20.19.0 || >=22.12.0"
  }
}
PATCH

# Update tsconfig.json - add vitest types
cat > tsconfig.json << 'PATCH'
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "module": "Preserve",
    "moduleResolution": "Bundler",
    "noEmit": true,
    "target": "ESNext",
    "strict": true,
    "skipLibCheck": true,
    "types": ["vitest/importMeta"]
  },
  "include": ["scripts", "conformance/*.ts", "src-js", "test/**/*.ts"],
  "exclude": ["test/**/fixtures"]
}
PATCH

# Update tsdown.config.ts - add import.meta.vitest define
cat > tsdown.config.ts << 'PATCH'
import { defineConfig } from "tsdown";

export default defineConfig({
  // Build all entry points together to share Prettier chunks
  entry: ["src-js/index.ts", "src-js/cli.ts", "src-js/cli-worker.ts"],
  format: "esm",
  platform: "node",
  target: "node20",
  dts: true,
  attw: { profile: "esm-only" },
  clean: true,
  outDir: "dist",
  shims: false,
  fixedExtension: false,
  define: { "import.meta.vitest": "undefined" },
  deps: {
    // Optional peer plugins that `prettier-plugin-tailwindcss` tries to dynamic import.
    // They are not installed and not needed for us,
    // mark as external to suppress "UNRESOLVED_IMPORT" warnings.
    neverBundle: [
      "@prettier/plugin-oxc",
      "@prettier/plugin-hermes",
      "@prettier/plugin-pug",
      "@shopify/prettier-plugin-liquid",
      "@zackad/prettier-plugin-twig",
      "prettier-plugin-astro",
      "prettier-plugin-marko",
      "prettier-plugin-svelte",
    ],
    alwaysBundle: [
      // Bundle it to control version
      "prettier",

      // Need to bundle plugins, since they depend on Prettier,
      // must be resolved to the same instance of Prettier at runtime.
      "prettier-plugin-tailwindcss",
      "prettier-plugin-tailwindcss/sorter",
      // Also, it internally loads plugins dynamically, so they also must be bundled
      /^prettier\/plugins\//,

      // Cannot bundle: `cli-worker.js` runs in separate thread and can't resolve bundled chunks
      // Be sure to add it to "dependencies" in `npm/oxfmt/package.json`!
      // "tinypool",
    ],
    // tsdown warns about final bundled modules by `alwaysBundle`.
    // But we know what we are doing, just suppress the warnings.
    onlyBundle: false,
  },
});
PATCH

# Update vitest.config.ts - include inline tests
cat > vitest.config.ts << 'PATCH'
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["./test/**/*.test.ts"],
    includeSource: ["./src-js/**/*.ts"],
    snapshotFormat: {
      escapeString: false,
      printBasicPrototype: false,
    },
    snapshotSerializers: [],
    testTimeout: 10000,
  },
});
PATCH

echo "Patch applied successfully"
