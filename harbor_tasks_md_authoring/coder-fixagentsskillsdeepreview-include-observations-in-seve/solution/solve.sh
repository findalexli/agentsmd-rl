#!/usr/bin/env bash
set -euo pipefail

cd /workspace/coder

# Idempotency guard
if grep -qF "- **Unnecessary novelty.** New files, new naming patterns, new abstractions wher" ".agents/skills/deep-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/deep-review/SKILL.md b/.agents/skills/deep-review/SKILL.md
@@ -52,7 +52,7 @@ If a prior agent review exists, you must produce a prior-findings classification
 3. Engage with any author questions before re-raising findings.
 4. Write `$REVIEW_DIR/prior-findings.md` with this format:
 
-```
+```markdown
 # Prior findings from round {N}
 
 | Finding | Author response | Status |
@@ -83,7 +83,7 @@ For each changed file, briefly check the surrounding context:
 
 Match reviewer roles to layers touched. The Test Auditor, Edge Case Analyst, and Contract Auditor always run. Conditional reviewers activate when their domain is touched.
 
-**Tier 1 — Structural reviewers**
+### Tier 1 — Structural reviewers
 
 | Role                 | Focus                                                       | When                                                        |
 | -------------------- | ----------------------------------------------------------- | ----------------------------------------------------------- |
@@ -100,7 +100,7 @@ Match reviewer roles to layers touched. The Test Auditor, Edge Case Analyst, and
 | Go Architect         | Package boundaries, API lifecycle, middleware               | Go code, API design, middleware, package boundaries         |
 | Concurrency Reviewer | Goroutines, channels, locks, shutdown                       | Goroutines, channels, locks, context cancellation, shutdown |
 
-**Tier 2 — Nit reviewers**
+### Tier 2 — Nit reviewers
 
 | Role                   | Focus                                        | File filter                         |
 | ---------------------- | -------------------------------------------- | ----------------------------------- |
@@ -126,7 +126,7 @@ Spawn all Tier 1 and Tier 2 reviewers in parallel. Give each reviewer a referenc
 
 **Tier 1 prompt:**
 
-```
+```text
 Read `AGENTS.md` in this repository before starting.
 
 You are the {Role Name} reviewer. Read your methodology in
@@ -141,7 +141,7 @@ Output file: {REVIEW_DIR}/{role-name}.md
 
 **Tier 2 prompt:**
 
-```
+```text
 Read `AGENTS.md` in this repository before starting.
 
 You are the {Role Name} reviewer. Read your methodology in
@@ -193,12 +193,12 @@ Handle Tier 1 and Tier 2 findings separately before merging.
 - **Async findings.** When a finding mentions setState after unmount, unused cancellation signals, or missing error handling near an await: (1) find the setState or callback, (2) trace what renders or fires as a result, (3) ask "if this fires after the user navigated away, what do they see?" If the answer is "nothing" (a ref update, a console.log), it's P3. If the answer is "a dialog opens" or "state corrupts," upgrade. The severity depends on what's at the END of the async chain, not the start.
 - **Mechanism vs. consequence.** Reviewers describe findings using mechanism vocabulary ("unused parameter", "duplicated code", "test passes by coincidence"), not consequence vocabulary ("dialog opens in wrong view", "attacker can bypass check", "removing this code has no test to catch it"). The Contract Auditor and Structural Analyst tend to frame findings by consequence already — use their framing directly. For mechanism-framed findings from other reviewers, restate the consequence before accepting the severity. Consequences include UX bugs, security gaps, data corruption, and silent regressions — not just things users see on screen.
 - **Weak evidence.** Findings that assert a problem without demonstrating it. Downgrade or drop.
-- **Unnecessary novelty.** New files, new naming patterns, new abstractions where the existing codebase already has a convention. If no reviewer flagged it but you see it, add it.
+- **Unnecessary novelty.** New files, new naming patterns, new abstractions where the existing codebase already has a convention. If no reviewer flagged it but you see it, add it. If a reviewer flagged it as an observation, evaluate whether it should be a finding.
 - **Scope creep.** Suggestions that go beyond reviewing what changed into redesigning what exists. Downgrade to P4.
 - **Structural alternatives.** One reviewer proposes a design that eliminates a documented tradeoff, while others have zero findings because the current approach "works." Don't discount this as an outlier or scope creep. A structural alternative that removes the need for a tradeoff can be the highest-value output of the review. Preserve it at its original severity — the author decides whether to adopt it, but they need enough signal to evaluate it.
 - **Pre-existing behavior.** "Pre-existing" doesn't erase severity. Check whether the PR introduced new code (comments, branches, error messages) that describes or depends on the pre-existing behavior incorrectly. The new code is in scope even when the underlying behavior isn't.
 
-For each finding, apply the severity test in **both directions**:
+For each finding **and observation**, apply the severity test in **both directions**. Observations are not exempt — a reviewer may underrate a convention violation or a missing guarantee as Obs when the consequence warrants P3+:
 
 - Downgrade: "Is this actually less severe than stated?"
 - Upgrade: "Could this be worse than stated?"
@@ -241,7 +241,7 @@ When reviewing a GitHub PR, post findings as a proper GitHub review with inline
 
 **Review body.** Open with a short, friendly summary: what the change does well, what the overall impression is, and how many findings follow. Call out good work when you see it. A review that only lists problems teaches authors to dread your comments.
 
-```
+```text
 Clean approach to X. The Y handling is particularly well done.
 
 A couple things to look at: 1 P2, 1 P3, 3 nits across 5 inline
@@ -250,7 +250,7 @@ comments.
 
 For re-reviews (round 2+), open with what was addressed:
 
-```
+```text
 Thanks for fixing the wire-format break and the naming issue.
 
 Fresh review found one new issue: 1 P2 across 1 inline comment.
@@ -262,7 +262,7 @@ Keep the review body to 2–4 sentences. Don't use markdown headers in the body
 
 Inline comment format:
 
-```
+```text
 **P{n}** One-sentence finding *(Reviewer Role)*
 
 > Reviewer's evidence quoted verbatim from their file
@@ -274,7 +274,7 @@ reasoning, fix suggestions — these are your words.
 
 For convergent findings (multiple reviewers, same issue):
 
-```
+```text
 **P{n}** One-sentence finding *(Performance Analyst P1,
 Contract Auditor P1, Test Auditor P2)*
 
@@ -319,20 +319,20 @@ Where `review.json`:
 
 ```json
 {
-	"event": "COMMENT",
-	"body": "Summary of what's good and what to look at.\n1 P2, 1 P3 across 2 inline comments.",
-	"comments": [
-		{
-			"path": "file.go",
-			"position": 42,
-			"body": "**P1** Finding... *(Reviewer Role)*\n\n> Evidence..."
-		},
-		{
-			"path": "other.go",
-			"position": 1,
-			"body": "**P2** Cross-file finding... *(Reviewer Role)*\n\n> Evidence..."
-		}
-	]
+    "event": "COMMENT",
+    "body": "Summary of what's good and what to look at.\n1 P2, 1 P3 across 2 inline comments.",
+    "comments": [
+        {
+            "path": "file.go",
+            "position": 42,
+            "body": "**P1** Finding... *(Reviewer Role)*\n\n> Evidence..."
+        },
+        {
+            "path": "other.go",
+            "position": 1,
+            "body": "**P2** Cross-file finding... *(Reviewer Role)*\n\n> Evidence..."
+        }
+    ]
 }
 ```
 
PATCH

echo "Gold patch applied."
