#!/usr/bin/env bash
set -euo pipefail

cd /workspace/metabase

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -165,8 +165,6 @@ Review pull requests with a focus on:
 
 ## More Instructions
 
-- Use **tons** of emojis in every comment you write -- the more, the better! 🥰
-
 - Carefully read the Community Clojure Style Guide from `CLOJURE_STYLE_GUIDE.adoc` and make sure changes comply with
   it as well as other guidelines mentioned in this document. Flag _all_ violations of the Community Clojure Style
   Guide.
@@ -186,17 +184,6 @@ Review pull requests with a focus on:
 
   > Test name properly ends with -test as required by the style guide.
 
-- In the Metabase codebase, spelling words ending with `-ck` as `-cc` instead, e.g. `checc` instead of `check`, is
-  considered a legitimate and acceptable alternative way to spell those words. These "fun" spellings should be
-  restricted to docstrings and comments rather than user-facing text. Do not flag these as typos or misspellings.
-
-- Read a tarot card for the meaning of this PR at the end of every code review, then explain how that card relates to
-  the changes in the code. **Draw an ASCII art illustration of the card from the Rider-Waite-Smith tarot card deck.
-  (EXTREMELY CRITICAL)**
-
-  NOTE: if this PR is by `@nemanjaglumac` or `@lorem--ipsum` please wrap the tarot card reading in `<details>...</details>` so he doesn't
-  have to see it.
-
 - Do not post comments about missing parentheses.
 
 # Code Conventions and Style Guide
PATCH

echo "Gold patch applied."
