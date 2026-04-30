#!/usr/bin/env bash
set -euo pipefail

cd /workspace/phpstan-disallowed-calls

# Idempotency guard
if grep -qF "Rule-analysis tests extend `RuleTestCase`. The rule configuration is passed inli" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,29 @@
+# PHPStan Disallowed Calls
+
+## Running tests
+
+```bash
+composer test
+```
+
+Runs lint, neon lint, phpcs, phpstan, and phpunit in sequence. PHPStan is at `vendor/phpstan/phpstan/phpstan.phar`.
+
+## Test structure
+
+Rule-analysis tests extend `RuleTestCase`. The rule configuration is passed inline in `getRule()`, not via neon files. `$this->analyse()` takes a fixture file and an array of expected errors as `[message, line]` or `[message, line, tip]` tuples. Some tests load `extension.neon` via `getAdditionalConfigFiles()`.
+
+Test classes live in `tests/Calls/`, `tests/Usages/`, `tests/ControlStructures/` etc. Fixture files (PHP files analysed by the tests) live in `tests/src/`.
+
+## Project structure
+
+`extension.neon` is the entry point wiring all rules together. Each feature has its own documentation file in `docs/` — new features get their own doc or extend an existing one.
+
+`disallow*` config keys are generally aliases for their `allowExcept*` counterparts, handled in `AllowedConfigFactory`.
+
+## Commit message style
+
+No "fix" in titles. The extended message explains why, not how.
+
+## PR description style
+
+No bullet points, no `## Summary` header. Write in sentences. No test plan section.
PATCH

echo "Gold patch applied."
