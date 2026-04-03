#!/bin/bash
set -euo pipefail

CHANGES_VIEW="src/vs/sessions/contrib/changes/browser/changesView.ts"
CODE_REVIEW="src/vs/sessions/contrib/codeReview/browser/codeReview.contributions.ts"

# Check if patch is already applied
if grep -q "hasGitRepositoryContextKey" "$CHANGES_VIEW"; then
    echo "Patch already applied, skipping"
    exit 0
fi

# 1. changesView.ts: Add hasGitRepositoryContextKey constant after isolationModeContextKey line
sed -i "/^const isolationModeContextKey/a\\
const hasGitRepositoryContextKey = new RawContextKey<boolean>('sessions.hasGitRepository', true);" "$CHANGES_VIEW"

# 2. changesView.ts: Add bindContextKey block after dom.clearNode(this.actionsContainer);
#    Insert after the empty line following clearNode
node -e "
const fs = require('fs');
let src = fs.readFileSync('$CHANGES_VIEW', 'utf8');
const marker = 'dom.clearNode(this.actionsContainer);';
const idx = src.indexOf(marker);
if (idx === -1) { console.error('marker not found'); process.exit(1); }
const insertAfter = idx + marker.length;
// Find the next newline after marker, then skip the empty line
let pos = src.indexOf('\n', insertAfter) + 1; // end of clearNode line
pos = src.indexOf('\n', pos) + 1; // end of empty line
const block = [
  '',
  '\t\t\tthis.renderDisposables.add(bindContextKey(hasGitRepositoryContextKey, this.scopedContextKeyService, reader => {',
  '\t\t\t\tconst repository = this.viewModel.activeSessionRepositoryObs.read(reader);',
  '\t\t\t\treturn repository !== undefined;',
  '\t\t\t}));',
  '',
].join('\n');
src = src.slice(0, pos) + block + src.slice(pos);
fs.writeFileSync('$CHANGES_VIEW', src);
"

# 3. codeReview.contributions.ts: Add sessions.hasGitRepository condition after IsSessionsWindowContext
sed -i "/IsSessionsWindowContext,/a\\
$(printf '\t\t\t\t\t\t\t')ContextKeyExpr.equals('sessions.hasGitRepository', true)," "$CODE_REVIEW"

echo "Patch applied successfully"
