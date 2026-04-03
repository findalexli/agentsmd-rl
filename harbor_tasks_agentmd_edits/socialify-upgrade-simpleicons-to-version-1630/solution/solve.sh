#!/usr/bin/env bash
set -euo pipefail

cd /workspace/socialify

# Idempotent: skip if already applied
if grep -q 'customHeroku' common/icons/customIcons.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Add custom Heroku, OpenAI, Slack icons to customIcons.ts
cat >> common/icons/customIcons.ts <<'ICONS_EOF'

export const customHeroku: SimpleIcon = {
  title: 'Heroku',
  slug: 'heroku',
  hex: '430098',
  source: 'https://devcenter.heroku.com/articles/heroku-brand-guidelines#logos',
  guidelines: 'https://devcenter.heroku.com/articles/heroku-brand-guidelines',
  path: 'M20.61 0H3.39C2.189 0 1.23.96 1.23 2.16v19.681c0 1.198.959 2.159 2.16 2.159h17.22c1.2 0 2.159-.961 2.159-2.159V2.16C22.77.96 21.811 0 20.61 0zm.96 21.841c0 .539-.421.96-.96.96H3.39c-.54 0-.96-.421-.96-.96V2.16c0-.54.42-.961.96-.961h17.22c.539 0 .96.421.96.961v19.681zM6.63 20.399L9.33 18l-2.7-2.4v4.799zm9.72-9.719c-.479-.48-1.379-1.08-2.879-1.08-1.621 0-3.301.421-4.5.84V3.6h-2.4v10.38l1.68-.78s2.76-1.26 5.16-1.26c1.2 0 1.5.66 1.5 1.26v7.2h2.4v-7.2c.059-.179.059-1.501-.961-2.52zM13.17 7.5h2.4c1.08-1.26 1.62-2.521 1.8-3.9h-2.399c-.241 1.379-.841 2.64-1.801 3.9z',
  get svg() {
    return `<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>${this.title}</title><path d="${this.path}"/></svg>`
  },
}

export const customOpenAI: SimpleIcon = {
  title: 'OpenAI',
  slug: 'openai',
  hex: '412991',
  source: 'https://openai.com/brand',
  guidelines: 'https://openai.com/brand',
  path: 'M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z',
  get svg() {
    return `<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>${this.title}</title><path d="${this.path}"/></svg>`
  },
}

export const customSlack: SimpleIcon = {
  title: 'Slack',
  slug: 'slack',
  hex: '4A154B',
  source: 'https://slack.com/brand-guidelines',
  guidelines: 'https://slack.com/brand-guidelines',
  path: 'M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z',
  get svg() {
    return `<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>${this.title}</title><path d="${this.path}"/></svg>`
  },
}
ICONS_EOF

# 2. Update languageMapping.ts: remove si* imports, add custom* imports, update mapping
sed -i '/^  siHeroku,$/d' common/icons/languageMapping.ts
sed -i '/^  siOpenai,$/d' common/icons/languageMapping.ts
sed -i '/^  siSlack,$/d' common/icons/languageMapping.ts

# Add custom imports to the customIcons import block
sed -i 's/  customCsharp,/  customCsharp,\n  customHeroku,/' common/icons/languageMapping.ts
sed -i 's/  customMicrosoftAzure,/  customMicrosoftAzure,\n  customOpenAI,/' common/icons/languageMapping.ts
sed -i 's/  customPowershell,/  customPowershell,\n  customSlack,/' common/icons/languageMapping.ts

# Update the mapping entries
sed -i "s/Heroku: siHeroku,/Heroku: customHeroku,/" common/icons/languageMapping.ts
sed -i "s/OpenAI: siOpenai,/OpenAI: customOpenAI,/" common/icons/languageMapping.ts
sed -i "s/Slack: siSlack,/Slack: customSlack,/" common/icons/languageMapping.ts

# 3. Update package.json: bump simple-icons version
sed -i 's/"simple-icons": "\^15\.22\.0"/"simple-icons": "^16.3.0"/' package.json

# 4. Install updated deps (regenerates lockfile)
pnpm install --no-frozen-lockfile

# 5. Update AGENTS.md: add .github/skills/ to project structure and AI Skills section
sed -i '/├── \.devcontainer\//a ├── .github/skills/         # AI skills for repo-specific workflows' AGENTS.md

# Add AI Skills section before ### Testing
sed -i '/^### Testing$/i ## AI Skills\n\n- `/.github/skills/upgrade-simple-icons/` - Upgrade the simple-icons dependency and preserve icons that are no longer available via custom mappings.\n' AGENTS.md

# 6. Create SKILL.md for upgrade-simple-icons
mkdir -p .github/skills/upgrade-simple-icons
cat > .github/skills/upgrade-simple-icons/SKILL.md <<'SKILL_EOF'
---
name: upgrade-simple-icons
description: Upgrade simple-icons to the latest version and preserve any removed icons by sourcing them from the previous version into common/icons/customIcons.ts and updating icon mappings. Use whenever bumping or upgrading simple-icons in this repo.
---

# Upgrade simple-icons

## Workflow

1. Record the current simple-icons version from `package.json` and `pnpm-lock.yaml`.
2. Install the latest package: `pnpm add simple-icons@latest`.
3. Reconcile icon imports:
   - Review `common/icons/languageMapping.ts` for imports from `simple-icons`.
   - Run `pnpm lint` or `pnpm verify` to surface missing icon exports.
4. If any previously used icon is missing after the upgrade:
   - Download the previous simple-icons version (recorded in step 1) to a temporary location or install it briefly.
   - Extract the icon data (`title`, `slug`, `hex`, `path`). In simple-icons, this is available from the `si*` export or `icons/<slug>.json` in the package.
   - Add a `custom<IconName>` entry to `common/icons/customIcons.ts` with the extracted data.
   - Update `common/icons/languageMapping.ts` to import and reference the custom icon.
   - Run `pnpm lint:fix` to fix import ordering issues if any.
   - Remove any temporary dependency or scratch folder after the data is captured.
5. Update relevant documentation if icon mappings or customization behavior changes.
6. Run `pnpm verify` before committing, and add a changeset for the upgrade.
SKILL_EOF

# 7. Create changeset
cat > .changeset/red-grapes-relate.md <<'CS_EOF'
---
"socialify": patch
---

Upgrade simple-icons and add custom fallbacks for removed icons
CS_EOF

echo "Patch applied successfully."
