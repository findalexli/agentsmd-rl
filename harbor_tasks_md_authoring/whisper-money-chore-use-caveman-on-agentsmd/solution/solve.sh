#!/usr/bin/env bash
set -euo pipefail

cd /workspace/whisper-money

# Idempotency guard
if grep -qF "Drop: articles, filler (just/really/basically), pleasantries, hedging." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,3 +1,10 @@
+Terse like caveman. Technical substance exact. Only fluff die.
+Drop: articles, filler (just/really/basically), pleasantries, hedging.
+Fragments OK. Short synonyms. Code unchanged.
+Pattern: [thing] [action] [reason]. [next step].
+ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.
+Code/commits/PRs: normal. Off: "stop caveman" / "normal mode".
+
 <laravel-boost-guidelines>
 === foundation rules ===
 
@@ -118,7 +125,7 @@ This project has domain-specific skills available. You MUST activate the relevan
 ## Constructors
 
 - Use PHP 8 constructor property promotion in `__construct()`.
-    - `public function __construct(public GitHub $github) { }`
+  - `public function __construct(public GitHub $github) { }`
 - Do not allow empty `__construct()` methods with zero parameters unless the constructor is private.
 
 ## Type Declarations
@@ -127,6 +134,7 @@ This project has domain-specific skills available. You MUST activate the relevan
 - Use appropriate PHP type hints for method parameters.
 
 <!-- Explicit Return Types and Method Params -->
+
 ```php
 protected function isAccessible(User $user, ?string $path = null): bool
 {
PATCH

echo "Gold patch applied."
