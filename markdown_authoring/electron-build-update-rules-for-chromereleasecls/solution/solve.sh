#!/usr/bin/env bash
set -euo pipefail

cd /workspace/electron

# Idempotency guard
if grep -qF "- **Roll CLs \u2014 skip and find the upstream fix:** For components whose fixes land" ".claude/skills/chrome-release-cls/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/chrome-release-cls/SKILL.md b/.claude/skills/chrome-release-cls/SKILL.md
@@ -74,11 +74,30 @@ Drive it from `/tmp/cve_bugs.txt`. Prefer the **non-`[M1xx]`-prefixed** commit s
 For any bug with no local hit:
 - `git -C <repo> fetch origin` then re-search `--remotes` (fix may be newer than the checkout).
 - Query Gerrit directly: `curl -s "https://chromium-review.googlesource.com/changes/?q=bug:${BUG}&n=10" | tail -n +2 | python3 -m json.tool` (also try `skia-review`, `pdfium-review`, `dawn-review`, `aomedia-review`).
+- **`b/` bug format (Skia, Graphite, Dawn):** These repos reference bugs as `b/<id>` in commit messages rather than `Bug: <id>` footers. The Gerrit `bug:` query will return nothing. Use `message:<id>` search instead:
+  ```bash
+  curl -s "https://skia-review.googlesource.com/changes/?q=message:${BUG}&n=5" | tail -n +2
+  ```
+  Apply the same pattern for `dawn-review.googlesource.com` when the component is Dawn.
+- **Tracing main CLs from merges:** When only `[M1xx]` merge CLs are found, query the CL detail for `cherry_pick_of_change` to find the original main CL number:
+  ```bash
+  curl -s "https://chromium-review.googlesource.com/changes/${CL_NUM}?o=CURRENT_REVISION" | tail -n +2 | python3 -c "
+  import sys, json
+  d = json.load(sys.stdin)
+  print(d.get('cherry_pick_of_change', 'none'))
+  "
+  ```
 - If still nothing and the bug was reported very recently (especially by "Google Threat Intelligence" or marked in-the-wild), the CL is likely still access-restricted — report it as such rather than guessing.
 
 ### 4. Special cases
 
-- **libaom / libvpx / ffmpeg** components: the actual fix lands upstream; the chromium-side hit will be a `Roll src/third_party/...` commit. Report the roll CL and note the fix is upstream.
+- **Roll CLs — skip and find the upstream fix:** For components whose fixes land in upstream repos (PDFium, Dawn, Skia, Graphite, libaom, libvpx, ffmpeg), the chromium-review hit will be a `Roll src/third_party/...` commit. Do not report the roll CL as the fix. Instead, query the component's own Gerrit instance directly for the actual fixing CL:
+  - PDFium → `pdfium-review.googlesource.com` (use `bug:` or `message:` query)
+  - Dawn → `dawn-review.googlesource.com` (use `message:` query — uses `b/` format)
+  - Skia / Graphite → `skia-review.googlesource.com` (use `message:` query — uses `b/` format)
+  - libaom → `aomedia-review.googlesource.com`
+  
+  Only if the upstream Gerrit instance returns no results should you fall back to reporting the roll CL — in that case, include the roll CL and note that the actual fix is upstream but the specific CL could not be identified.
 - Multiple `Reviewed-on:` lines in one commit body: cherry-picks keep the original line plus a new one. The **first** `Reviewed-on:` is the original CL.
 - A bug may have multiple distinct fix CLs (fix + follow-up hardening) — list all of them.
 
PATCH

echo "Gold patch applied."
