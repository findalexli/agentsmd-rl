#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skillpack

# Idempotency guard
if grep -qF "- If the task is still too broad, narrow the scope instead of writing a vague me" "skills/skillpack-creator/SKILL.md" && grep -qF "The `description` is the primary triggering mechanism \u2014 make it concrete with bo" "templates/builtin-skills/skill-creator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/skillpack-creator/SKILL.md b/skills/skillpack-creator/SKILL.md
@@ -13,99 +13,84 @@ Turn a successful task into a reusable SkillPack. Extract the stable workflow, d
 
 ### 1. Normalize the source task
 
-Start by reducing the finished task into a clean execution spec:
+Reduce the finished task into a clean execution spec:
 
-- Capture the user goal and the concrete deliverable.
-- Capture the final successful workflow, not the full exploratory transcript.
+- Capture the user goal, concrete deliverable, and the final successful workflow (not the full exploratory transcript).
 - List required skills, tools, files, secrets, and environment assumptions.
-- Separate deterministic steps from heuristic steps.
-- Remove dead ends, retries, and one-off debugging noise.
+- Separate deterministic steps from heuristic steps; remove dead ends and debugging noise.
+- If the task is still too broad, narrow the scope instead of writing a vague mega-skill. If key success conditions depend on hidden human judgment, mark the pack as a best-effort assistant workflow.
 
-If the prior work is still ambiguous, ask for the missing stable facts or infer only the pieces that are low risk.
+Ask for missing stable facts or infer only the low-risk pieces.
 
 ### 2. Decide what the pack should contain
 
-Use this split:
-
-- Put reusable procedural knowledge in a local skill under the target pack's `skills/`.
-- Put repeated shell or file-generation logic into scripts inside that local skill when reliability matters.
-- Put detailed schemas, API notes, or conventions into reference files.
-- Put 1 to 3 pack-level prompts in `skillpack.json` as the pack's user-facing entry points.
-
-Do not treat `prompts` as a strict workflow engine. In this codebase they are starter inputs for the UI, not a DAG or state machine. Read `references/skillpack-format.md` when you need the exact pack semantics.
+- **Local skill** (`skills/`): reusable procedural knowledge. Keep scripts minimal unless reproducibility depends on exact file generation or repetitive shell steps.
+- **Scripts** (`scripts/`): repeated shell or file-generation logic where reliability matters.
+- **References** (`references/`): detailed schemas, API notes, or conventions that should not bloat `SKILL.md`.
+- **Prompts** (`skillpack.json`): 1–3 pack-level starter inputs for the UI — not a DAG or state machine. See `references/skillpack-format.md` for exact pack semantics.
 
 ### 3. Create the pack specification
 
-Before writing files, define:
-
-- Pack name
-- Pack description
-- Preset prompts
-- Skill list with `name`, `source`, and `description`
-- Which skill is the new local orchestrator skill
-- Expected output files and success criteria
-
-Prefer one local orchestrator skill plus a small number of external skills. Keep the pack narrow and job-focused.
+Before writing files, define the pack spec. Prefer one local orchestrator skill plus a small number of external skills. Example minimal manifest:
+
+```json
+{
+  "name": "company-research",
+  "description": "Research a company and produce a summary report",
+  "version": "1.0.0",
+  "prompts": ["Research {company} and create a report with financials and competitors"],
+  "skills": [
+    { "name": "research-orchestrator", "source": "./skills/research-orchestrator", "description": "Orchestrate company research across multiple sources" }
+  ]
+}
+```
 
 ### 4. Create the local orchestrator skill
 
-In the target pack:
+Create `skills/<skill-name>/SKILL.md` with frontmatter and imperative workflow instructions:
 
-- Create `skills/<skill-name>/SKILL.md`.
-- Write frontmatter that clearly describes what the local skill does and when it should trigger.
-- Move the stable workflow into imperative instructions.
-- Add `scripts/` only for fragile or repeated operations.
-- Add `references/` only for detailed information that should not bloat `SKILL.md`.
+```yaml
+---
+name: research-orchestrator
+description: "Orchestrate multi-source company research. Use when the user wants a structured company report covering financials, competitors, and market position."
+---
+```
 
-If the workflow is mostly instructions, keep the local skill simple. If reproducibility depends on exact file generation, add scripts.
+- Write the stable workflow as imperative steps in the body.
+- Add `scripts/` only for fragile or repeated operations; add `references/` only for detailed information.
 
 ### 5. Materialize the pack
 
