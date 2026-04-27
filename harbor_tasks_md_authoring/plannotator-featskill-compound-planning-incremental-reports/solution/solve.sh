#!/usr/bin/env bash
set -euo pipefail

cd /workspace/plannotator

# Idempotency guard
if grep -qF "- Subsequent reports: `compound-planning-report-v2.html`, `compound-planning-rep" "apps/skills/plannotator-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/apps/skills/plannotator-compound/SKILL.md b/apps/skills/plannotator-compound/SKILL.md
@@ -10,38 +10,96 @@ description: >
 # Compound Planning Analysis
 
 You are conducting a comprehensive research analysis of a user's Plannotator plan
-archive. The goal: extract patterns from their denied plans and annotations, reduce
+archive. The goal: extract patterns from their denied plans, reduce
 them into actionable insights, and produce an elegant HTML dashboard report.
 
 This is a multi-phase process. Each phase must complete fully before the next begins.
 Research integrity is paramount — every file must be read, no skipping.
 
-## Phase 0: Locate the Plans Directory
+## Phase 0: Locate Plans & Check for Previous Reports
 
 Check for `~/.plannotator/plans/`. If it exists and contains `.md` files, proceed.
 
 If not found, ask the user:
 > "I couldn't find plans at ~/.plannotator/plans/. Where is your plans directory?"
 
-Once you have the path, verify it contains files matching `*-denied.md` and/or
-`*.annotations.md`. If neither exist, inform the user there's no denial/annotation
-data to analyze and stop.
+Once you have the path, verify it contains files matching `*-denied.md`. If none
+exist, inform the user there's no denial data to analyze and stop.
+
+### Previous Report Detection
+
+After locating the plans directory, check for existing reports:
+
+```
+ls ~/.plannotator/plans/compound-planning-report*.html
+```
+
+Reports follow a versioned naming scheme:
+- First report: `compound-planning-report.html`
+- Subsequent reports: `compound-planning-report-v2.html`, `compound-planning-report-v3.html`, etc.
+
+If one or more reports exist, determine the **latest** one (highest version number).
+Get its filesystem modification date using `stat` (macOS: `stat -f %Sm -t %Y-%m-%d`,
+Linux: `stat -c %y | cut -d' ' -f1`). This is the **cutoff date**.
+
+Present the user with a choice:
+
+> "I found a previous report (`compound-planning-report-v{N}.html`) last updated
+> on {CUTOFF_DATE}. I can either:
+>
+> 1. **Incremental** — Only analyze files dated after {CUTOFF_DATE}, saving tokens
+>    and building on previous findings
+> 2. **Full** — Re-analyze the entire archive from scratch
+>
+> Which would you prefer?"
+
+Wait for the user's response before proceeding.
+
+**If incremental:** Filter all subsequent phases to only process files with dates
+after the cutoff date. The new report version will note in its header narrative that
+it covers the period from {CUTOFF_DATE} to present, and reference the previous
+report for earlier findings. The inventory (Phase 1) should still count ALL files
+for overall stats, but clearly separate "new since last report" counts.
+
+**If full:** Proceed normally with all files, but still use the next version number
+for the output filename.
+
+**If no previous report exists:** Proceed normally. The output filename will be
+`compound-planning-report.html` (no version suffix for the first report).
 
 ## Phase 1: Inventory
 
-Count and report the dataset:
+Count and report the dataset. **Always count ALL files** for overall stats,
+regardless of whether this is an incremental or full run:
 
 ```
 - *-approved.md files (count)
 - *-denied.md files (count)
-- *.annotations.md files (count)
-- *.diff.md files (count)
 - Date range (earliest to latest date found in filenames)
 - Total days spanned
 - Revision rate: denied / (approved + denied) — this is the "X% of plans
   revised before coding" stat used in dashboard section 1
 ```
 
+**Note:** Ignore `*.annotations.md` files entirely. Denied files already contain
+the full plan text plus all reviewer feedback appended after a `---` separator.
+Annotation files are redundant subsets of this content — reading both would
+double-count feedback.
+
+**If incremental mode:** After the total counts, separately report the counts for
+files dated after the cutoff date only:
+
+```
+New since {CUTOFF_DATE}:
+- *-denied.md files: X (of Y total)
+- New date range: {CUTOFF_DATE} to {LATEST_DATE}
+- New days spanned: N
+```
+
+If fewer than 3 new denied files exist since the cutoff, warn the user:
+> "Only {N} new denied plans since the last report. The incremental analysis may
+> be thin. Would you like to proceed or switch to a full analysis?"
+
 Also run `wc -l` across all `*-approved.md` files to get average lines per
 approved plan. This tells the user whether their plans are staying lightweight
 or bloating over time. You do not need to read approved plan contents — just
