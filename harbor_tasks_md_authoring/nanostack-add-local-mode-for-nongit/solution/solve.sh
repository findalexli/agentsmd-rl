#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "**Local mode:** Run `source bin/lib/git-context.sh && detect_git_mode`. If resul" "plan/SKILL.md" && grep -qF "- **Language:** replace all jargon with plain terms. \"Revis\u00e9 N archivos. Encontr" "review/SKILL.md" && grep -qF "- HTML \u2192 run `open index.html` (or the main HTML file) so the user sees it insta" "ship/SKILL.md" && grep -qF "**Local mode language:** Run `source bin/lib/git-context.sh && detect_git_mode`." "think/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plan/SKILL.md b/plan/SKILL.md
@@ -27,7 +27,7 @@ If the output shows `"active":false`, create a session:
 
 Then run `session.sh phase-start plan`.
 
-**Local mode:** Run `source bin/lib/git-context.sh && detect_git_mode`. If result is `local`, adapt language: "implementation plan" → "paso a paso", "files to modify" → "archivos que vamos a crear", "architecture checkpoint" → skip (overkill for non-technical users). Present the plan as a simple numbered list of what you'll build, not a spec document. Same rigor, accessible words.
+**Local mode:** Run `source bin/lib/git-context.sh && detect_git_mode`. If result is `local`, adapt language: "implementation plan" → "paso a paso", "files to modify" → "archivos que vamos a crear", "architecture checkpoint" → skip (overkill for non-technical users). Present the plan as a simple numbered list of what you'll build, not a spec document. Same rigor, accessible words. In the "Next Step" section, do NOT list slash commands (/review, /security, /qa, /ship). Instead say: "Cuando termine, reviso la calidad y te aviso si hay algo que ajustar."
 
 ## Process
 
diff --git a/review/SKILL.md b/review/SKILL.md
@@ -39,7 +39,8 @@ Calibrate depth by diff size: **Small** (< 100 lines, quick pass) / **Medium** (
 Run `source bin/lib/git-context.sh && detect_git_mode`. If `local` (no git):
 - **File source:** use `context_checkpoint.key_files` from the plan artifact instead of git diff. If no plan artifact, list files in the project directory.
 - **Skip:** scope drift check (no diff to compare), PR preview.
-- **Language:** replace "diff", "branch", "PR" with plain terms. "Revisé N archivos. Encontré X cosas:" instead of "Diff: N files, X findings." Explain each finding in plain language — what's wrong, why it matters, and whether you can fix it.
+- **Language:** replace all jargon with plain terms. "Revisé N archivos. Encontré X cosas:" instead of "Diff: N files, X findings." Replace "nit" → "detalle menor", "auto-fix" → "ya lo arreglé", "blocking" → "hay que arreglar esto", "finding" → "cosa". Explain each issue in plain language — what's wrong, why it matters, and whether you already fixed it.
+- **Next steps:** do NOT list slash commands. Instead: "¿Querés que revise la seguridad antes de darlo por terminado?"
 - **Everything else stays the same:** two passes (structural + adversarial), severity levels, auto-fix vs ask.
 
 ## Step 0: Read Plan Context and Past Solutions
diff --git a/ship/SKILL.md b/ship/SKILL.md
@@ -22,14 +22,14 @@ Run `source bin/lib/git-context.sh && detect_git_mode`.
 **If `local` (no git repo):** Skip the entire PR/CI/deploy flow below. Instead:
 1. Run `ship/bin/quality-check.sh` (already works without git).
 2. Verify files from the plan exist and are non-empty.
-3. Detect project type and show how to use the result:
-   - HTML → "Abrí index.html en tu navegador (doble click en el archivo)"
+3. Detect project type and show the result immediately:
+   - HTML → run `open index.html` (or the main HTML file) so the user sees it instantly. Then say "Se abrió en tu navegador."
    - Python → "Corré: python3 main.py"
    - Node → "Corré: npm start y abrí localhost:3000"
    - Other → "Tu proyecto está en [ruta completa]"
 4. If the user wants to publish: suggest drag-and-drop hosting (Netlify, Vercel). Walk through it step by step.
 5. Save artifact and run compound as normal.
-Never mention PR, CI, branch, merge, deploy, or rollback. Output: "Listo. Para verlo: [comando]."
+Never mention PR, CI, branch, merge, deploy, rollback, or slash commands. Output: "Listo. Para verlo: [comando]."
 
 **If `local-git` (git, no remote):** Run pre-ship check and quality check. Skip PR/CI/deploy. Suggest `git tag` for versioning. Output: "Listo. Commit: [hash]."
 
diff --git a/think/SKILL.md b/think/SKILL.md
@@ -78,7 +78,7 @@ Determine the mode from the user's description:
 
 **How to detect the mode:** If the user describes a personal pain ("I have this problem," "I need to..."), default to Startup or Builder. If the user pitches an idea for others ("I want to build X for Y market"), default to Startup. Only use Founder mode when the user asks for it or the context is clearly a high-stakes venture decision.
 
-**Local mode language:** Run `source bin/lib/git-context.sh && detect_git_mode`. If the result is `local` (no git repo), the user is likely non-technical. Adapt your language throughout the entire sprint: replace jargon with plain language. "Narrowest wedge" → "¿Cuál es lo mínimo que necesitás que funcione?" / "Status quo" → "¿Cómo lo estás resolviendo ahora?" / "Premise validated" → "Tiene sentido, avancemos." Same rigor, simpler words. Never mention git, branches, PRs, or diffs.
+**Local mode language:** Run `source bin/lib/git-context.sh && detect_git_mode`. If the result is `local` (no git repo), the user is likely non-technical. Adapt your language throughout the entire sprint: replace jargon with plain language. "Narrowest wedge" → "¿Cuál es lo mínimo que necesitás que funcione?" / "Status quo" → "¿Cómo lo estás resolviendo ahora?" / "Premise validated" → "Tiene sentido, avancemos." Same rigor, simpler words. Never mention git, branches, PRs, or diffs. Do NOT expose internal labels like "Phase 1", "Phase 1.5", "Startup mode", or "Builder mode" — these are your internal process, not something the user needs to see. Just do the work naturally.
 
 ### Phase 1.5: Search Before Building
 
PATCH

echo "Gold patch applied."
