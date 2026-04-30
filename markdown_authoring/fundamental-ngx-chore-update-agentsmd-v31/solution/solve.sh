#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fundamental-ngx

# Idempotency guard
if grep -qF "When migrating from `@Input()` decorators to `input()` signals, you may encounte" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,7 +1,7 @@
 <!--
 Document: Angular 21+ Development Guidelines for Fundamental NGX
-Last Updated: February 6, 2026
-Version: 3.0
+Last Updated: February 21, 2026
+Version: 3.1
 Purpose: Comprehensive guide for AI agents and developers working with Angular 21+ in NX monorepo
 -->
 
@@ -12,14 +12,23 @@ Purpose: Comprehensive guide for AI agents and developers working with Angular 2
 1. [Persona](#persona)
 2. [Angular 21 Component Examples](#angular-21-component-examples)
 3. [Resources](#resources)
-4. [Best Practices & Style Guide](#best-practices--style-guide)
+4. [Quick Decision Guide](#quick-decision-guide)
+5. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
+6. [Best Practices & Style Guide](#best-practices--style-guide)
     - [Angular Style Guide](#angular-style-guide)
     - [TypeScript Best Practices](#typescript-best-practices)
     - [Angular Best Practices](#angular-best-practices)
     - [Zoneless Compatibility](#zoneless-compatibility)
     - [Accessibility Requirements](#accessibility-requirements)
     - [Components](#components)
+        - [Migrating from CssClassBuilder](#migrating-from-cssclassbuilder)
+        - [Linked Signals](#linked-signals)
+        - [Queries](#queries)
+        - [Component Member Ordering](#component-member-ordering)
     - [Dependency Injection Patterns](#dependency-injection-patterns)
+        - [Pattern 1: Contextual Defaults](#pattern-1-contextual-defaults-with-injectiontokens)
+        - [Pattern 2: Component Composition](#pattern-2-component-composition-with-injectiontokens)
+        - [Programmatic Signal Input Updates](#programmatic-signal-input-updates)
     - [State Management](#state-management)
     - [Render Lifecycle Hooks](#render-lifecycle-hooks)
     - [Resource API (Experimental)](#resource-api-experimental)
@@ -28,10 +37,12 @@ Purpose: Comprehensive guide for AI agents and developers working with Angular 2
     - [Signal-Based Change Detection](#signal-based-change-detection)
     - [Templates](#templates)
     - [Services](#services)
-5. [NX Monorepo Architecture](#nx-monorepo-architecture)
-6. [Commit Message Guidelines](#commit-message-guidelines)
-7. [Pull Request Guidelines](#pull-request-guidelines)
-8. [Coding Rules and Standards](#coding-rules-and-standards)
+7. [NX Monorepo Architecture](#nx-monorepo-architecture)
+8. [Breaking Changes Guidelines](#breaking-changes-guidelines)
+9. [Dead Code Removal](#dead-code-removal)
+10. [Commit Message Guidelines](#commit-message-guidelines)
+11. [Pull Request Guidelines](#pull-request-guidelines)
+12. [Coding Rules and Standards](#coding-rules-and-standards)
 
 ---
 
@@ -129,6 +140,29 @@ Here are the essential links for building Angular components. Use these to under
 | Host bindings and event listeners         | Use `host: {}` in decorator              | [Host Bindings](#host-bindings-and-event-listeners)                                |
 | Async operations (HTTP, timers)           | Use RxJS Observables                     | [Effect vs Observables](#effect-vs-observables)                                    |
 | BehaviorSubject for state                 | Migrate to `signal()`                    | [BehaviorSubject vs Computed](#behaviorsubject--combinelatest-vs-computed-signals) |
+| `Subject<void>` for notifications         | Replace with `effect()` on signal        | [Effect vs Observables](#effect-vs-observables)                                    |
+| `contentChild()` returns undefined        | Use `?? null` for null-expecting signals | [Queries](#queries)                                                                |
+| Setting signal input programmatically     | Use setter method pattern                | [Programmatic Signal Input Updates](#programmatic-signal-input-updates)            |
+| Removing unused code                      | Verify no usages, check public API       | [Dead Code Removal](#dead-code-removal)                                            |
+
+## Common Mistakes to Avoid
+
+**For AI Agents: Quick reference of anti-patterns to watch for**
+
+| ❌ Don't Do This                     | ✅ Do This Instead                            | Why                                      |
+| ------------------------------------ | --------------------------------------------- | ---------------------------------------- |
+| `@HostBinding()` / `@HostListener()` | Use `host: {}` in decorator                   | Better tree-shaking, AOT compilation     |
+| `@Input()` / `@Output()` decorators  | Use `input()` / `output()` functions          | Signal-based, automatic change detection |
+| `standalone: true` in decorator      | Omit it (default in Angular 21+)              | Cleaner code, implicit default           |
+| `ngClass` / `ngStyle`                | Use `class` / `style` bindings                | Direct binding is simpler                |
+| `*ngIf` / `*ngFor` / `*ngSwitch`     | Use `@if` / `@for` / `@switch`                | New control flow syntax                  |
+| `BehaviorSubject` for local state    | Use `signal()`                                | Simpler, automatic cleanup               |
+| `signal.set(); markForCheck();`      | Just `signal.set();`                          | Signals auto-notify Angular              |
+| Custom `DestroyedService`            | Use `DestroyRef` + `takeUntilDestroyed()`     | Built-in Angular pattern                 |
+| `CssClassBuilder` + `@applyCssClass` | Use `computed()` + `host: { '[class]': ... }` | Signal-based reactivity                  |
+| Setting signal inputs externally     | Use InjectionToken or setter method           | Signal inputs are read-only              |
+| Protected after private members      | Protected before private                      | ESLint member ordering rule              |
+| `allowSignalWrites: true` in effect  | Remove the option                             | Deprecated in Angular 21+                |
 
 ## Best Practices & Style Guide
 
@@ -150,6 +184,33 @@ Follow the [Angular Style Guide](https://angular.dev/style-guide) for all coding
 - Always handle null/undefined cases explicitly
 - Use type guards and discriminated unions for complex conditional types
 
+#### Precise Signal Type Annotations
+
+When exposing signals from services or components, use precise type annotations that match exactly what is assigned:
+
+```typescript
+// For readonly signals from WritableSignal.asReadonly()
+readonly contentDensity: ReturnType<WritableSignal<ContentDensityMode>['asReadonly']>;
+
+// For computed signals
+readonly isCompact: ReturnType<typeof computed<boolean>>;
+
+// Generic Signal type (simpler, also acceptable)
+readonly contentDensity: Signal<ContentDensityMode>;
+```
+
+**Why use `ReturnType<...>` patterns:**
+
+- `ReturnType<WritableSignal<T>['asReadonly']>` - Precisely matches the return type of `asReadonly()` method
+- `ReturnType<typeof computed<T>>` - Precisely matches the return type of `computed()` function
+- These ensure type annotations exactly match the assigned value
+
+**When to use each:**
+
+- **`Signal<T>`**: General-purpose, works in most cases
+- **`ReturnType<WritableSignal<T>['asReadonly']>`**: When assigning from `signal().asReadonly()`
+- **`ReturnType<typeof computed<T>>`**: When assigning from `computed()`
+
 ### Angular Best Practices
 
 - Always use standalone components over `NgModules`
@@ -503,6 +564,15 @@ export class Form {
 - Query results are signals - call them with `()`
 - Prefer querying by type or token over template references
 - Use `read` option to specify what to extract from the queried element
+- **Type coercion:** `contentChild()` with optional chaining returns `undefined`, not `null`. Use `?? null` when passing to signals expecting `string | null`:
+
+```typescript
+// ❌ Type error - undefined not assignable to null
+this.header()?.ariaControls.set(this.list()?.id());
+
+// ✅ Correct - coerce undefined to null
+this.header()?.ariaControls.set(this.list()?.id() ?? null);
+```
 
 #### Naming Conventions
 
@@ -793,6 +863,79 @@ export class Title {
 
 **Key principle:** With signal inputs, the **child component is in control** of its own state. The parent provides context via DI, and the child decides what to do with it.
 
+#### Programmatic Signal Input Updates
+
+When migrating from `@Input()` decorators to `input()` signals, you may encounter cases where external code needs to programmatically update a directive's input value. **Signal inputs are read-only** from outside the component, so direct assignment no longer works.
+
+**❌ This pattern breaks with signal inputs:**
+
+```typescript
+// Before migration - worked with @Input()
+@Directive({ selector: '[fdContentDensity]' })
+export class ContentDensityDirective {
+    @Input() fdContentDensity: ContentDensityMode;
+}
+
+// External code could directly assign:
+this._contentDensity.fdContentDensity = ContentDensityMode.COMPACT; // Worked!
+
+// After migration - signal input is read-only
+@Directive({ selector: '[fdContentDensity]' })
+export class ContentDensityDirective {
+    readonly fdContentDensity = input<ContentDensityMode>('');
+}
+
+// External code CANNOT assign:
+this._contentDensity.fdContentDensity = ContentDensityMode.COMPACT; // ❌ Error: read-only!
+```
+
+**✅ Solution: Add a setter method for programmatic updates:**
+
+```typescript
+@Directive({ selector: '[fdContentDensity]' })
+export class ContentDensityDirective {
+    // Signal input for template binding
+    readonly fdContentDensity = input<ContentDensityMode | ''>('');
+
+    // Private signal for programmatic updates
+    private readonly _programmaticValue = signal<ContentDensityMode | null>(null);
+
+    // Computed that combines both sources (programmatic takes priority)
+    readonly effectiveValue = computed(() => {
+        const programmatic = this._programmaticValue();
+        if (programmatic !== null) {
+            return programmatic;
+        }
+        return this.fdContentDensity() || this._defaultValue;
+    });
+
+    // Public method for programmatic updates
+    setDensity(density: ContentDensityMode): void {
+        this._programmaticValue.set(density);
+    }
+
+    // Optional: method to clear programmatic value and revert to input
+    clearDensity(): void {
+        this._programmaticValue.set(null);
+    }
+}
+
+// External code uses the setter method:
+this._contentDensity.setDensity(ContentDensityMode.COMPACT); // ✅ Works!
+```
+
+**When this pattern is needed:**
+
+- Directives used via `hostDirectives` where parent needs to control the value
+- Components that expose an API for programmatic state changes
+- Migration scenarios where existing code relied on direct property assignment
+
+**Alternative approaches to consider:**
+
+1. **Use a service/storage provider** - If multiple components need to share the value
+2. **Use `model()` instead of `input()`** - If two-way binding is appropriate
+3. **Use InjectionToken pattern** - If parent should provide defaults (see Pattern 1 above)
+
 #### Pattern 2: Component Composition with InjectionTokens
 
 Use `InjectionToken` for component composition and content queries to create loose coupling between parent and child components. This pattern allows querying for component roles rather than concrete implementations.
@@ -1091,6 +1234,29 @@ export class Popover {
 - Effects automatically track signal dependencies - no need for manual dependency arrays
 - Effects are automatically cleaned up when the component/service is destroyed
 
+**Replace `Subject<void>` with `effect()`:**
+
+When a `Subject<void>` is used for notifications alongside a signal update, remove it and use `effect()` instead:
+
+```typescript
+// ❌ Before - redundant Subject notification
+set collapsed(value: boolean) {
+    this.service.collapsed.set(value);
+    this.service.visibilityChange.next();  // Redundant!
+}
+// Consumer: this.service.visibilityChange.subscribe(() => this.update());
+
+// ✅ After - effect reacts to signal directly
+set collapsed(value: boolean) {
+    this.service.collapsed.set(value);  // Just update the signal
+}
+// Consumer uses effect():
+effect(() => {
+    this.service.collapsed();  // Track signal
+    this.update();             // React to change
+});
+```
+
 **Using `untracked()` to prevent dependencies:**
 
 Use `untracked()` when you need to read a signal's value inside an effect without creating a dependency on it.
@@ -1430,7 +1596,69 @@ protected readonly _isEnabled = computed(() =>
 - Use the `providedIn: 'root'` option for singleton services
 - Use the `inject()` function instead of constructor injection
 
----
+**Subscription Cleanup with `takeUntilDestroyed()`:**
+
+When services or components subscribe to observables, use `takeUntilDestroyed()` for automatic cleanup instead of manual `Subject<void>` + `takeUntil()` pattern.
+
+```typescript
+// ❌ Before - manual cleanup with Subject
+@Injectable()
+export class MyService implements OnDestroy {
+    private readonly _destroy$ = new Subject<void>();
+    private readonly _router = inject(Router);
+
+    constructor() {
+        this._router.events.pipe(takeUntil(this._destroy$)).subscribe((event) => this.handleEvent(event));
+    }
+
+    ngOnDestroy(): void {
+        this._destroy$.next();
+        this._destroy$.complete();
+    }
+}
+
+// ✅ After - automatic cleanup with takeUntilDestroyed
+@Injectable()
+export class MyService {
+    private readonly _router = inject(Router);
+    private readonly _destroyRef = inject(DestroyRef);
+
+    constructor() {
+        this._router.events.pipe(takeUntilDestroyed(this._destroyRef)).subscribe((event) => this.handleEvent(event));
+    }
+    // No ngOnDestroy needed!
+}
+```
+
+**Key points:**
+
+- Import `DestroyRef` and `takeUntilDestroyed` from `@angular/core` and `@angular/core/rxjs-interop`
+- In constructor context, `takeUntilDestroyed()` can be called without arguments
+- Outside constructor, pass `DestroyRef` explicitly: `takeUntilDestroyed(this._destroyRef)`
+- This pattern prevents memory leaks from forgotten unsubscriptions
+
+**Deprecated patterns:**
+
+- **Do NOT use custom `DestroyedService` implementations** - Angular's built-in `DestroyRef` + `takeUntilDestroyed()` replaces any custom destroyed service patterns
+- If you encounter a `DestroyedService` in the codebase, migrate it to `DestroyRef`
+
+**Signal-based Services:**
+
+- Use `readonly` on all signals to prevent accidental reassignment (`.set()` and `.update()` still work)
+- Remove RxJS `Subject<void>` when signals can replace the notification pattern
+- Use `computed()` for derived state in services
+
+```typescript
+@Injectable()
+export class MyService {
+    readonly collapsed = signal(false);       // readonly prevents reassignment
+    readonly size = computed(() => ...);      // derived state
+
+    toggleCollapsed(): void {
+        this.collapsed.update(v => !v);       // .update() still works
+    }
+}
+```
 
 ---
 
@@ -1478,6 +1706,121 @@ This project uses NX as a monorepo build system with the following library struc
 
 ---
 
+## Breaking Changes Guidelines
+
+**For AI Agents: Understanding what constitutes a breaking change**
+
+A breaking change is any modification that could cause existing consumer code to fail or behave differently after upgrading.
+
+### What Constitutes a Breaking Change
+
+| Change Type                           | Breaking? | Example                                         |
+| ------------------------------------- | --------- | ----------------------------------------------- |
+| Removing exported class/function/type | ✅ Yes    | Removing `DestroyedService` from public API     |
+| Removing exported constant/token      | ✅ Yes    | Removing `FD_BUTTON` InjectionToken             |
+| Changing function signature           | ✅ Yes    | Adding required parameter, changing return type |
+| Renaming exported symbol              | ✅ Yes    | Renaming `ButtonComponent` to `FdButton`        |
+| Changing input/output names           | ✅ Yes    | Renaming `@Input() label` to `@Input() text`    |
+| Changing default values               | ⚠️ Maybe  | If consumers rely on the default behavior       |
+| Adding optional parameter             | ❌ No     | Adding `options?: Config` parameter             |
+| Adding new export                     | ❌ No     | Exporting new `CardComponent`                   |
+| Internal refactoring                  | ❌ No     | Changing private implementation details         |
+
+### Breaking Change Commit Format
+
+```
+fix(scope)!: description of change
+
+BREAKING CHANGE: Detailed explanation of what changed and migration path.
+```
+
+**Key points:**
+
+- Use `!` after the scope to indicate breaking change
+- Include `BREAKING CHANGE:` in the footer with migration instructions
+- Provide clear guidance on how consumers should update their code
+
+### Before Removing Public API
+
+1. **Search for usages** - Use grep/search to find all references in the codebase
+2. **Check exports** - Verify if the symbol is exported from any `index.ts` or public API files
+3. **Consider deprecation** - For widely-used APIs, deprecate first with `@deprecated` JSDoc
+4. **Document migration** - Explain what consumers should use instead
+
+---
+
+## Dead Code Removal
+
+**For AI Agents: Safely identifying and removing unused code**
+
+### Steps to Safely Remove Dead Code
+
+1. **Search for all usages:**
+
+    ```bash
+    # Search for the symbol name across the codebase
+    grep -r "SymbolName" --include="*.ts" --include="*.html"
+    ```
+
+2. **Check public API exports:**
+
+    - Look in `index.ts` files for re-exports
+    - Check if symbol is part of the library's public API
+    - Public API removal = breaking change
+
+3. **Verify with build:**
+
+    ```bash
+    nx build <affected-project>
+    ```
+
+4. **Run tests:**
+    ```bash
+    nx test <affected-project>
+    ```
+
+### Decision Tree for Removal
+
+```
+Is the symbol exported from a public index.ts?
+├── Yes → Breaking change, requires:
+│         • !suffix in commit type
+│         • BREAKING CHANGE footer
+│         • Migration documentation
+└── No → Internal code, safe to remove if:
+          • No grep results found
+          • Build succeeds
+          • Tests pass
+```
+
+### Common Dead Code Patterns
+
+- **Deprecated services** - Old patterns replaced by Angular built-ins (e.g., `DestroyedService` → `DestroyRef`)
+- **Unused utilities** - Helper functions that were refactored away
+- **Legacy adapters** - Compatibility code for old Angular versions
+- **Orphaned types** - Interfaces/types no longer referenced
+
+### Example: Removing Unused Service
+
+```bash
+# 1. Search for usages
+grep -r "DestroyedService" --include="*.ts"
+
+# 2. If only found in its own file → candidate for removal
+
+# 3. Check if exported (look in index.ts)
+grep "destroyed.service" libs/cdk/utils/services/index.ts
+
+# 4. If exported → breaking change
+# 5. Remove file and export
+# 6. Build and test
+nx build cdk && nx test cdk
+
+# 7. Commit with breaking change format
+```
+
+---
+
 ## Commit Message Guidelines
 
 **Quick Format:** `<type>(<scope>): <subject>` - Both type AND scope are mandatory.
@@ -1701,8 +2044,11 @@ The project uses ESLint with NX and TypeScript plugins. Key rules:
 - **TypeScript comments**: `@ts-expect-error` allowed with description (minimum 3 characters), `@ts-ignore` discouraged
 - **Accessibility**: All components must pass AXE checks and WCAG AA standards
 - **Console statements**: Remove all debug console statements before committing
+    - Use `console.warn()` for developer warnings (invalid inputs, deprecated usage)
+    - Use `console.debug()` for debug-mode output (guarded by `if (config.debug)`)
+    - Avoid `console.log()` in production code
 - **No unused variables**: All declared variables must be used
-- **Prefix private memvers**: Only private members must be prefixed with `_`
+- **Prefix private members**: Only private members must be prefixed with `_`
 
 ### Testing Requirements
 
@@ -1814,3 +2160,12 @@ If you observe abusive, harassing, or otherwise unacceptable behavior, report it
 - Update the docs app when adding new features
 - Follow the documentation guidelines in the project wiki
 - Include accessibility notes for interactive components
+
+### Updating Documentation Examples
+
+When migrating components or making API changes:
+
+1. **Check `libs/docs/<library>/api-files.ts`** - Ensure all exported classes are listed
+2. **Review example components** - Update examples to demonstrate new features or API changes
+3. **Test examples visually** - Run the docs app to verify examples work as expected
+4. **Add explanatory notes** - If behavior is non-obvious (e.g., element width vs viewport width), add inline comments or display text explaining it
PATCH

echo "Gold patch applied."
