#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hyperframes

# Idempotency guard
if grep -qF "- **Never stack two transform tweens on the same element.** A common failure: a " "skills/website-to-hyperframes/references/step-6-build.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/website-to-hyperframes/references/step-6-build.md b/skills/website-to-hyperframes/references/step-6-build.md
@@ -164,3 +164,66 @@ These exist because the capture engine is deterministic. Violations produce brok
 - **Never use ANY CSS `transform` for centering** — not `translate(-50%, -50%)`, not `translateX(-50%)`, not `translateY(-50%)`. GSAP animates the `transform` property, which overwrites ALL CSS transforms including centering. The element flies offscreen. Use flexbox centering instead: `display:flex; align-items:center; justify-content:center` on a wrapper div. The linter catches this (`gsap_css_transform_conflict`) but only if you run it.
 - **Minimum font sizes**: 20px body, 16px labels
 - **No full-screen dark linear gradients** — H.264 banding
+
+---
+
+## Load-bearing rules for animation authoring
+
+Rules below came out of two independent website-to-hyperframes builds (2026-04-20) where compositions lint-clean and still ship broken — elements that never appear, ambient motion that doesn't scrub, entrance tweens that silently kill their target. The linter cannot catch these; the rules must be followed by the author.
+
+- **No iframes for captured content.** Iframes do not seek deterministically with the timeline — the capture engine cannot scrub inside them, so they appear frozen (or blank) in the rendered output. If the source you're stylizing is a live web app, use the screenshots from `capture/` as stacked panels or layered images, not live embeds.
+
+- **Never stack two transform tweens on the same element.** A common failure: a `y` entrance plus a `scale` Ken Burns on the same `<img>`. The second tween's `immediateRender: true` writes the element's initial state at construction time, overwriting whatever the first tween set — leaving the element invisible or offscreen with no lint warning. A secondary mechanism: `tl.from()` resets to its declared "from" state when the playhead is seeked past the timeline's end, so an element that looked correct in linear playback vanishes in the capture engine's non-linear seek. Fix one of two ways:
+
+  ```html
+  <!-- BAD: two transforms on one element -->
+  <img class="hero" src="..." />
+  <script>
+    tl.from(".hero", { y: 50, opacity: 0, duration: 0.6 }, 0);
+    tl.to(".hero", { scale: 1.04, duration: beat }, 0); // kills the entrance
+  </script>
+
+  <!-- GOOD option A: combine into one tween -->
+  <script>
+    tl.fromTo(
+      ".hero",
+      { y: 50, opacity: 0, scale: 1.0 },
+      { y: 0, opacity: 1, scale: 1.04, duration: beat, ease: "none" },
+      0,
+    );
+  </script>
+
+  <!-- GOOD option B: split across parent + child -->
+  <div class="hero-wrap"><img class="hero" src="..." /></div>
+  <script>
+    tl.from(".hero-wrap", { y: 50, opacity: 0, duration: 0.6 }, 0); // entrance on parent
+    tl.to(".hero", { scale: 1.04, duration: beat }, 0); // Ken Burns on child
+  </script>
+  ```
+
+- **Prefer `tl.fromTo()` over `tl.from()` inside `.clip` scenes.** `gsap.from()` sets `immediateRender: true` by default, which writes the "from" state at timeline construction — before the `.clip` scene's `data-start` is active. Elements can flash visible, start from the wrong position, or skip their entrance entirely when the scene is seeked non-linearly (which the capture engine does). Explicit `fromTo` makes the state at every timeline position deterministic:
+
+  ```js
+  // BRITTLE: immediateRender interacts badly with scene boundaries
+  tl.from(el, { opacity: 0, y: 50, duration: 0.6 }, t);
+
+  // DETERMINISTIC: state is defined at both ends, no immediateRender surprise
+  tl.fromTo(el, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.6 }, t);
+  ```
+
+- **Ambient pulses must attach to the seekable `tl`, never bare `gsap.to()`.** Auras, shimmers, gentle float loops, logo breathing — all of these must be added to the scene's timeline, not fired standalone. Standalone tweens run on wallclock time and do not scrub with the capture engine, so the effect is absent in the rendered video even though it looks correct in the studio preview:
+
+  ```js
+  // BAD: lives outside the timeline, never renders in capture
+  gsap.to(".aura", { scale: 1.08, yoyo: true, repeat: 5, duration: 1.2 });
+
+  // GOOD: seekable, deterministic, renders
+  tl.to(".aura", { scale: 1.08, yoyo: true, repeat: 5, duration: 1.2 }, 0);
+  ```
+
+- **Hard-kill every scene boundary, not just captions.** The caption hard-kill rule above generalizes: any element whose visibility changes at a beat boundary needs a deterministic `tl.set()` kill after its fade, because later tweens on the same element (or `immediateRender` from a sibling tween) can resurrect it. Apply to every element with an exit animation:
+
+  ```js
+  tl.to(el, { opacity: 0, duration: 0.3 }, beatEnd);
+  tl.set(el, { opacity: 0, visibility: "hidden" }, beatEnd + 0.3); // deterministic kill
+  ```
PATCH

echo "Gold patch applied."
