#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mudblazor

# Idempotency guard
if grep -qF "- Show code for simple, canonical examples by default. Also show code when the m" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -210,12 +210,22 @@ private Task ToggleAsync()
 - Provide accessible names for interactive controls through a label, `aria-label`, or `aria-labelledby`.
 - Components with logic require bUnit tests and a docs page at `src/MudBlazor.Docs/Pages/Components/<ComponentName>.razor`.
 
-## Docs Rules
-
-- Order examples from simple to complex.
-- Collapse examples longer than 15 lines by default.
-- Prefer minimal, focused examples that demonstrate one concept at a time.
-- Keep docs in sync with behavior and parameter changes.
+## Docs Pages and Examples
+
+- Keep docs in sync with component behavior, public APIs, and parameter changes.
+- Use `src/MudBlazor.Docs/Pages/Components/Button/ButtonPage.razor` or `src/MudBlazor.Docs/Pages/Components/Menu/MenuPage.razor` as a reference for component docs structure.
+- Start with basic usage, introduce common variants next, group related scenarios with `SectionSubGroups`, and leave advanced or edge-case behavior for the end.
+- Write each component page as a guided progression rather than a catalog dump. Use clear section titles and short descriptions that explain when and why a feature is useful.
+- Order examples from simple to complex. Start with a small canonical example, then add focused examples for common variants, composition patterns, binding, edge cases, and advanced behavior.
+- Keep examples in `src/MudBlazor.Docs/Pages/Components/<ComponentName>/Examples/` and name them after the component and scenario, such as `<ComponentName>SimpleExample`, `<ComponentName>DenseExample`, or `<ComponentName>TwoWayBindingExample`.
+- Do not leave orphaned example components under `Examples/`. Every example should be referenced by the docs page or removed.
+- Prefer minimal examples that demonstrate one concept at a time. Make them realistic enough to teach the workflow, but avoid extra state, styling, or unrelated component features that distract from the documented behavior.
+- Use meaningful labels and sample content in examples. Avoid `Item 1`, `Item 2`, or placeholder text unless the content is irrelevant to the behavior being demonstrated.
+- Reference example components from pages with `Code="@nameof(...)"` so renames stay compiler-checked.
+- Show code for simple, canonical examples by default. Also show code when the markup, binding, accessibility attribute, or event pattern is the behavior being taught. Collapse examples longer than 15 lines, and use `ShowCode="false"` on secondary examples when the rendered behavior is more important than repeating similar markup.
+- Use `CodeInline` for parameter, component, and member names in descriptions. Use `MudLink` for cross-links to related component pages when that helps users continue learning.
+- Descriptions and examples must agree with the component's actual defaults and current behavior. Verify ambiguous defaults against the component code or tests before documenting them.
+- Include practical guidance near the relevant example for accessibility-sensitive behavior, keyboard interaction, focus management, and other usage constraints. When prose mentions an accessibility requirement, the example should demonstrate it.
 - Docs examples are exercised by generated tests, so they must render without exceptions.
 - Generated docs tests are emitted as `Generated/*.generated.cs` files and must not be edited by hand.
 - `MudBlazor.UnitTests.Docs` does not generate docs tests in the default local build unless `GenerateDocsTests=true`.
PATCH

echo "Gold patch applied."
