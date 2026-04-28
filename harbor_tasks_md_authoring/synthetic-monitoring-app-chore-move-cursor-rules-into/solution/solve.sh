#!/usr/bin/env bash
set -euo pipefail

cd /workspace/synthetic-monitoring-app

# Idempotency guard
if grep -qF ".cursor/rules/documentation.mdc" ".cursor/rules/documentation.mdc" && grep -qF ".cursor/rules/engineering-best-practices.mdc" ".cursor/rules/engineering-best-practices.mdc" && grep -qF ".cursor/rules/file-organisation.mdc" ".cursor/rules/file-organisation.mdc" && grep -qF ".cursor/rules/reference-directory.mdc" ".cursor/rules/reference-directory.mdc" && grep -qF ".cursor/rules/team-composition.mdc" ".cursor/rules/team-composition.mdc" && grep -qF ".cursor/rules/this-product.mdc" ".cursor/rules/this-product.mdc" && grep -qF ".cursor/rules/when-creating-prs.mdc" ".cursor/rules/when-creating-prs.mdc" && grep -qF ".cursor/rules/when-writing-tests.mdc" ".cursor/rules/when-writing-tests.mdc" && grep -qF ".cursor/rules/you-and-me.mdc" ".cursor/rules/you-and-me.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/documentation.mdc b/.cursor/rules/documentation.mdc

diff --git a/.cursor/rules/engineering-best-practices.mdc b/.cursor/rules/engineering-best-practices.mdc

diff --git a/.cursor/rules/file-organisation.mdc b/.cursor/rules/file-organisation.mdc

diff --git a/.cursor/rules/reference-directory.mdc b/.cursor/rules/reference-directory.mdc

diff --git a/.cursor/rules/team-composition.mdc b/.cursor/rules/team-composition.mdc

diff --git a/.cursor/rules/this-product.mdc b/.cursor/rules/this-product.mdc

diff --git a/.cursor/rules/when-creating-prs.mdc b/.cursor/rules/when-creating-prs.mdc

diff --git a/.cursor/rules/when-writing-tests.mdc b/.cursor/rules/when-writing-tests.mdc

diff --git a/.cursor/rules/you-and-me.mdc b/.cursor/rules/you-and-me.mdc

PATCH

echo "Gold patch applied."
