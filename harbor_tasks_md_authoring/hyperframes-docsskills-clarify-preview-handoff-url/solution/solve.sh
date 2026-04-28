#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hyperframes

# Idempotency guard
if grep -qF "Use the actual port from the preview output and the project directory name. For" "skills/hyperframes-cli/SKILL.md" && grep -qF "**Gate:** `npx hyperframes lint` and `npx hyperframes validate` pass with zero e" "skills/website-to-hyperframes/SKILL.md" && grep -qF "The Studio URL is the project handoff surface. In the final response, report the" "skills/website-to-hyperframes/references/step-7-validate.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/hyperframes-cli/SKILL.md b/skills/hyperframes-cli/SKILL.md
@@ -73,6 +73,20 @@ npx hyperframes preview --port 4567       # custom port (default 3002)
 
 Hot-reloads on file changes. Opens the studio in your browser automatically.
 
+When handing a project back to the user, use the Studio project URL, not the
+source `index.html` path:
+
+```text
+http://localhost:<port>/#project/<project-name>
+```
+
+Use the actual port from the preview output and the project directory name. For
+example, after `npx hyperframes preview --port 3017` in `codex-openai-video`,
+report `http://localhost:3017/#project/codex-openai-video`.
+
+Treat `index.html` as source-code context only. It is fine to link it as an
+implementation file, but do not label it as the project or preview surface.
+
 ## Rendering
 
 ```bash
diff --git a/skills/website-to-hyperframes/SKILL.md b/skills/website-to-hyperframes/SKILL.md
@@ -83,9 +83,12 @@ Build each composition following the storyboard. After each one: self-review for
 
 **Read:** [references/step-7-validate.md](references/step-7-validate.md)
 
-Lint, validate, snapshot, preview. Deliver the preview to the user first — only render to MP4 on explicit request.
+Lint, validate, snapshot, preview. Deliver the localhost Studio project URL
+(`http://localhost:<port>/#project/<project-name>`) to the user first — only
+render to MP4 on explicit request. Do not treat `index.html` as the project
+handoff link; it is source-code context only.
 
-**Gate:** `npx hyperframes lint` and `npx hyperframes validate` pass with zero errors.
+**Gate:** `npx hyperframes lint` and `npx hyperframes validate` pass with zero errors, and the final response includes the active Studio project URL.
 
 ---
 
diff --git a/skills/website-to-hyperframes/references/step-7-validate.md b/skills/website-to-hyperframes/references/step-7-validate.md
@@ -71,6 +71,32 @@ npx hyperframes preview
 
 Open the studio in a browser. Scrub through every beat.
 
+### Handoff URL
+
+The Studio URL is the project handoff surface. In the final response, report the
+active preview URL with the project hash:
+
+```text
+http://localhost:<port>/#project/<project-name>
+```
+
+Use the actual port selected by `hyperframes preview` and the project name shown
+by the preview command. If you run `hyperframes preview --port 3017` for a
+project directory named `codex-openai-video`, the project URL is:
+
+```text
+http://localhost:3017/#project/codex-openai-video
+```
+
+Do **not** present `index.html` as the project link. `index.html` is the source
+file for agents and editors; the user-facing project is the running HyperFrames
+Studio preview. You may include source file links as secondary context, but the
+primary "Project" or "Preview" line must be the localhost Studio URL.
+
+If a render was also requested, still include the Studio URL first so the user
+can scrub and inspect the project. Include the MP4 path as the rendered output,
+not as a replacement for the project URL.
+
 ## Render (on-demand only)
 
 **Do NOT render automatically as part of the pipeline.** Preview is the delivery — the user scrubs, spots anything they want tweaked, and you iterate. Rendering to MP4 takes minutes of wall-clock time per pass and is wasted work if the user wants changes.
PATCH

echo "Gold patch applied."
