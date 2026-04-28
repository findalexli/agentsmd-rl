#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ssw.cleanarchitecture

# Idempotency guard
if grep -qF "This is a .NET 10 Clean Architecture template using Domain-Driven Design (DDD) t" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,6 +1,6 @@
-# SSW Clean Architecture - Copilot Instructions
+# SSW Clean Architecture - AGENTS.md
 
-This is a .NET 9 Clean Architecture template using Domain-Driven Design (DDD) tactical patterns, CQRS with MediatR, and .NET Aspire for orchestration.
+This is a .NET 10 Clean Architecture template using Domain-Driven Design (DDD) tactical patterns, CQRS with MediatR, and .NET Aspire for orchestration.
 
 ## Architecture Overview
 
PATCH

echo "Gold patch applied."