-Use `scripts/scaffold_skillpack.py` in this skill when you already know the pack spec. It will:
-
-- validate a JSON manifest shaped like `skillpack.json`
-- write `skillpack.json`
-- create `skills/`
-- copy `start.sh` and `start.bat` from this repository's `templates/`
-- optionally run `npx -y @cremini/skillpack zip`
-
-Typical usage:
+Use `scripts/scaffold_skillpack.py` when you have the pack spec:
 
 ```bash
+# Basic
 python3 skills/skillpack-creator/scripts/scaffold_skillpack.py \
   --manifest /tmp/skillpack.json \
   --output /absolute/path/to/output-pack
-```
-
-With zip generation:
 
-```bash
+# With zip
 python3 skills/skillpack-creator/scripts/scaffold_skillpack.py \
   --manifest /tmp/skillpack.json \
   --output /absolute/path/to/output-pack \
   --zip
 ```
 
-### 6. Validate the result
-
-Before handing the pack back:
+The script validates the manifest, writes `skillpack.json`, creates `skills/`, copies `start.sh`/`start.bat` from `templates/`, and optionally runs `npx -y @cremini/skillpack zip`.
 
-- Confirm the manifest matches the intended pack scope.
-- Confirm every declared skill has a valid `name`, `source`, and `description`.
-- Confirm local skills are present under the target pack's `skills/`.
-- Confirm the starter prompts are concrete enough to reproduce the workflow.
-- Zip only after the pack can already run as a directory.
+### 6. Validate the result
 
-## Decision Rules
+Before handing the pack back, confirm:
 
-- If the reusable value is mostly workflow knowledge, create a local skill and keep scripts minimal.
-- If the task depends on exact file emission or repetitive shell steps, script those parts.
-- If the task is still too broad, split it into a narrower pack instead of writing a vague mega-skill.
-- If key success conditions depend on hidden human judgment, state that the pack is a best-effort assistant workflow, not a deterministic pipeline.
+- The manifest matches the intended pack scope
+- Every declared skill has a valid `name`, `source`, and `description`
+- Local skills are present under the target pack's `skills/`
+- Starter prompts are concrete enough to reproduce the workflow
+- Zip only after the pack runs as a directory
 
 ## Output Standard
 
-When you use this skill, produce:
+Produce:
 
 1. A short summary of the stabilized workflow.
 2. The target pack structure and skill inventory.
diff --git a/templates/builtin-skills/skill-creator/SKILL.md b/templates/builtin-skills/skill-creator/SKILL.md
@@ -5,106 +5,55 @@ description: Create new skills, modify and improve existing skills, and measure
 
 # Skill Creator
 
-A skill for creating new skills and iteratively improving them inside this SkillPack.
-
-At a high level, the process of creating a skill goes like this:
-
-- Decide what the skill should do and when it should trigger.
-- Write a draft of the skill.
-- Create a few realistic test prompts.
-- Run the tests, review the results with the user, and improve the skill.
-- Repeat until the skill is good enough for the user's needs.
-
-Your job when using this skill is to figure out where the user is in this process and help them move forward without overcomplicating things.
-
-## Communicating with the user
-
-Adjust your language to the user's level of familiarity. Avoid unnecessary jargon. Briefly explain terms like "frontmatter", "assertion", or "benchmark" if the user does not appear comfortable with them.
-
-If the user clearly wants a lightweight collaboration rather than a full evaluation loop, keep things simple and iterate directly with them.
+Create new skills and iteratively improve them inside this SkillPack. Determine where the user is in the create → draft → test → improve cycle and help them move forward.
 
 ## Pack-specific rules
 
-This SkillPack uses a fixed project-level skills directory and config file:
-
-- Skills directory: `{{SKILLS_PATH}}`
-- SkillPack config: `{{PACK_CONFIG_PATH}}`
-
-These paths override any generic advice you may know from other environments.
-
-When creating or updating skills in this SkillPack:
-
-- Always place the skill under `{{SKILLS_PATH}}/<skill-name>/`.
-- Always write the main skill file to `{{SKILLS_PATH}}/<skill-name>/SKILL.md`.
-- Treat `skill-name` as the canonical directory name unless the user explicitly asks to preserve an existing directory layout.
-- Never create new skills inside the current workspace directory just because the active cwd is elsewhere.
+All skills live under `{{SKILLS_PATH}}/<skill-name>/SKILL.md` and config is at `{{PACK_CONFIG_PATH}}`. These paths override any generic advice. Never create skills in the current workspace directory — always use `{{SKILLS_PATH}}`.
 
 ## Creating a skill
 
 ### Capture intent
 
-Start by understanding the user's intent. The current conversation may already contain the workflow the user wants to capture. Extract answers from the conversation first, then fill the gaps with targeted questions.
-
-Confirm these points before writing the first draft:
+Extract answers from the current conversation first, then fill gaps with targeted questions. Confirm before writing the first draft:
 
 1. What should this skill enable the model to do?
 2. When should this skill trigger?
 3. What output should it produce?
 4. Does the user want a lightweight draft, or a tested and iterated skill?
 
