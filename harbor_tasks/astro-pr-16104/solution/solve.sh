#!/bin/bash
set -e
cd /workspace/astro

# The distinctive line from the patch for idempotency check
IDEMPOTENCY_CHECK="mergeConfig(userViteConfig, astroPreviewConfig)"

# Check if already patched (idempotency)
if grep -q "$IDEMPOTENCY_CHECK" packages/astro/src/core/preview/static-preview-server.ts 2>/dev/null; then
    echo "Already patched, skipping"
    exit 0
fi

# Use Python to make the changes (handles tabs correctly)
python3 << 'PYEOF'
filepath = '/workspace/astro/packages/astro/src/core/preview/static-preview-server.ts'
with open(filepath, 'r') as f:
    content = f.read()

# 1. Add mergeConfig to import
old_import = "import { preview, type PreviewServer as VitePreviewServer } from 'vite';"
new_import = "import { mergeConfig, preview, type PreviewServer as VitePreviewServer } from 'vite';"
if old_import in content:
    content = content.replace(old_import, new_import)
    print("Step 1: Updated import")
else:
    print("ERROR: Could not find import line")
    exit(1)

# 2. Replace the preview call block - matching actual file's single quotes
old_preview = """	let previewServer: VitePreviewServer;
	try {
		previewServer = await preview({
			configFile: false,
			base: settings.config.base,
			appType: 'mpa',
			build: {
				outDir: fileURLToPath(settings.config.outDir),
			},
			root: fileURLToPath(settings.config.root),
			preview: {
				host: settings.config.server.host,
				port: settings.config.server.port,
				headers: settings.config.server.headers,
				open: settings.config.server.open,
				allowedHosts: settings.config.server.allowedHosts,
			},
			plugins: [vitePluginAstroPreview(settings)],
		});
	} catch (err) {"""

new_preview = """	let previewServer: VitePreviewServer;
	try {
		// Build the Astro-specific preview config
		const astroPreviewConfig: vite.InlineConfig = {
			configFile: false,
			base: settings.config.base,
			appType: 'mpa',
			build: {
				outDir: fileURLToPath(settings.config.outDir),
			},
			root: fileURLToPath(settings.config.root),
			preview: {
				host: settings.config.server.host,
				port: settings.config.server.port,
				headers: settings.config.server.headers,
				open: settings.config.server.open,
			},
			plugins: [vitePluginAstroPreview(settings)],
		};

		// Merge user's vite config (from astro.config.mjs `vite` field) as the base,
		// then apply Astro's overrides on top. This ensures vite.preview.* settings
		// are respected while Astro-specific values (like configFile: false) always win.
		// Plugins are excluded from the user config since Astro manages its own plugin set.
		const { plugins: _plugins, ...userViteConfig } = settings.config.vite ?? {};
		const mergedViteConfig = mergeConfig(userViteConfig, astroPreviewConfig);

		// Apply allowedHosts after merging to avoid Vite's array concatenation behavior.
		// If the user explicitly set server.allowedHosts in Astro config (boolean or non-empty
		// array), that takes precedence. Otherwise, the user's vite.preview.allowedHosts from
		// settings.config.vite (merged above) is preserved.
		const { allowedHosts } = settings.config.server;
		if (
			typeof allowedHosts === 'boolean' ||
			(Array.isArray(allowedHosts) && allowedHosts.length > 0)
		) {
			mergedViteConfig.preview ??= {};
			mergedViteConfig.preview.allowedHosts = allowedHosts;
		}

		previewServer = await preview(mergedViteConfig);
	} catch (err) {"""

if old_preview in content:
    content = content.replace(old_preview, new_preview)
    print("Step 2: Replaced preview block")
else:
    print("ERROR: Could not find preview block to replace")
    exit(1)

with open(filepath, 'w') as f:
    f.write(content)

print("Patch applied successfully")
PYEOF