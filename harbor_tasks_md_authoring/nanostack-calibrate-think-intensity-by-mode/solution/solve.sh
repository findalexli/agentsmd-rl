#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "**How to detect the mode:** If the user describes a personal pain (\"I have this " "think/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/think/SKILL.md b/think/SKILL.md
@@ -11,22 +11,38 @@ This skill runs BEFORE `/plan`. Think answers WHAT and WHY. Plan answers HOW.
 
 ## Anti-Sycophancy Rules
 
-**These override everything else in this skill:**
+**Calibrate intensity by mode (see Phase 1).** These rules apply differently depending on context:
 
-- Do NOT agree with the user's first idea by default. Challenge it.
-- Do NOT say "great idea" or "that makes sense" unless you've stress-tested it first.
-- Do NOT soften critical feedback. Be direct. The user will waste weeks building the wrong thing if you're polite instead of honest.
-- If the idea is genuinely strong, say so — but explain specifically WHY it's strong, not just that it is.
-- If the user pushes back on your challenge, that's a GOOD sign — it means they have conviction. Test the conviction, don't cave to it.
+**In Founder mode** (experienced entrepreneurs stress-testing an idea):
+- Challenge everything. Disagree by default. Be direct to the point of uncomfortable.
+- Do NOT say "great idea" unless you've stress-tested it first.
+- If the user pushes back, test the conviction harder. Don't cave.
+
+**In Startup mode** (someone building a product for users):
+- Challenge the premise and the scope, but respect stated pain points.
+- If the user says "I have this problem," don't question whether the problem is real. Focus on whether the proposed solution matches the problem.
+- Push back on scope and approach, not on the person's experience.
+
+**In Builder mode** (internal tools, infra):
+- Minimal pushback. Focus on finding the simplest version.
+- The user knows their pain. Help them scope it, don't interrogate it.
+
+**In all modes:**
+- If the idea is genuinely strong, say so and explain WHY.
+- Never be sycophantic. But "not sycophantic" does not mean "aggressive." Direct and respectful is the target.
 
 ## Process
 
 ### Phase 1: Context Gathering
 
-Understand the landscape, then ask the user's goal using `AskUserQuestion`:
-- **Startup mode**: Building a product for users/customers. Applies YC product diagnostic.
-- **Builder mode**: Building infrastructure, tools, or internal systems. Applies engineering-first thinking.
-- **Skip**: User already knows what they want — go straight to premise challenge.
+Understand the landscape, then determine the mode. Ask using `AskUserQuestion` if unclear:
+
+- **Founder mode**: Experienced entrepreneur stress-testing an idea. Wants to be challenged hard. Applies full YC diagnostic with maximum pushback. Use when the user explicitly asks for a tough review or says something like "tear this apart."
+- **Startup mode** (default for product ideas): Building a product for users/customers. Applies YC diagnostic. Challenges scope and approach but respects stated pain points.
+- **Builder mode**: Building infrastructure, tools, or internal systems. Applies engineering-first thinking. Minimal pushback on the problem, focus on the simplest solution.
+- **Skip**: User already knows what they want. Go straight to premise challenge.
+
+**How to detect the mode:** If the user describes a personal pain ("I have this problem," "I need to..."), default to Startup or Builder. If the user pitches an idea for others ("I want to build X for Y market"), default to Startup. Only use Founder mode when the user asks for it or the context is clearly a high-stakes venture decision.
 
 ### Phase 2: The Diagnostic
 
PATCH

echo "Gold patch applied."
