#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'tr\.row-odd' js/dataframe/shared/Table.svelte 2>/dev/null && ! grep -q 'nth-child' js/dataframe/shared/VirtualTable.svelte 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fix 1: RowNumber.svelte - remove background and nth-child rules
# Remove the line with background: var(--table-even-background-fill);
sed -i '/background: var(--table-even-background-fill);/d' js/dataframe/shared/RowNumber.svelte

# Remove the :global(tr:nth-child(odd)) .row-number block (4 lines)
sed -i '/:global(tr:nth-child(odd)) .row-number {/,/}/d' js/dataframe/shared/RowNumber.svelte

# Remove the :global(tr:nth-child(even)) .row-number block (4 lines)
sed -i '/:global(tr:nth-child(even)) .row-number {/,/}/d' js/dataframe/shared/RowNumber.svelte

# Fix 2: Table.svelte - change .row-odd to tr.row-odd and add base tr rule
# Replace '.row-odd {' with 'tr {\n\t\tbackground: var(--table-even-background-fill);\n\t}\n\n\ttr.row-odd {'
sed -i 's/^\t.row-odd {$/\ttr {\n\t\tbackground: var(--table-even-background-fill);\n\t}\n\n\ttr.row-odd {/' js/dataframe/shared/Table.svelte

# Fix 3: VirtualTable.svelte - remove nth-child rule
# Remove the tbody > :global(tr:nth-child(even)) block (3 lines)
sed -i '/tbody > :global(tr:nth-child(even)) {/,/}/d' js/dataframe/shared/VirtualTable.svelte

# Fix 4: CONTRIBUTING.md - update pnpm version
sed -i 's/pnpm 8.1+/pnpm 9.x/' CONTRIBUTING.md

# Fix 5: CONTRIBUTING.md - update browser test section
# Add browser test dependencies section after "pnpm test" line
sed -i '/^pnpm test$/a\
\
To install browser test dependencies:\
\
```\
pip install -r demo/outbreak_forecast/requirements.txt\
pip install -r demo/stream_video_out/requirements.txt\
pnpm exec playwright install chromium firefox\
pnpm exec playwright install-deps chromium firefox\
pnpm --filter @gradio/utils --filter @gradio/theme package\
```\
\
To run browser tests:' CONTRIBUTING.md

# Fix 6: js/README.md - update browser test setup
sed -i 's/pnpm exec playwright install chromium$/pnpm exec playwright install chromium firefox/' js/README.md
sed -i 's/pnpm exec playwright install-deps chromium$/pnpm exec playwright install-deps chromium firefox/' js/README.md
sed -i '/pnpm exec playwright install-deps chromium firefox/a\pnpm --filter @gradio/utils --filter @gradio/theme package' js/README.md

echo "Patch applied successfully."