@@ -56,31 +114,43 @@ Tell the user what you found and that you're beginning the extraction.
 
 ## Phase 2: Map — Parallel Extraction
 
-This is the most time-intensive phase. You must read EVERY denied plan and EVERY
-annotation file. Do not skip files. Do not summarize early.
+This is the most time-intensive phase. You must read EVERY `*-denied.md` file
+**in scope**. Do not skip files. Do not summarize early.
 
-**Important:** Do NOT read approved plan files. They are counted in the inventory
-for context (total volume, approval rate) but are not analyzed for feedback
-patterns. Only `*-denied.md` and `*.annotations.md` files contain the feedback
-data this analysis needs.
+**In scope** means: all denied files if running a full analysis, or only denied
+files dated after the cutoff date if running incrementally. In incremental mode,
+only process files whose embedded YYYY-MM-DD date is strictly after the cutoff.
+
+**Important:** Only read `*-denied.md` files. Do NOT read approved plans,
+annotation files, or diff files. Each denied file contains the full plan text
+followed by a `---` separator and the reviewer's feedback — everything needed
+for analysis is in one file.
 
 ### Batching Strategy
 
+All extraction agents should use `model: "haiku"` — they're doing straightforward
+file reading and structured extraction, not reasoning. Haiku is faster and cheaper
+for this work.
+
 The approach depends on dataset size:
 
-**Small datasets (< 40 total files):** Read all files directly — no need for
-parallel agents. Just read them sequentially and proceed to Phase 3.
+**Tiny datasets (≤ 10 total files):** Read all files directly in the main agent —
+no need for sub-agents. Just read them sequentially and proceed to Phase 3.
 
-**Medium datasets (40-120 files):** Split into 2-4 parallel agents by file type
-and/or time period.
+**Small datasets (11-30 files):** Launch 2-3 parallel Haiku agents, splitting
+files roughly evenly.
 
-**Large datasets (120+ files):** Split into batches of ~40-60 files per agent.
-Split by the natural time boundaries in the data (months, quarters, or whatever
-groupings produce balanced batches). If one time period dominates (e.g., the most
-recent month has 3x the files), split that period into two batches.
+**Medium datasets (31-80 files):** Launch 4-6 parallel Haiku agents (~10-15 files
+each). Split by file type and/or time period.
+
+**Large datasets (80+ files):** Launch as many parallel Haiku agents as needed to
+keep each batch around 10-15 files. Split by the natural time boundaries in the
+data (months, quarters, or whatever groupings produce balanced batches). If one
+time period dominates (e.g., the most recent month has 3x the files), split that
+period into multiple batches.
 
 Launch all extraction agents in parallel using the Agent tool with
-`run_in_background: true`.
+`run_in_background: true` and `model: "haiku"`.
 
 ### Output Files
 
@@ -95,30 +165,36 @@ logs that are difficult to parse). Instruct each agent to write to:
 Create the `/tmp/compound-planning/` directory before launching agents. The
 reduce agent in Phase 3 will read these clean files directly.
 
-### Extraction Prompt for Denied Plans
+### Extraction Prompt
 
