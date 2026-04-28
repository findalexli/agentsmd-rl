#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hanzi-browse

# Idempotency guard
if grep -qF "description: 'Search for apartments across multiple real estate platforms, compa" "server/skills/apartment-finder/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/server/skills/apartment-finder/SKILL.md b/server/skills/apartment-finder/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: apartment-finder
-description: Search for apartments across multiple real estate platforms, compare listings side by side, and help submit inquiries or applications. Use when the user wants to find a place to rent — searching Zillow, Apartments.com, Craigslist, and similar sites with their real signed-in browser. Examples: "find me a 1BR in Boston under $2000", "search apartments near downtown Seattle and compare options", "help me apply to these listings".
+description: 'Search for apartments across multiple real estate platforms, compare listings side by side, and help submit inquiries or applications. Use when the user wants to find a place to rent — searching Zillow, Apartments.com, Craigslist, and similar sites with their real signed-in browser. Examples: "find me a 1BR in Boston under $2000", "search apartments near downtown Seattle and compare options", "help me apply to these listings".'
 category: life
 ---
 
PATCH

echo "Gold patch applied."
