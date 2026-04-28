#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cms

# Idempotency guard
if grep -qF "description: Guidance for writing and updating Craft CMS 6 tests (Pest/Laravel) " ".agents/skills/testing-guidelines/SKILL.md" && grep -qF "When testing element traits/concerns, create a minimal test element class that e" ".agents/skills/testing-guidelines/references/testing-guidelines.md" && grep -qF "- **Classes marked `final` have this keyword stripped during testing** - you can" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/testing-guidelines/SKILL.md b/.agents/skills/testing-guidelines/SKILL.md
@@ -0,0 +1,33 @@
+---
+name: testing-guidelines
+description: Guidance for writing and updating Craft CMS 6 tests (Pest/Laravel) including element factories, CP URL rules, custom field setup, trait testing, and event assertions. Use when creating or modifying tests, debugging test patterns, or aligning new tests with repository testing standards.
+---
+
+# Testing Guidelines
+
+## Overview
+
+Apply Craft CMS 6 testing patterns consistently and avoid common pitfalls around elements, CP URLs, and event assertions. Use the quick rules below, then load the reference file for full examples and code snippets.
+
+## Workflow
+
+1. Identify the test scope (CP URL, element behavior, trait, event, custom field).
+2. Follow the matching rule set below.
+3. Pull detailed examples from `references/testing-guidelines.md` when needed.
+4. Implement tests using Pest and repo conventions.
+
+## Core Rules
+
+- Use `CraftCms\Cms\Cms::config()->cpTrigger` when asserting CP URLs; never hard-code `/admin`.
+- Do not instantiate element classes directly with `new` in tests; use factories to ensure database state.
+- Prefer factories and element queries over Eloquent models when asserting element behavior.
+- For element traits, create minimal test elements that override only what is needed.
+- Use Laravel event fakes/listeners to assert dispatch, cancellation, or data changes.
+
+## When to Load References
+
+- Need code samples for entry creation, custom fields, or event tests.
+- Need the minimal trait-testing element example.
+- Unsure about the exact factory + query pattern for elements.
+
+See `references/testing-guidelines.md` for full examples and snippets.
diff --git a/.agents/skills/testing-guidelines/references/testing-guidelines.md b/.agents/skills/testing-guidelines/references/testing-guidelines.md
@@ -0,0 +1,163 @@
+# Testing Guidelines Reference
+
+## Table of Contents
+
+1. CP URLs
+2. Elements
+3. Creating test elements
+4. Creating an entry with a custom field
+5. Testing element concerns (traits)
+6. Testing Laravel events
+
+## CP URLs
+
+- When testing CP URLs, always use `CraftCms\Cms\Cms::config()->cpTrigger` instead of testing for `/admin`.
+
+## Elements
+
+Important: Do not instantiate element classes directly with `new Entry()` in tests. Use factories to ensure proper database state.
+
+## Creating test elements
+
+```php
+use CraftCms\Cms\Entry\Elements\Entry as EntryElement;
+use CraftCms\Cms\Entry\Models\Entry;
+use CraftCms\Cms\User\Elements\User;
+use function Pest\Laravel\actingAs;
+
+// Authenticate as user (required for most element operations)
+actingAs(User::findOne());
+
+// Create an entry using the Eloquent model factory, then query the element
+Entry::factory()->create();
+$entry = EntryElement::findOne();
+
+// With specific attributes
+Entry::factory()->create(['title' => 'Test Entry']);
+```
+
+## Creating an entry with a custom field
+
+```php
+use craft\behaviors\CustomFieldBehavior;
+use CraftCms\Cms\Field\Models\Field;
+use CraftCms\Cms\FieldLayout\Models\FieldLayout;
+use CraftCms\Cms\Entry\Models\Entry as EntryModel;
+use CraftCms\Cms\Support\Facades\Fields;
+
+$field = Field::factory()->create([
+    'handle' => 'textField',
+    'type' => CraftCms\Cms\Field\PlainText::class,
+]);
+
+$fieldLayout = FieldLayout::factory()->forField($field)->create();
+$entry = EntryModel::factory()->create();
+
+$entry->element->update([
+    'fieldLayoutId' => $fieldLayout->id,
+]);
+
+CustomFieldBehavior::$fieldHandles[$field->handle] = true;
+Fields::refreshFields();
+
+$entry = entryQuery()->id($entry->id)->firstOrFail();
+$entry->title = 'Test entry';
+$entry->setFieldValue('textField', 'Foo');
+
+Craft::$app->getElements()->saveElement($entry);
+```
+
+## Testing element concerns (traits)
+
+When testing element traits/concerns, create a minimal test element class that extends `Element` and overrides only the methods you need to test:
+
+```php
+use CraftCms\Cms\Element\Element;
+
+class TestRoutableElement extends Element
+{
+    protected ?string $customRoute = null;
+
+    #[Override]
+    public static function displayName(): string
+    {
+        return 'Test Element';
+    }
+
+    public function setCustomRoute(?string $route): void
+    {
+        $this->customRoute = $route;
+    }
+
+    #[Override]
+    protected function route(): array|string|null
+    {
+        return $this->customRoute;
+    }
+}
+
+test('returns custom route', function () {
+    $element = new TestRoutableElement;
+    $element->setCustomRoute('my/route');
+
+    expect($element->getRoute())->toBe('my/route');
+});
+```
+
+This pattern allows testing trait behavior without needing factories or database state. See `tests/Element/Concerns/` for examples.
+
+## Testing Laravel events
+
+Use Laravel's event fakes to test that events are dispatched correctly:
+
+```php
+use CraftCms\Cms\Element\Events\BeforeSave;
+use CraftCms\Cms\Element\Events\AfterSave;
+use Illuminate\Support\Facades\Event;
+
+test('dispatches save events', function () {
+    Event::fake([BeforeSave::class, AfterSave::class]);
+
+    $entry = Entry::factory()->create();
+    $element = entryQuery()->id($entry->id)->one();
+
+    Craft::$app->getElements()->saveElement($element);
+
+    Event::assertDispatched(BeforeSave::class, function ($event) use ($element) {
+        return $event->element->id === $element->id;
+    });
+
+    Event::assertDispatched(AfterSave::class);
+});
+```
+
+Testing cancellable events:
+
+```php
+test('can cancel save via event', function () {
+    Event::listen(BeforeSave::class, function (BeforeSave $event) {
+        $event->isValid = false;
+    });
+
+    $entry = Entry::factory()->create();
+    $element = entryQuery()->id($entry->id)->one();
+
+    $result = Craft::$app->getElements()->saveElement($element);
+
+    expect($result)->toBeFalse();
+});
+```
+
+Testing event data modification:
+
+```php
+test('can modify event data', function () {
+    Event::listen(DefineUrl::class, function (DefineUrl $event) {
+        $event->url = 'https://custom-url.com';
+    });
+
+    $element = new TestElement();
+
+    expect($element->getUrl())->toBe('https://custom-url.com');
+});
+```
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,221 @@
+# AGENTS.md
+
+This file provides guidance to AI Coding agents when working with code in this repository.
+
+## Overview
+
+This is the Craft CMS 6.x repository. Craft CMS 6 is a major rewrite that migrates from Yii2 to Laravel 12 while maintaining backwards compatibility through a Yii2 adapter layer.
+
+## Common Commands
+
+### Testing
+```bash
+# Run all tests (uses Pest)
+composer tests
+
+# Run a specific test file
+./vendor/bin/pest --compact tests/Field/FieldTest.php
+
+# Run a specific test
+./vendor/bin/pest --compact --filter="test name"
+
+# Run yii2-adapter Laravel tests
+composer tests-adapter
+
+# Run yii2-adapter legacy tests (in the yii2-adapter directory)
+./vendor/bin/codecept run unit --filter="test name"
+```
+
+
+- When running tests with `./vendor/bin/pest`, always add `--compact` to reduce output verbosity and token count.
+- When writing tests, don't use Mockery or Mocks unless absolutely necessary. Prefer using Laravel's Facade fakes or running real code. Tests written are feature or integration tests and not unit tests.
+
+### Code Quality
+```bash
+# Fix code style (runs rector, pint, and ecs in parallel)
+composer fix-cs
+
+# Run static analysis
+composer phpstan
+
+# Run rector only
+composer rector
+```
+
+### Frontend Development
+```bash
+# Run Vite dev server for control panel assets
+npm run dev
+
+# Build control panel assets for production
+npm run build
+
+# Run web components package in watch mode
+npm run dev:cp
+
+# Build web components for production
+npm run build:cp
+
+# Run tests for @craftcms/cp package
+npm run test:cp
+
+# Build all frontend assets (bundles, cp, main)
+npm run build:all
+```
+
+### Legacy Bundles (yii2-adapter)
+```bash
+npm run build:bundles
+npm run dev:bundles -- -- --config-name=cp
+```
+
+## Architecture
+
+### Laravel + Yii2 Hybrid System
+
+Craft 6 runs on Laravel 12 but maintains backwards compatibility with legacy Yii2 code through `craftcms/yii2-adapter`.
+
+**Key architectural points:**
+- Primary namespace: `CraftCms\Cms\` in `src/`
+- Main service provider: `CraftServiceProvider` (aggregates ~20 domain service providers)
+- Legacy Yii2 app bootstrapped via `Yii2ServiceProvider` which creates `Craft::$app`
+- The `yii2-adapter/` directory is a Composer path repository (`craftcms/yii2-adapter: self.version`)
+- The goal before the next release is to have no Yii code or references in the `src` folder, the `yii2-adapter` provides fallbacks and compatibility layers.
+- This is a large codebase, with large files. Be mindful of file size and search before you read.
+
+### Domain Structure
+
+The codebase is organized by domain in `src/`:
+- `Element/` - Base element system (entries, assets, users are all elements)
+  - `Element/Concerns/` - Traits that compose Element functionality (e.g., `HasRoutesAndUrls`, `Cacheable`, `HasCanonical`)
+- `Entry/` - Entry element type and related services
+- `Field/` - Field types and field layout system
+- `Database/` - Migrations, queries, and the custom `ElementQuery` system
+- `ProjectConfig/` - YAML-based configuration management
+- `Plugin/` - Plugin system and loading
+- `User/` - Authentication, permissions, user groups
+- `Site/` - Multi-site support
+
+### Element Queries
+
+Element queries (`src/Database/Queries/`) are the primary way to query content:
+- `Entry::find()`, `Asset::find()`, `User::find()` return specialized `ElementQuery` objects.
+- `ElementQuery` implements `Illuminate\Contracts\Database\Query\Builder` and forwards calls to a Laravel query builder.
+- Use `joinElementTable(Table::ENTRIES)` to join specialized element tables and gain access to their columns.
+- Support eager loading (`with()`), caching, and custom field queries.
+- Located in `src/Database/Queries/` with concerns in `Concerns/` subdirectory.
+- **Important:** Eloquent classes which are in a `Models` namespace are not usually how content is queries. Use the elements instead if they exist, namespaced in `Elements`.
+
+### Database Patterns
+
+- Use `CraftCms\Cms\Database\Table` constants for all table names (e.g., `Table::ENTRIES`, `Table::ELEMENTS`).
+- Prefer Laravel's schema builder and migrations over raw SQL.
+- When working with elements, always respect the `elements` and `elements_sites` base tables.
+
+### Translations
+
+- Use the `t()` helper function for translations: `t('Settings')`. The second argument is optional and specifies the translation category `app` (default) or `site`.
+- The `t()` helper is a wrapper around `CraftCms\Cms\Support\Facades\I18N::translate()`.
+
+### Configuration
+
+- Craft config: `config/craft/` (general.php, custom-fields.php, etc.)
+- Project config: `config/craft/project/` (YAML files for schema)
+- Laravel config: `config/` (standard Laravel configuration)
+
+### Testing
+
+- Uses Pest with Orchestra Testbench for Laravel package testing
+- Base test class: `CraftCms\Cms\Tests\TestCase`
+- Tests require database - configure via `tests/.env` (copy from `.env.example.mysql` or `.env.example.pgsql`)
+- Uses `RefreshDatabase` trait - tables are migrated fresh via the `Install` migration
+- **Classes marked `final` have this keyword stripped during testing** - you can create custom test classes that extend production classes (e.g., extending `User` element) to override methods like `getFieldLayout()` for easier testing without complex mocks
+
+**Important**: When creating or adjusting tests, take a look at @docs/TESTING.md for patterns and best practices.
+
+### Service Providers Pattern
+
+Each domain has its own service provider (e.g., `FieldsServiceProvider`, `UserServiceProvider`) registered through the aggregate `CraftServiceProvider`.
+
+### Singleton Services
+
+Services that should be singletons use the `#[Singleton]` attribute from Laravel:
+
+```php
+use Illuminate\Container\Attributes\Singleton;
+
+#[Singleton]
+final class MyService
+{
+    public function __construct(
+        private readonly SomeDependency $dependency,
+    ) {}
+}
+```
+
+The service can then be resolved via `app(MyService::class)` and will return the same instance each time.
+
+### Routing
+
+Craft 6 uses Laravel's routing system, coordinated through `src/Route/RouteServiceProvider.php`.
+
+**Route Registration:**
+- `routes/routes.php` is the main entry point for route loading.
+- `routes/actions.php` contains action-style routes (e.g., `actions/users/login`), registered under the `craft.actions.` name prefix.
+- `routes/cp.php` contains Control Panel routes, registered under the `craft.cp.` name prefix and prefixed with the `cpTrigger` config value.
+- `routes/web.php` contains frontend web routes, registered under the `craft.` name prefix.
+
+**Middleware Groups:**
+- `craft`: Base middleware for all Craft requests (locale, schema checks, etc.)
+- `craft.cp`: Middleware specific to Control Panel requests (requires CP request, license checks)
+- `craft.web`: Middleware for frontend web requests
+
+**Dynamic Routing:**
+- **Action Requests:** `HandleActionRequest` middleware dynamically routes requests that use the `action` parameter or the `actions/` URI prefix.
+- **Token Requests:** `HandleTokenRequest` middleware handles requests with a `token` parameter (e.g., for previews).
+- **Project Config Routes:** Dynamic routes defined by users in the Control Panel are loaded from Project Config and registered during the `booted` lifecycle of the application.
+
+### Events
+
+Craft 6 uses Laravel's event system. Events are simple classes with public properties located in `Events/` subdirectories within each domain (e.g., `src/Element/Events/`).
+
+**Laravel Event Pattern:**
+```php
+// Event class (src/Element/Events/BeforeSave.php)
+final class BeforeSave
+{
+    use \CraftCms\Cms\Shared\Concerns\ValidatableEvent; // For cancellable events
+    use \CraftCms\Cms\Shared\Concerns\HandleableEvent; // For events able to be marked as handled
+    
+    public function __construct(
+        public \CraftCms\Cms\Element\Element $element,
+        public bool $isNew,
+    ) {}
+}
+
+// Dispatching the event
+event($event = new BeforeSave($this, $isNew));
+if (!$event->isValid) {
+    return false;
+}
+```
+
+**Yii2 Backwards Compatibility:**
+- Legacy `EVENT_*` constants are maintained in `yii2-adapter/legacy/base/Element.php`
+- The `registerEvents()` method in the yii2-adapter bridges Laravel events to Yii2 handlers
+- When referencing yii2-adapter constants from `src/`, use an alias: `use craft\base\Element as YiiElement;`
+
+**Key directories:**
+- `src/Element/Events/` - Element lifecycle and UI events
+- `src/Entry/Events/` - Entry-specific events
+- `src/User/Events/` - User-related events
+- `src/Plugin/Events/` - Plugin lifecycle events
+
+## Code Style
+
+- Uses Laravel Pint with Laravel preset
+- Rector for automated refactoring (PHP 8.4, Laravel-specific rules)
+- `declare(strict_types=1)` required in all PHP files
+- Final classes by default, `readonly` when possible
+- ECS for yii2-adapter code style
+- You don't need to remove unused imports, running Pint will fix that for you
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