-Each agent for denied plans receives this instruction (adapt the time period,
-file glob, and output path):
+Each agent receives this instruction (adapt the time period, file list, and
+output path):
 
 ```
 You are extracting structured data from denied plan files for a pattern analysis.
 
 Directory: [PLANS DIRECTORY]
-Files to read: All *-denied.md files with dates in [TIME PERIOD]
+Files to read: [LIST OF SPECIFIC *-denied.md FILES]
 Output: Write your complete results to [OUTPUT FILE PATH]
 
-Read EVERY matching file. For EACH file, extract:
-- The plan name/topic
-- The denial reason or feedback given (look for reviewer comments, annotations,
-  revision requests — capture the actual words used)
+Each denied file contains two parts separated by a --- line:
+1. The plan text (above the ---)
+2. The reviewer's feedback and annotations (below the ---)
+
+Read EVERY file in your list. For EACH file, extract:
+- The plan name/topic (from the plan text above the ---)
+- The denial reason or feedback given (from below the --- — capture the actual
+  words used)
 - What was specifically asked to change
 - The type of feedback (let the content determine the category — don't force-fit
   into predefined types. Common types include things like: scope concerns,
   approach disagreements, missing information, process requirements, quality
   concerns, UX/design issues, naming disputes, clarification requests,
   testing/procedural denials — but the user's actual patterns may differ)
 - Any specific phrases or recurring language from the reviewer
-- The date
+- Individual annotations if present (numbered feedback items with quoted text
+  and reviewer comments)
+- The date (extracted from the filename)
 
 Do NOT skip any files. One entry per file.
 
@@ -130,43 +206,7 @@ Format each entry as:
 - Feedback type: ...
 - Specific asks: ...
 - Notable phrases: ...
----
-
-After processing all files, write the complete results to [OUTPUT FILE PATH].
-State the total file count at the end of the file.
-```
-
-### Extraction Prompt for Annotation Files
-
-Annotation files have a different structure — they contain inline comments,
-highlights, and feedback left on specific sections of plans. Each agent for
-annotations receives this instruction:
-
-```
-You are extracting structured data from annotation files for a pattern analysis.
-
-Directory: [PLANS DIRECTORY]
-Files to read: All *.annotations.md files with dates in [TIME PERIOD]
-Output: Write your complete results to [OUTPUT FILE PATH]
-
-Read EVERY matching file. For EACH file, extract:
-- The plan name/topic it annotates
-- Every individual annotation/comment made (there may be multiple per file)
-- For each annotation: the quoted text, what type of feedback it is (correction,
-  scope concern, design preference, structural request, question, praise,
-  process directive, etc.), and what section of the plan was annotated
-- The overall tone of the feedback
-
-Do NOT skip any files. One entry per file.
-
-Format each entry as:
-**[filename]**
-- Plan topic: ...
-- Annotations found: [count]
-- Annotation 1: "[quote or paraphrase]" — Type: ... — Section: ...
-- Annotation 2: "[quote or paraphrase]" — Type: ... — Section: ...
-- (continue for all annotations in the file)
-- Overall tone: ...
+- Annotations: [count, with brief summary of each]
 ---
 
 After processing all files, write the complete results to [OUTPUT FILE PATH].
@@ -185,28 +225,49 @@ file to see how far it got before timing out.
 
 ## Phase 3: Reduce — Pattern Analysis
 
-Once ALL extraction agents have completed (or all files have been read for small
-datasets), launch a single reduction agent.
+Once ALL extraction agents have completed (or all files have been read for tiny
+datasets), proceed with the reduction. Reduction agents should use `model: "sonnet"`
+— this phase requires real analytical reasoning, not just file reading.
+
+### Reduction Strategy
+
+The approach depends on how many extraction files were produced:
+
+**Standard (≤ 20 extraction files):** Launch a single Sonnet agent to read all
+extraction files and produce the full analysis. This covers most datasets.
+
+**Large (21+ extraction files):** Use a two-stage reduce:
 
-The reduction agent reads the clean extraction files from `/tmp/compound-planning/`
-(not the agent task output files, which contain noisy JSONL framework logs). It
-processes all extraction files together and produces the comprehensive analysis.
+1. **Stage 1 — Partial reduces:** Split the extraction files into groups of 4-6.
+   Launch parallel Sonnet agents, each reading one group and producing a partial
+   analysis with the same sections listed below. Each writes to
+   `/tmp/compound-planning/partial-reduce-{N}.md`.
 
-Give the reduction agent this prompt (adapt the file paths):
+2. **Stage 2 — Final reduce:** A single Sonnet agent reads all partial reduce
+   files and synthesizes them into the final comprehensive analysis. This agent
+   merges taxonomies, combines counts, deduplicates patterns, and reconciles any
+   conflicting categorizations across partials.
+
+### Reduction Prompt
+
+Give each reduction agent this prompt (adapt file paths for single vs multi-stage):
 
 ```
 You are a data scientist conducting the reduction phase of a map-reduce analysis
-across a user's plan denial and annotation archive.
+across a user's denied plan archive.
 
-Read ALL extraction files at /tmp/compound-planning/extraction-*.md
+Read ALL extraction files at [FILE PATHS]
 
-These files contain structured extractions from every denied plan and annotation
-file. Your job: aggregate everything, find patterns, cluster into a taxonomy,
+These files contain structured extractions from every denied plan file. Each
+extraction includes the plan topic, denial feedback, annotations, and reviewer
+language. Your job: aggregate everything, find patterns, cluster into a taxonomy,
 and produce a comprehensive analysis.
 
 Be exhaustive. Use real counts. Quote real phrases from the data. This is
 research — no hand-waving, no fabrication.
 
