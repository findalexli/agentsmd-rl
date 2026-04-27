#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "EnableNUnitRunner, UseMicrosoftTestingPlatformRunner, dotnet test exit" "plugins/dotnet-test/skills/migrate-vstest-to-mtp/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/dotnet-test/skills/migrate-vstest-to-mtp/SKILL.md b/plugins/dotnet-test/skills/migrate-vstest-to-mtp/SKILL.md
@@ -4,12 +4,13 @@ description: >
   Migrates .NET test projects from VSTest to Microsoft.Testing.Platform (MTP).
   Use when user asks to "migrate to MTP", "switch from VSTest", "enable
   Microsoft.Testing.Platform", "use MTP runner", or mentions EnableMSTestRunner,
-  EnableNUnitRunner, UseMicrosoftTestingPlatformRunner, or dotnet test exit
-  code 8. Supports MSTest, NUnit, xUnit.net v2 (via YTest.MTP.XUnit2), and
-  xUnit.net v3 (native MTP). Also covers translating xUnit.net v3 MTP filter
-  syntax (--filter-class, --filter-trait, --filter-query).
-  Covers runner enablement, CLI argument translation, Directory.Build.props
-  and global.json configuration, CI/CD pipeline updates, and MTP extension
+  EnableNUnitRunner, UseMicrosoftTestingPlatformRunner, dotnet test exit
+  code 8, zero tests discovered, or MTP behavioral differences
+  (--ignore-exit-code, TESTINGPLATFORM_EXITCODE_IGNORE).
+  Supports MSTest, NUnit, xUnit.net v2 (via YTest.MTP.XUnit2), and
+  xUnit.net v3 (native MTP). Covers runner enablement, CLI argument
+  translation, xUnit.net v3 filter syntax, Directory.Build.props and
+  global.json configuration, CI/CD pipeline updates, and MTP extension
   packages. DO NOT USE FOR: migrating between test frameworks
   (MSTest/xUnit/NUnit), xUnit.net v2 to v3 API migration, MSTest version
   upgrades (use migrate-mstest-* skills), TFM upgrades, or UWP/WinUI test
PATCH

echo "Gold patch applied."
