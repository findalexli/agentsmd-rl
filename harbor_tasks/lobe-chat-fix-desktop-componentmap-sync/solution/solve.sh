#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'SettingsTabs.Stats' src/routes/\(main\)/settings/features/componentMap.desktop.ts 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

echo "Applying fix..."

# Fix 1: componentMap.desktop.ts - add Stats and Creds imports and entries
DESKTOP_COMPONENTMAP="src/routes/(main)/settings/features/componentMap.desktop.ts"

# Add import for Creds after Appearance import
sed -i "/import Appearance from '..\/appearance';/a import Creds from '..\/creds';" "$DESKTOP_COMPONENTMAP"

# Add import for Stats after Skill import
sed -i "/import Skill from '..\/skill';/a import Stats from '..\/stats';" "$DESKTOP_COMPONENTMAP"

# Add Stats entry after Profile entry
sed -i '/\[SettingsTabs.Profile\]: Profile,/a\  [SettingsTabs.Stats]: Stats,' "$DESKTOP_COMPONENTMAP"

# Add Creds entry after APIKey entry
sed -i '/\[SettingsTabs.APIKey\]: APIKey,/a\  [SettingsTabs.Creds]: Creds,' "$DESKTOP_COMPONENTMAP"

# Fix 2: desktopRouter.config.desktop.tsx - add /onboarding route
DESKTOP_ROUTER="src/spa/router/desktopRouter.config.desktop.tsx"

# Add the onboarding route at the end of the file before the final newline
cat >> "$DESKTOP_ROUTER" << 'EOF'

// Web onboarding aliases redirect to the desktop-specific onboarding flow.
desktopRoutes.push({
  element: redirectElement('/desktop-onboarding'),
  errorElement: <ErrorBoundary resetPath="/" />,
  path: '/onboarding',
});
EOF

# Fix 3: code-review/SKILL.md - add SPA/routing section after i18n section
CODE_REVIEW_SKILL=".agents/skills/code-review/SKILL.md"
# Use a temp file approach since sed with newlines is tricky
head -n 38 "$CODE_REVIEW_SKILL" > /tmp/code_review_top.txt
tail -n +39 "$CODE_REVIEW_SKILL" > /tmp/code_review_bottom.txt
cat > /tmp/spa_section.txt << 'SPASECTION'

### SPA / routing

- **`desktopRouter` pair:** If the diff touches `src/spa/router/desktopRouter.config.tsx`, does it also update `src/spa/router/desktopRouter.config.desktop.tsx` with the same route paths and nesting? Single-file edits often cause drift and blank screens.
SPASECTION
cat /tmp/code_review_top.txt /tmp/spa_section.txt /tmp/code_review_bottom.txt > "$CODE_REVIEW_SKILL"

# Fix 4: react/SKILL.md - update lines and add sync rule
REACT_SKILL=".agents/skills/react/SKILL.md"

# Update the React Router DOM line
sed -i "s/| React Router DOM   | Main SPA (chat, settings)         | \`desktopRouter.config.tsx\`   |/| React Router DOM   | Main SPA (chat, settings)         | \`desktopRouter.config.tsx\` + \`desktopRouter.config.desktop.tsx\` (must match) |/" "$REACT_SKILL"

# Update Desktop router line
sed -i 's/- Desktop router: \`src\/spa\/router\/desktopRouter.config.tsx\`/- Desktop router (pair — **always edit both** when changing routes): \`src\/spa\/router\/desktopRouter.config.tsx\` (dynamic imports) and \`src\/spa\/router\/desktopRouter.config.desktop.tsx\` (sync imports). Drift can cause unregistered routes \/ blank screen./' "$REACT_SKILL"

# Add .desktop sync rule section at end of react/SKILL.md
cat >> "$REACT_SKILL" << 'EOF'

### `.desktop.{ts,tsx}` File Sync Rule

**CRITICAL**: Some files have a `.desktop.ts(x)` variant that Electron uses instead of the base file. When editing a base file, **always check** if a `.desktop` counterpart exists and update it in sync. Drift causes blank pages or missing features in Electron.

Known pairs that must stay in sync:

| Base file (web, dynamic imports) | Desktop file (Electron, sync imports) |
| --- | --- |
| `src/spa/router/desktopRouter.config.tsx` | `src/spa/router/desktopRouter.config.desktop.tsx` |
| `src/routes/(main)/settings/features/componentMap.ts` | `src/routes/(main)/settings/features/componentMap.desktop.ts` |

**How to check**: After editing any `.ts` / `.tsx` file, run `Glob` for `<filename>.desktop.{ts,tsx}` in the same directory. If a match exists, update it with the equivalent sync-import change.
EOF

# Fix 5: spa-routes/SKILL.md - update description and add content
SPA_ROUTES_SKILL=".agents/skills/spa-routes/SKILL.md"

# Update description line
sed -i 's/description: SPA route and feature structure. Use when adding or modifying SPA routes in src\/routes, defining new route segments, or moving route logic into src\/features. Covers how to keep routes thin and how to divide files between routes and features./description: MUST use when editing src\/routes\/ segments, src\/spa\/router\/desktopRouter.config.tsx or desktopRouter.config.desktop.tsx (always change both together), mobileRouter.config.tsx, or when moving UI\/logic between routes and src\/features\/./' "$SPA_ROUTES_SKILL"

# Add agent constraint after the roots vs features paragraph - using temp file approach
grep -n "roots vs features" "$SPA_ROUTES_SKILL"
# Get the line number of the "roots vs features" line
ROOTS_LINE=$(grep -n "roots vs features" "$SPA_ROUTES_SKILL" | head -1 | cut -d: -f1)
head -n "$ROOTS_LINE" "$SPA_ROUTES_SKILL" > /tmp/spa_top.txt
tail -n +$((ROOTS_LINE + 1)) "$SPA_ROUTES_SKILL" > /tmp/spa_bottom.txt
cat > /tmp/parity_constraint.txt << 'EOF'

**Agent constraint — desktop router parity:** Edits to the desktop route tree must update **both** `src/spa/router/desktopRouter.config.tsx` and `src/spa/router/desktopRouter.config.desktop.tsx` in the same change (same paths, nesting, index routes, and segment registration). Updating only one causes drift; the missing tree can fail to register routes and surface as a **blank screen** or broken navigation on the affected build.
EOF
cat /tmp/spa_top.txt /tmp/parity_constraint.txt /tmp/spa_bottom.txt > "$SPA_ROUTES_SKILL"

# Replace "5. **Register the route**" with updated version
sed -i 's/5. \*\*Register the route\*\*/5. **Register the route (desktop — two files, always)**/' "$SPA_ROUTES_SKILL"
sed -i 's/- Add the segment to \`src\/spa\/router\/desktopRouter.config.tsx\` (or the right router config) with \`dynamicElement\` \/ \`dynamicLayout\` pointing at the new route paths (e.g. \`@\/routes\/(main)\/my-feature\`)./- **`desktopRouter.config.tsx:`** Add the segment with `dynamicElement` \/ `dynamicLayout` pointing at route modules (e.g. `@\/routes\/(main)\/my-feature`).\n   - **`desktopRouter.config.desktop.tsx:`** Mirror the **same** `RouteObject` shape: identical `path` \/ `index` \/ parent-child structure. Use the static imports and elements already used in that file (see neighboring routes). Do **not** register in only one of these files.\n   - **Mobile-only flows:** use `mobileRouter.config.tsx` instead (no need to duplicate into the desktop pair unless the route truly exists on both)./' "$SPA_ROUTES_SKILL"

# Add desktop router pair section at end of spa-routes/SKILL.md
cat >> "$SPA_ROUTES_SKILL" << 'EOF'

---

## 3a. Desktop router pair (`desktopRouter.config` x 2)

| File | Role |
|------|------|
| `desktopRouter.config.tsx` | Dynamic imports via `dynamicElement` / `dynamicLayout` — code-splitting; used by `entry.web.tsx` and `entry.desktop.tsx`. |
| `desktopRouter.config.desktop.tsx` | Same route tree with **synchronous** imports — kept for Electron / local parity and predictable bundling. |

Anything that changes the tree (new segment, renamed `path`, moved layout, new child route) must be reflected in **both** files in one PR or commit. Remove routes from both when deleting.
EOF

echo "Fix applied successfully."