-### Interview and research
-
-Ask about:
-
-- edge cases
-- input/output formats
-- example prompts or files
-- success criteria
-- dependencies or required tools
-
-Wait to write test prompts until these basics are clear enough.
+Clarify edge cases, input/output formats, success criteria, and dependencies as needed before writing test prompts.
 
 ### Write the skill
 
-Create the skill directory at `{{SKILLS_PATH}}/<skill-name>/`.
-
-Create `SKILL.md` with YAML frontmatter. The frontmatter must include:
-
-- `name`
-- `description`
+Create the skill at `{{SKILLS_PATH}}/<skill-name>/SKILL.md`. Example template:
 
-The `description` is the primary triggering mechanism. Make it concrete and slightly "pushy": include both what the skill does and the situations where it should be used.
+```yaml
+---
+name: example-skill
+description: "Analyze competitor pricing pages and generate a comparison matrix. Use when the user wants to benchmark pricing tiers, feature gaps, or positioning against specific competitors."
+---
 
-Keep the skill practical:
+# Example Skill
 
-- Put "when to use" information in the `description`, not buried in the body.
-- Keep the body focused on the workflow, decisions, and output expectations.
-- If the skill needs deterministic helpers, place them under `scripts/`.
-- If the skill needs long reference material, place it under `references/` and tell the model when to read it.
+## Workflow
 
-### Required save location
+1. Collect the target URLs from the user.
+2. Extract pricing tiers, features, and limits from each page.
+3. Generate a comparison matrix as a markdown table.
 
-For a newly created skill named `example-skill`, the target layout must be:
+## Output
 
-```text
-{{SKILLS_PATH}}/example-skill/
-{{SKILLS_PATH}}/example-skill/SKILL.md
+Return a markdown table with one column per competitor and one row per feature.
 ```
 
-If the user is improving an existing skill, preserve the existing skill name unless they explicitly request a rename.
-
-### Update skillpack.json
+The `description` is the primary triggering mechanism — make it concrete with both what the skill does and when to use it. Keep the body focused on workflow, decisions, and output expectations. Place deterministic helpers under `scripts/` and long reference material under `references/`.
 
-After you create or update a skill, you must sync `{{PACK_CONFIG_PATH}}`.
+Preserve the existing skill name when improving unless the user explicitly requests a rename.
 
-Do not guess the metadata from memory. Instead:
+### Sync skillpack.json
 
-1. Read the final `SKILL.md`.
-2. Parse the YAML frontmatter.
-3. Extract:
-   - `name`
-   - `description`
-4. Upsert an entry into the `skills` array in `{{PACK_CONFIG_PATH}}`:
+After creating or updating a skill, sync `{{PACK_CONFIG_PATH}}`. Read the final `SKILL.md`, parse the YAML frontmatter, and upsert into the `skills` array:
 
 ```json
 {
@@ -114,40 +63,17 @@ Do not guess the metadata from memory. Instead:
 }
 ```
 
-Rules for this update:
-
-- `name` must come from `frontmatter.name`.
-- `description` must come from `frontmatter.description`.
-- `source` must be `./skills/<frontmatter.name>`.
-- If an entry for the same skill already exists, update it instead of creating a duplicate.
+All three fields must come from frontmatter — do not guess from memory. Update existing entries instead of creating duplicates.
 
 ### Writing guide
 
-Prefer imperative, clear instructions. Explain why important constraints exist. Avoid overly rigid language unless strict behavior is actually required.
-
-Useful structure:
-
-- purpose
-- trigger guidance
-- required inputs
-- step-by-step workflow
-- output format
-- edge cases
-
-If the skill supports multiple domains or frameworks, organize the references by variant and tell the model how to choose the right one.
+Prefer imperative instructions. Structure skills as: purpose, trigger guidance, required inputs, step-by-step workflow, output format, edge cases. For multi-domain skills, organize references by variant and tell the model how to choose.
 
 ## Test and iterate
 
-After drafting the skill, propose 2-3 realistic test prompts. The prompts should sound like something a real user would actually say.
-
-If the user wants evaluation:
-
-- run the test prompts with the skill
-- compare the outputs against the user's expectations
-- note what worked and what failed
-- revise the skill
+After drafting the skill, propose 2–3 realistic test prompts phrased as a real user would.
 
-If the user does not want a heavy evaluation loop, do at least a lightweight sanity check before calling the skill complete.
+If the user wants evaluation, run the prompts, compare outputs against expectations, note failures, and revise. Otherwise, do at least a lightweight sanity check before calling the skill complete.
 
 ## Improving an existing skill
 
PATCH

echo "Gold patch applied."
