#!/usr/bin/env bash
set -euo pipefail

cd /workspace/avoid-ai-writing

# Idempotency guard
if grep -qF "- \"Let's explore,\" \"Let's take a look,\" \"Let's break this down,\" \"Let's examine\"" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -77,6 +77,20 @@ The user will provide a piece of writing. Your job is to:
 | thriving | growing, active (or cite a number) |
 | despite challenges… continues to thrive | (name the challenge and the response, or cut) |
 | showcasing | showing, demonstrating (or cut the clause) |
+| nuanced | specific, subtle, detailed (or name the actual nuance) |
+| crucial | important, key, necessary |
+| multifaceted | (describe the actual facets, or cut) |
+| ecosystem (metaphor) | system, community, network, market |
+| myriad | many, numerous (or give a number) |
+| plethora | many, a lot of (or give a number) |
+| deep dive / dive into | look at, examine, explore |
+| unpack | explain, break down, walk through |
+| bolster | support, strengthen, back up |
+| spearhead | lead, drive, run |
+| resonate / resonates with | connect with, appeal to, matter to |
+| revolutionize | change, transform, reshape (or describe what changed) |
+| facilitate / facilitates | enable, help, allow, run |
+| underpin | support, form the basis of |
 
 ### Template phrases (avoid)
 
@@ -116,12 +130,10 @@ These slot-fill constructions signal that a sentence was generated, not written.
 
 ### Filler phrases
 - Strip mechanical padding that adds words without meaning:
-  - "In order to" → "To"
-  - "Due to the fact that" → "Because"
   - "It is important to note that" → (just state it)
-  - "At the end of the day" → (cut)
   - "In terms of" → (rewrite)
   - "The reality is that" → (cut or just state the claim)
+- Note: "In order to," "Due to the fact that," and "At the end of the day" are covered in the word/phrase table and transition sections above — don't duplicate rules.
 
 ### Generic conclusions
 - "The future looks bright," "Only time will tell," "One thing is certain," "As we move forward" — these are filler disguised as conclusions. Cut them. If the piece needs a closing thought, make it specific to the argument.
@@ -130,6 +142,9 @@ These slot-fill constructions signal that a sentence was generated, not written.
 - "I hope this helps!", "Certainly!", "Absolutely!", "Great question!", "Feel free to reach out," "Let me know if you need anything else" — these are conversational tics from chat interfaces, not writing. Remove entirely.
 - Also watch for: "In this article, we will explore…" or "Let's dive in!" — these are AI-generated meta-narration. Cut or rewrite with a direct opening.
 
+### "Let's" constructions
+- "Let's explore," "Let's take a look," "Let's break this down," "Let's examine" — AI uses "let's" as a false-collaborative opener to ease into a topic. It's filler that delays the actual point. Just start with the point. "Let's dive in" is covered above under chatbot artifacts, but the pattern is broader than that — flag any "let's + verb" that's functioning as a transition rather than a genuine invitation to act.
+
 ### Notability name-dropping
 - AI text piles on prestigious citations to manufacture credibility: "cited in The New York Times, BBC, Financial Times, and The Hindu." If a source matters, use it with context: "In a 2024 NYT interview, she argued..." One specific reference beats four name-drops.
 
PATCH

echo "Gold patch applied."