+Write your complete results to [OUTPUT FILE PATH].
+
 Produce the following sections:
 [... sections listed below ...]
 ```
@@ -262,7 +323,21 @@ vs total denials). Report this percentage — it will be different for every use
 ## Phase 4: Generate the HTML Dashboard
 
 Build a single, self-contained HTML file as the final deliverable. Save it to
-the user's plans directory as `compound-planning-report.html`.
+the user's plans directory with a versioned filename:
+
+- First ever report: `compound-planning-report.html`
+- Second report: `compound-planning-report-v2.html`
+- Third report: `compound-planning-report-v3.html`
+- And so on.
+
+The version number was determined in Phase 0 based on existing reports found.
+
+**If this is an incremental report**, the header should indicate the analysis
+period (e.g., "March 15 – March 31, 2026") and include a subtitle noting
+"Incremental analysis — see v{N-1} for earlier findings." The narrative in
+section 1 should frame findings as what's new or changed since the last report,
+not as a complete picture. Overall stats in the header (file counts, revision
+rate) should still reflect the full archive for context.
 
 Read the template at `assets/report-template.html` for the **design language
 only**. The template contains example data from a previous analysis — ignore all
@@ -287,12 +362,12 @@ Before the 7 sections, the page has:
 
 - **Header:** Report title on the left (Playfair Display, ~36px), project name +
   date range below it in light meta text. On the right: file counts in mono
-  (e.g., "202 denials · 168 annotations · 71 days"). Separated from content by
+  (e.g., "223 denials · 71 days"). Separated from content by
   a bottom border. Generous bottom padding before section 1.
 
 - **Footer:** After section 7. Top border, centered italic Playfair Display tagline
-  summarizing the corpus (e.g., "Analysis of X denied plans and Y annotation files
-  from the Plannotator archive.").
+  summarizing the corpus (e.g., "Analysis of X denied plans from the Plannotator
+  archive.").
 
 ### Dashboard Section Order (7 sections)
 
@@ -350,8 +425,8 @@ one — the flow moves from "what happened" through "why" to "what to do about i
 ### Adaptation Rules
 
 - If the user has < 3 months of data, reduce the evolution section to fewer cards
-- If the user has no annotation files (only denials), note this in the narrative
-  and skip annotation-specific insights
+- If most denied files lack feedback below the `---` (bare denials with no
+  annotations), note this in the narrative — the analysis will be thinner
 - If fewer than 5 denial categories emerge, combine the taxonomy and patterns
   sections into one
 - If the dataset is very small (< 20 files), the narrative should acknowledge the
@@ -374,11 +449,64 @@ After generating, open the file in the user's browser.
 ## Phase 5: Summary
 
 Tell the user:
-- How many total files were analyzed (denials + annotations)
+- How many denied files were analyzed
+- If incremental: how many were new since the last report
 - The top 3 denial patterns found
 - The estimated percentage of denials the prompt instructions would address
 - The single most impactful prompt improvement
-- Where the report was saved
+- Where the report was saved (including version number)
+- If incremental: remind the user that earlier findings are in the previous report
+
+## Phase 6: Improvement Hook
+
+After presenting the summary, ask the user if they want to enable an **improvement
+hook** — this takes the corrective prompt instructions from section 7 of the report
+and writes them to a file that Plannotator's `EnterPlanMode` hook can inject into
+every future planning session automatically.
+
+> "Would you like to enable the improvement hook? This will save the corrective
+> prompt instructions to a file that gets automatically injected into all future
+> planning sessions — so Claude sees your feedback patterns before writing any plan."
+
+**If yes:**
+
+The hook file lives at:
+
+```
+~/.plannotator/compound/enterplanmode-improve-hook.txt
+```
+
+Create the `~/.plannotator/compound/` directory if it doesn't exist.
+
+The file contents should be the corrective prompt instructions from Phase 3 —
+the same numbered list that appears in section 7 of the HTML report. Write them
+as plain text, one instruction per line, prefixed with their number. No HTML, no
+markdown fences, no preamble — just the instructions themselves. The hook system
+will inject this file's contents as-is into the planning context.
+
+**If the file already exists:**
+
+Read the existing file and present the user with a choice:
+
+> "An improvement hook already exists from a previous analysis. I can:
+>
+> 1. **Replace** — Overwrite with the new instructions (the old ones are gone)
+> 2. **Merge** — Combine both, deduplicating overlapping instructions and
+>    keeping the best version of each
+> 3. **Keep existing** — Leave the current hook as-is, skip this step
+>
+> Which would you prefer?"
+
+- **Replace:** Overwrite the file with the new instructions.
+- **Merge:** Read the existing instructions, compare with the new ones, and
+  produce a merged set. Remove duplicates (same intent even if worded differently).
+  When two instructions cover the same pattern, keep the more specific or
+  actionable version. Re-number the final list sequentially. Write the merged
+  result to the file. Show the user what changed (added N new, removed N
+  redundant, kept N existing).
+- **Keep existing:** Do nothing, move on.
+
+**If no:** Skip this phase entirely.
 
 ## Important Notes
 
PATCH

echo "Gold patch applied."
