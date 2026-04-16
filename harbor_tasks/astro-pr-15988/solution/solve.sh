#!/bin/bash
set -e
cd /workspace/astro

# The fix for withastro/astro#15988: CSS from dynamically imported components
# not injected on first dev server load.
#
# The fix adds ensureModulesLoaded() to pre-walk the Vite module graph and
# eagerly fetch/transform untransformed modules before CSS dependency collection.

FILE=packages/astro/src/vite-plugin-css/index.ts

# First, add ensureModulesLoaded function before collectCSSWithOrder
python3 << 'PYTHON'
with open('packages/astro/src/vite-plugin-css/index.ts', 'r') as f:
    lines = f.readlines()

# Find the line containing "Walk down the dependency tree" comment and then
# search backwards to find the opening /** of the JSDoc block
insert_idx = None
jsdoc_start = None
for i, line in enumerate(lines):
    if 'Walk down the dependency tree to collect CSS with depth/order' in line:
        # Search backwards for the opening /**
        for j in range(i - 1, -1, -1):
            if lines[j].strip() == '/**':
                jsdoc_start = j
                break
        break

if jsdoc_start is None:
    print("ERROR: Could not find collectCSSWithOrder JSDoc comment")
    exit(1)

insert_idx = jsdoc_start

if insert_idx is None:
    print("ERROR: Could not find collectCSSWithOrder comment")
    exit(1)

# The new function to add before this comment
ensure_modules_func = '''/**
 * Ensure all modules reachable from the given module have been fetched and transformed.
 * This is needed for dynamically imported components whose modules may be registered
 * in the graph (via Vite's import analysis) but not yet transformed, meaning their
 * own imports (including CSS) would not be visible during the CSS graph walk.
 */
async function ensureModulesLoaded(
	env: DevEnvironment,
	mod: vite.EnvironmentModuleNode,
	seen = new Set<string>(),
): Promise<void> {
	const id = mod.id ?? mod.url;
	if (seen.has(id)) return;
	seen.add(id);

	for (const imp of mod.importedModules) {
		if (!imp.id) continue;
		if (seen.has(imp.id)) continue;
		if (imp.id.includes(PROPAGATED_ASSET_QUERY_PARAM)) continue;

		if (!imp.transformResult) {
			try {
				await env.fetchModule(imp.id);
			} catch {
				// Module may not be fetchable (e.g., virtual modules that resolve differently).
			}
		}

		await ensureModulesLoaded(env, imp, seen);
	}
}

'''

# Insert the function before the comment
lines.insert(insert_idx, ensure_modules_func)

with open('packages/astro/src/vite-plugin-css/index.ts', 'w') as f:
    f.writelines(lines)

print(f"Added ensureModulesLoaded function before line {insert_idx+1}")
PYTHON

# Second, add the call to ensureModulesLoaded before collectCSSWithOrder loop
python3 << 'PYTHON'
with open('packages/astro/src/vite-plugin-css/index.ts', 'r') as f:
    content = f.read()

# Find the pattern: after "if (!mod)" block, before "// Walk through the graph depth-first"
old_text = '''if (!mod) {
							return {
								code: 'export const css = new Set()',
							};
						}

						// Walk through the graph depth-first'''

new_text = '''if (!mod) {
							return {
								code: 'export const css = new Set()',
							};
						}

						// Ensure all reachable modules have been transformed.
						// Dynamically imported components may be in the graph (detected by Vite's
						// import analysis) but not yet transformed, so their own CSS imports would
						// be invisible during the graph walk. This eagerly fetches them.
						if (env) {
							await ensureModulesLoaded(env, mod);
						}

						// Walk through the graph depth-first'''

if old_text not in content:
    print("ERROR: Could not find the pattern to insert ensureModulesLoaded call")
    print("Looking for:", repr(old_text[:100]))
    exit(1)

content = content.replace(old_text, new_text)

with open('packages/astro/src/vite-plugin-css/index.ts', 'w') as f:
    f.write(content)

print("Added ensureModulesLoaded call before collectCSSWithOrder")
PYTHON
