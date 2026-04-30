#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "**Critical rules**: Always use `useCurrentFrame()` for animations. Never use CSS" "skills/remotion/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/remotion/SKILL.md b/skills/remotion/SKILL.md
@@ -1,13 +1,42 @@
 ---
 name: remotion-best-practices
-description: Best practices for Remotion - Video creation in React
+description: >
+  Guides implementation of Remotion video compositions, animations, transitions,
+  audio/video embedding, captions, and rendering in React. Covers frame-based timing
+  with interpolate() and useCurrentFrame(), media trimming and looping, scene sequencing,
+  3D content, chart animations, text effects, and Tailwind integration.
+  Use when the user mentions Remotion, programmatic video, React video, video composition,
+  video rendering, frame animation, MP4 export, or works with .remotion files.
 metadata:
   tags: remotion, video, react, animation, composition
 ---
 
 ## When to use
 
-Use this skills whenever you are dealing with Remotion code to obtain the domain-specific knowledge.
+Use this skill when working with Remotion code — creating compositions, animating scenes,
+embedding audio/video, adding captions, configuring rendering, or troubleshooting
+frame-based timing issues.
+
+## Quick start
+
+A minimal Remotion composition:
+
+```tsx
+import { useCurrentFrame, useVideoConfig, interpolate, Composition } from "remotion";
+
+const MyVideo: React.FC = () => {
+  const frame = useCurrentFrame();
+  const { fps } = useVideoConfig();
+  const opacity = interpolate(frame, [0, fps], [0, 1], { extrapolateRight: "clamp" });
+  return <div style={{ opacity }}>Hello Remotion</div>;
+};
+
+export const RemotionRoot: React.FC = () => (
+  <Composition id="MyVideo" component={MyVideo} width={1920} height={1080} fps={30} durationInFrames={90} />
+);
+```
+
+**Critical rules**: Always use `useCurrentFrame()` for animations. Never use CSS transitions or Tailwind animation classes — they will not render.
 
 ## How to use
 
PATCH

echo "Gold patch applied."
