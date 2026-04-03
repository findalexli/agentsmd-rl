#!/usr/bin/env bash
set -euo pipefail

cd /workspace/angular

# Idempotent: skip if already applied
if grep -q 'NOTE: OnPush is enabled by default' packages/core/src/change_detection/constants.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/adev/src/content/best-practices/runtime-performance/skipping-subtrees.md b/adev/src/content/best-practices/runtime-performance/skipping-subtrees.md
index 02304d483b8b..405836da6e6b 100644
--- a/adev/src/content/best-practices/runtime-performance/skipping-subtrees.md
+++ b/adev/src/content/best-practices/runtime-performance/skipping-subtrees.md
@@ -4,33 +4,20 @@ JavaScript, by default, uses mutable data structures that you can reference from

 Change detection is sufficiently fast for most applications. However, when an application has an especially large component tree, running change detection across the whole application can cause performance issues. You can address this by configuring change detection to only run on a subset of the component tree.

-If you are confident that a part of the application is not affected by a state change, you can use [OnPush](/api/core/ChangeDetectionStrategy) to skip change detection in an entire component subtree.
-
 ## Using `OnPush`

-OnPush change detection instructs Angular to run change detection for a component subtree **only** when:
+OnPush is the default change detection strategy in Angular (since v22). It instructs Angular to run change detection for a component subtree **only** when:

 - The root component of the subtree receives new inputs as the result of a template binding. Angular compares the current and past value of the input with `==`.
 - Angular handles an event _(for example using event binding, output binding, or `@HostListener` )_ in the subtree's root component or any of its children whether they are using OnPush change detection or not.

-You can set the change detection strategy of a component to `OnPush` in the `@Component` decorator:
-
-```ts
-import {ChangeDetectionStrategy, Component} from '@angular/core';
-
-@Component({
-  changeDetection: ChangeDetectionStrategy.OnPush,
-})
-export class MyComponent {}
-```
-
 ## Common change detection scenarios

 This section examines several common change detection scenarios to illustrate Angular's behavior.

-### An event is handled by a component with default change detection
+### An event is handled by a component with `Eager` change detection

-If Angular handles an event within a component without `OnPush` strategy, the framework executes change detection on the entire component tree. Angular will skip descendant component subtrees with roots using `OnPush`, which have not received new inputs.
+If Angular handles an event within a component with the `Eager` strategy, the framework executes change detection on the entire component tree. Angular will skip descendant component subtrees with roots using `OnPush`, which have not received new inputs.

 As an example, if we set the change detection strategy of `MainComponent` to `OnPush` and the user interacts with a component outside the subtree with root `MainComponent`, Angular will check all the pink components from the diagram below (`AppComponent`, `HeaderComponent`, `SearchComponent`, `ButtonComponent`) unless `MainComponent` receives new inputs:

diff --git a/adev/src/content/guide/components/advanced-configuration.md b/adev/src/content/guide/components/advanced-configuration.md
index db7352678995..87a47d4ea51f 100644
--- a/adev/src/content/guide/components/advanced-configuration.md
+++ b/adev/src/content/guide/components/advanced-configuration.md
@@ -7,12 +7,12 @@ TIP: This guide assumes you've already read the [Essentials Guide](essentials).
 The `@Component` decorator accepts a `changeDetection` option that controls the component's **change
 detection mode**. There are two change detection mode options.

-**`ChangeDetectionStrategy.Eager`/`Default`** is, unsurprisingly, the default strategy. In this mode,
+**`ChangeDetectionStrategy.Eager`/`Default`** is an optional mode. In this mode,
 Angular checks whether the component's DOM needs an update whenever any activity may have occurred
 application-wide. Activities that trigger this checking include user interaction, network response,
 timers, and more.

-**`ChangeDetectionStrategy.OnPush`** is an optional mode that reduces the amount of checking Angular
+**`ChangeDetectionStrategy.OnPush`** is the default strategy (since v22). This mode reduces the amount of checking Angular
 needs to perform. In this mode, the framework only checks if a component's DOM needs an update when:

 - A component input has changes as a result of a binding in a template, or
