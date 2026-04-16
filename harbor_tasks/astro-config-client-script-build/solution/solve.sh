#!/bin/bash
set -e

cd /workspace/astro

# Apply the fix for astro:config/client build failure in client scripts
cat <<'PATCH' | git apply -
diff --git a/packages/astro/src/core/create-vite.ts b/packages/astro/src/core/create-vite.ts
index 1d35bad22f5e..e8aaaf05583e 100644
--- a/packages/astro/src/core/create-vite.ts
+++ b/packages/astro/src/core/create-vite.ts
@@ -136,7 +136,7 @@ export async function createVite(
 			}),
 			vitePluginStaticPaths(),
 			await astroPluginRoutes({ routesList, settings, logger, fsMod: fs, command }),
-			astroVirtualManifestPlugin(),
+			astroVirtualManifestPlugin({ settings }),
 			vitePluginEnvironment({ settings, astroPkgsConfig, command }),
 			pluginPage({ routesList }),
 			pluginPages({ routesList }),
diff --git a/packages/astro/src/manifest/serialized.ts b/packages/astro/src/manifest/serialized.ts
index 61afe60aed75..75e2664ce3db 100644
--- a/packages/astro/src/manifest/serialized.ts
+++ b/packages/astro/src/manifest/serialized.ts
@@ -72,6 +72,16 @@ export function serializedManifestPlugin({
 			server.watcher.on('change', (path) => reloadManifest(path, server));
 		},

+		// Restrict to server environments only since the generated code imports
+		// server-only virtual modules (virtual:astro:routes, virtual:astro:pages)
+		applyToEnvironment(environment) {
+			return (
+				environment.name === ASTRO_VITE_ENVIRONMENT_NAMES.astro ||
+				environment.name === ASTRO_VITE_ENVIRONMENT_NAMES.ssr ||
+				environment.name === ASTRO_VITE_ENVIRONMENT_NAMES.prerender
+			);
+		},
+
 		resolveId: {
 			filter: {
 				id: new RegExp(`^${SERIALIZED_MANIFEST_ID}$`),
diff --git a/packages/astro/src/manifest/virtual-module.ts b/packages/astro/src/manifest/virtual-module.ts
index 627008a1082f..5d6da15dc232 100644
--- a/packages/astro/src/manifest/virtual-module.ts
+++ b/packages/astro/src/manifest/virtual-module.ts
@@ -2,13 +2,59 @@ import type { Plugin } from 'vite';
 import { AstroError, AstroErrorData } from '../core/errors/index.js';
 import { SERIALIZED_MANIFEST_ID } from './serialized.js';
 import { ASTRO_VITE_ENVIRONMENT_NAMES } from '../core/constants.js';
+import { fromRoutingStrategy, toFallbackType, toRoutingStrategy } from '../core/app/common.js';
+import type { AstroSettings } from '../types/astro.js';

 const VIRTUAL_SERVER_ID = 'astro:config/server';
 const RESOLVED_VIRTUAL_SERVER_ID = '\0' + VIRTUAL_SERVER_ID;
 const VIRTUAL_CLIENT_ID = 'astro:config/client';
 const RESOLVED_VIRTUAL_CLIENT_ID = '\0' + VIRTUAL_CLIENT_ID;

-export default function virtualModulePlugin(): Plugin {
+export default function virtualModulePlugin({ settings }: { settings: AstroSettings }): Plugin {
+	// Pre-compute the client config values from settings so that astro:config/client
+	// doesn't need to import from virtual:astro:manifest (which pulls in server-only
+	// virtual modules like virtual:astro:routes and virtual:astro:pages that are
+	// restricted to server environments via applyToEnvironment).
+	const config = settings.config;
+
+	let i18nCode = 'const i18n = undefined;';
+	if (config.i18n) {
+		// Apply the same toRoutingStrategy → fromRoutingStrategy roundtrip that the
+		// serialized manifest uses, to ensure consistent routing config values.
+		const strategy = toRoutingStrategy(config.i18n.routing, config.i18n.domains);
+		const fallbackType = toFallbackType(config.i18n.routing);
+		const routing = fromRoutingStrategy(strategy, fallbackType);
+		i18nCode = `const i18n = {
+  defaultLocale: ${JSON.stringify(config.i18n.defaultLocale)},
+  locales: ${JSON.stringify(config.i18n.locales)},
+  routing: ${JSON.stringify(routing)},
+  fallback: ${JSON.stringify(config.i18n.fallback)}
+};`;
+	}
+
+	let imageCode = 'const image = undefined;';
+	if (config.image) {
+		imageCode = `const image = {
+  objectFit: ${JSON.stringify(config.image.objectFit)},
+  objectPosition: ${JSON.stringify(config.image.objectPosition)},
+  layout: ${JSON.stringify(config.image.layout)},
+};`;
+	}
+
+	const clientConfigCode = `
+${i18nCode}
+${imageCode}
+const base = ${JSON.stringify(config.base)};
+const trailingSlash = ${JSON.stringify(config.trailingSlash)};
+const site = ${JSON.stringify(config.site)};
+const compressHTML = ${JSON.stringify(config.compressHTML)};
+const build = {
+  format: ${JSON.stringify(config.build.format)},
+};
+
+export { base, i18n, trailingSlash, site, compressHTML, build, image };
+`;
+
 	return {
 		name: 'astro-manifest-plugin',
 		resolveId: {
@@ -30,41 +76,11 @@ export default function virtualModulePlugin(): Plugin {
 			},
 			handler(id) {
 				if (id === RESOLVED_VIRTUAL_CLIENT_ID) {
-					// There's nothing wrong about using `/client` on the server
-					const code = `
-import { manifest } from '${SERIALIZED_MANIFEST_ID}'
-import { fromRoutingStrategy } from 'astro/app';
-
-let i18n = undefined;
-if (manifest.i18n) {
-i18n = {
-  defaultLocale: manifest.i18n.defaultLocale,
-  locales: manifest.i18n.locales,
-  routing: fromRoutingStrategy(manifest.i18n.strategy, manifest.i18n.fallbackType),
-  fallback: manifest.i18n.fallback
-  };
-}
-
-let image = undefined;
-if (manifest.image) {
-  image = {
-    objectFit: manifest.image.objectFit,
-    objectPosition: manifest.image.objectPosition,
-    layout: manifest.image.layout,
-  };
-}
-
-const base = manifest.base;
-const trailingSlash = manifest.trailingSlash;
-const site = manifest.site;
-const compressHTML = manifest.compressHTML;
-const build = {
-  format: manifest.buildFormat,
-};
-
-export { base, i18n, trailingSlash, site, compressHTML, build, image };
-				`;
-					return { code };
+					// astro:config/client inlines values directly from settings instead of
+					// importing from virtual:astro:manifest to avoid pulling server-only
+					// virtual modules (virtual:astro:routes, virtual:astro:pages) into the
+					// client environment where they are not available.
+					return { code: clientConfigCode };
 				}
 				if (id === RESOLVED_VIRTUAL_SERVER_ID) {
 					if (this.environment.name === ASTRO_VITE_ENVIRONMENT_NAMES.client) {
PATCH

# Idempotency check - verify the distinctive change is present
if ! grep -q "Pre-compute the client config values from settings" packages/astro/src/manifest/virtual-module.ts; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

# Rebuild the astro package to apply the changes
pnpm -C packages/astro build

echo "Fix applied successfully"
