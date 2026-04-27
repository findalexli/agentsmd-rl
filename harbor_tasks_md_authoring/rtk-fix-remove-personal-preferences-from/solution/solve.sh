#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rtk

# Idempotency guard
if grep -qF "**Never assume** which project to work in. Always verify before file operations." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -508,13 +508,11 @@ hyperfine 'target/release/rtk git log -10' --warmup 3
 **ALWAYS confirm working directory before starting any work**:
 
 ```bash
-pwd  # Verify you're in /Users/florianbruniaux/Sites/rtk-ai/rtk
+pwd  # Verify you're in the rtk project root
 git branch  # Verify correct branch (main, feature/*, etc.)
 ```
 
-**Never assume** which project to work in. RTK shares parent directory with other projects (ccboard, cc-economics).
-
-**Context**: Wrong directory detection was a common friction point in multi-repo environments. Always verify before file operations.
+**Never assume** which project to work in. Always verify before file operations.
 
 ## Avoiding Rabbit Holes
 
@@ -545,16 +543,6 @@ When user provides a numbered plan (QW1-QW4, Phase 1-5, sprint tasks, etc.):
 
 **Why**: Plan-driven execution produces better outcomes than ad-hoc implementation. Structured plans help maintain focus and prevent scope creep.
 
-## Language & Communication
-
-- **User communicates in French**: Respond in French unless explicitly writing English content (docs, code comments, READMEs)
-- **"reprend"**: Resume previous task where it was left off
-- **Be direct**: User prefers direct, factual communication (Bold Guy style - cash, bienveillant, énergique)
-
-**Examples**:
-- ✅ "Ça ne va pas marcher parce que X. Voici ce que je ferais : Y."
-- ✅ "Le test échoue car le regex ne capture pas les commits merge. Fix : ajouter `(?:Merge|commit)`."
-- ❌ "Je pense que peut-être nous pourrions éventuellement envisager de..." (trop verbeux, pas direct)
 
 ## Filter Development Checklist
 
PATCH

echo "Gold patch applied."