diff --git a/adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md b/adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md
index 00b9a1523373..542e085ec144 100644
--- a/adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md
+++ b/adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md
@@ -116,9 +116,3 @@ The toggle button is already in the template. Connect it to your `toggleStatus()
 Congratulations! You've created your first signal and learned how to update it using both `set()` and `update()` methods. The `signal()` function creates a reactive value that Angular tracks, and when you update it, your UI automatically reflects the changes.

 Next, you'll learn [how to derive state from signals using computed](/tutorials/signals/2-deriving-state-with-computed-signals)!
-
-<docs-callout helpful title="About ChangeDetectionStrategy.OnPush">
-
-You might notice `ChangeDetectionStrategy.OnPush` in the component decorator throughout this tutorial. This is a performance optimization for Angular components that use signals. For now, you can safely ignore it—just know it helps your app run faster when using signals! You can learn more in the [change detection strategies API docs](/api/core/ChangeDetectionStrategy).
-
-</docs-callout>
diff --git a/adev/src/context/airules.md b/adev/src/context/airules.md
index 6e814772dc0d..0044786c9522 100644
--- a/adev/src/context/airules.md
+++ b/adev/src/context/airules.md
@@ -86,7 +86,6 @@ Here is a link to the most recent Angular style guide https://angular.dev/style-
 - Use `input()` signal instead of decorators, learn more here https://angular.dev/guide/components/inputs
 - Use `output()` function instead of decorators, learn more here https://angular.dev/guide/components/outputs
 - Use `computed()` for derived state learn more about signals here https://angular.dev/guide/signals.
-- Set `changeDetection: ChangeDetectionStrategy.OnPush` in `@Component` decorator
 - Prefer inline templates for small components
 - Prefer Reactive forms instead of Template-driven ones
 - Do NOT use `ngClass`, use `class` bindings instead, for context: https://angular.dev/guide/templates/binding#css-class-and-style-property-bindings
diff --git a/adev/src/context/angular-20.mdc b/adev/src/context/angular-20.mdc
index 10a378c7d367..552050c64625 100644
--- a/adev/src/context/angular-20.mdc
+++ b/adev/src/context/angular-20.mdc
@@ -64,7 +64,6 @@ This project adheres to modern Angular best practices, emphasizing maintainabili
         userSelected = output<string>();
         ```
 * **`computed()` for Derived State:** Use the `computed()` function from `@angular/core` for derived state based on signals.
-* **`ChangeDetectionStrategy.OnPush`:** Always set `changeDetection: ChangeDetectionStrategy.OnPush` in the `@Component` decorator for performance benefits by reducing unnecessary change detection cycles.
 * **Inline Templates:** Prefer inline templates (template: `...`) for small components to keep related code together. For larger templates, use external HTML files.
 * **Reactive Forms:** Prefer Reactive forms over Template-driven forms for complex forms, validation, and dynamic controls due to their explicit, immutable, and synchronous nature.
 * **No `ngClass` / `NgClass`:** Do not use the `ngClass` directive. Instead, use native `class` bindings for conditional styling.
diff --git a/adev/src/context/guidelines.md b/adev/src/context/guidelines.md
index 3bcc2d332e00..8bc6f835c0ad 100644
--- a/adev/src/context/guidelines.md
+++ b/adev/src/context/guidelines.md
@@ -92,7 +92,6 @@ Here is a link to the most recent Angular style guide https://angular.dev/style-
 - Use `input()` signal instead of decorators, learn more here https://angular.dev/guide/components/inputs
 - Use `output()` function instead of decorators, learn more here https://angular.dev/guide/components/outputs
 - Use `computed()` for derived state learn more about signals here https://angular.dev/guide/signals.
-- Set `changeDetection: ChangeDetectionStrategy.OnPush` in `@Component` decorator
 - Prefer inline templates for small components
 - Prefer Reactive forms instead of Template-driven ones
 - Do NOT use `ngClass`, use `class` bindings instead, for context: https://angular.dev/guide/templates/binding#css-class-and-style-property-bindings
diff --git a/packages/core/src/change_detection/constants.ts b/packages/core/src/change_detection/constants.ts
index 093da595575d..03299372140b 100644
--- a/packages/core/src/change_detection/constants.ts
+++ b/packages/core/src/change_detection/constants.ts
@@ -21,6 +21,8 @@ export enum ChangeDetectionStrategy {
    * until reactivated by setting the strategy to `Default` (`CheckAlways`).
    * Change detection can still be explicitly invoked.
    * This strategy applies to all child directives and cannot be overridden.
+   *
+   * NOTE: OnPush is enabled by default.
    */
   OnPush = 0,

diff --git a/packages/core/src/metadata/directives.ts b/packages/core/src/metadata/directives.ts
index 8605922095c5..2df2ff379ffb 100644
--- a/packages/core/src/metadata/directives.ts
+++ b/packages/core/src/metadata/directives.ts
@@ -548,7 +548,9 @@ export interface Component extends Directive {
    * which is responsible for propagating the component's bindings.
    * The strategy is one of:
    * - `ChangeDetectionStrategy#OnPush` sets the strategy to `CheckOnce` (on demand).
-   * - `ChangeDetectionStrategy#Default` sets the strategy to `CheckAlways`.
+   * - `ChangeDetectionStrategy#Eager` sets the strategy to `CheckAlways`.
+   *
+   * NOTE: OnPush is enabled by default.
    */
   changeDetection?: ChangeDetectionStrategy;

PATCH

echo "Patch applied successfully."
