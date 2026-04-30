#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-toolkit

# Idempotency guard
if grep -qF "| union types, intersection types, DNF, enums, readonly, named arguments, match " "skills/php-quality/SKILL.md" && grep -qF "> **Scope**: Idiomatic patterns for Laravel and Symfony. Covers Eloquent scopes," "skills/php-quality/references/framework-idioms.md" && grep -qF "> **Scope**: PHP 8.0, 8.1, and 8.2 language features relevant to code quality re" "skills/php-quality/references/modern-php-features.md" && grep -qF "Alternative to PHPStan with taint analysis for security-sensitive code paths. Sh" "skills/php-quality/references/quality-tools.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/php-quality/SKILL.md b/skills/php-quality/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: php-quality
 description: "PHP code quality: PSR standards, strict types, framework idioms."
-version: 1.0.0
+version: 1.1.0
 user-invocable: false
 context: fork
 agent: php-general-engineer
@@ -17,334 +17,72 @@ routing:
 
 # PHP Quality Skill
 
-## Strict Types Declaration
+PHP code quality enforcement: strict types, PSR-12 compliance, modern language features, framework idioms, and static analysis tooling.
 
-Every PHP file must begin with `declare(strict_types=1)`. This enforces scalar type coercion rules, catching type errors at call time instead of silently converting values.
+## Reference Loading Table
 
-```php
-<?php
+| Signal | Reference | Size |
+|--------|-----------|------|
+| union types, intersection types, DNF, enums, readonly, named arguments, match expression, null-safe operator, PHP 8.0, PHP 8.1, PHP 8.2 | `references/modern-php-features.md` | ~160 lines |
+| Laravel, Eloquent, Collections, Service Container, Symfony, DI attributes, Event Dispatcher, framework | `references/framework-idioms.md` | ~70 lines |
+| PHP-CS-Fixer, PHPStan, Psalm, Rector, static analysis, CI, linting, code style, taint analysis | `references/quality-tools.md` | ~60 lines |
 
-declare(strict_types=1);
+**Load greedily.** If the user's question touches any signal keyword, load the matching reference before responding. Multiple signals matching = load all matching references.
 
-// Without strict_types: strlen(123) silently returns 3
-// With strict_types: strlen(123) throws TypeError
-```
+---
 
-This is non-negotiable. Omitting it is a code quality defect.
+## Core Rules (Always Apply)
 
-## PSR-12 Coding Standard
+### Strict Types Declaration
 
-PSR-12 extends PSR-1 and PSR-2 as the accepted PHP coding style.
+Every PHP file must begin with `declare(strict_types=1)`. This enforces scalar type coercion rules, catching type errors at call time instead of silently converting values.
 
 ```php
 <?php
 
 declare(strict_types=1);
 
-namespace App\Service;
-
-use App\Repository\UserRepository;
-use Psr\Log\LoggerInterface;
-
-class UserService
-{
-    // Visibility required on all properties, methods, constants
-    private const MAX_RETRIES = 3;
-
-    public function __construct(
-        private readonly UserRepository $repository,
-        private readonly LoggerInterface $logger,
-    ) {
-    }
-
-    public function findActiveUsers(int $limit = 50): array
-    {
-        // Opening braces on same line for control structures
-        if ($limit <= 0) {
-            throw new \InvalidArgumentException('Limit must be positive');
-        }
-
-        // Opening braces on next line for classes and methods (shown above)
-        return $this->repository->findActive($limit);
-    }
-}
-```
-
-Key rules: 4-space indentation, no trailing whitespace, one class per file, `use` statements after namespace with a blank line before and after, visibility on everything.
-
-## Type Declarations
-
-### Union Types (PHP 8.0)
-
-```php
-function parseId(int|string $id): User
-{
-    return match (true) {
-        is_int($id)    => $this->findById($id),
-        is_string($id) => $this->findBySlug($id),
-    };
-}
-```
-
-### Intersection Types (PHP 8.1)
-
-```php
-function processItem(Countable&Iterator $collection): void
-{
-    // $collection must implement BOTH interfaces
-    foreach ($collection as $item) {
-        // ...
-    }
-}
-```
-
-### DNF Types — Disjunctive Normal Form (PHP 8.2)
-
-```php
-function handle((Countable&Iterator)|null $items): void
-{
-    // Combines union and intersection: (A&B)|C
-    if ($items === null) {
-        return;
-    }
-    // ...
-}
-```
-
-## Enums (PHP 8.1)
-
-### Backed Enums
-
-```php
-enum Status: string
-{
-    case Active   = 'active';
-    case Inactive = 'inactive';
-    case Pending  = 'pending';
-
-    // Enums can have methods
-    public function label(): string
-    {
-        return match ($this) {
-            self::Active   => 'Active',
-            self::Inactive => 'Inactive',
-            self::Pending  => 'Pending Review',
-        };
-    }
-
-    // And implement interfaces
-    public function isTerminal(): bool
-    {
-        return $this === self::Inactive;
-    }
-}
-
-// Usage
-$status = Status::from('active');        // throws ValueError if invalid
-$status = Status::tryFrom('unknown');    // returns null if invalid
-$value  = Status::Active->value;         // 'active'
-```
-
-Backed enums can be `string` or `int`. Use them instead of class constants for fixed value sets.
-
-## Readonly Properties and Classes (PHP 8.1 / 8.2)
-
-```php
-// Readonly properties (PHP 8.1) — set once, immutable after
-class Money
-{
-    public function __construct(
-        public readonly int $amount,
-        public readonly string $currency,
-    ) {
-    }
-}
-
-// Readonly classes (PHP 8.2) — all properties are implicitly readonly
-readonly class Coordinate
-{
-    public function __construct(
-        public float $latitude,
-        public float $longitude,
-    ) {
-    }
-}
-
-$c = new Coordinate(37.7749, -122.4194);
-// $c->latitude = 0; // Error: Cannot modify readonly property
-```
-
-## Named Arguments (PHP 8.0)
-
-Named arguments improve readability for functions with many parameters or boolean flags.
-
-```php
-// Before: positional arguments — what does true mean?
-$user = createUser('Alice', 'alice@example.com', true, false);
-
-// After: named arguments — intent is clear
-$user = createUser(
-    name: 'Alice',
-    email: 'alice@example.com',
-    isAdmin: true,
-    sendWelcomeEmail: false,
-);
-
-// Named arguments can skip optional parameters
-htmlspecialchars($string, encoding: 'UTF-8');
-```
-
-## Match Expressions (PHP 8.0)
-
-`match` is a stricter alternative to `switch`. It uses strict comparison (`===`), returns a value, and throws `UnhandledMatchError` for missing cases.
-
-```php
-// switch — loose comparison, fall-through risk, verbose
-switch ($statusCode) {
-    case 200:
-        $text = 'OK';
-        break;
-    case 404:
-        $text = 'Not Found';
-        break;
-    default:
-        $text = 'Unknown';
-}
-
-// match — strict comparison, no fall-through, expression
-$text = match ($statusCode) {
-    200     => 'OK',
-    301     => 'Moved Permanently',
-    404     => 'Not Found',
-    500     => 'Internal Server Error',
-    default => 'Unknown',
-};
-
-// match with no subject — replaces if/elseif chains
-$category = match (true) {
-    $age < 13  => 'child',
-    $age < 18  => 'teen',
-    $age < 65  => 'adult',
-    default    => 'senior',
-};
-```
-
-## Null Safe Operator (PHP 8.0)
-
-The `?->` operator short-circuits to `null` when the left side is null, eliminating nested null checks.
-
-```php
-// Before: defensive null checking
-$country = null;
-if ($user !== null) {
-    $address = $user->getAddress();
-    if ($address !== null) {
-        $country = $address->getCountry();
-    }
-}
-
-// After: nullsafe chaining
-$country = $user?->getAddress()?->getCountry();
-
-// Combine with null coalescing for defaults
-$countryCode = $user?->getAddress()?->getCountry()?->code ?? 'US';
-```
-
-## Laravel Idioms
-
-### Eloquent
-
-```php
-// Scopes for reusable query constraints
-class User extends Model
-{
-    public function scopeActive(Builder $query): Builder
-    {
-        return $query->where('active', true);
-    }
-}
-
-// Usage: User::active()->where('role', 'admin')->get();
-```
-
-### Collections
-
-```php
-// Prefer collection methods over raw loops
-$names = collect($users)
-    ->filter(fn (User $u) => $u->isActive())
-    ->map(fn (User $u) => $u->fullName())
-    ->sort()
-    ->values()
-    ->all();
-```
-
-### Service Container
-
-```php
-// Bind interface to implementation in a ServiceProvider
-$this->app->bind(PaymentGateway::class, StripeGateway::class);
-
-// Contextual binding
-$this->app->when(OrderService::class)
-    ->needs(PaymentGateway::class)
-    ->give(StripeGateway::class);
+// Without strict_types: strlen(123) silently returns 3
+// With strict_types: strlen(123) throws TypeError
 ```
 
-## Symfony Idioms
-
-### Dependency Injection with Attributes
+This is non-negotiable. Omitting it is a code quality defect.
 
-```php
-use Symfony\Component\DependencyInjection\Attribute\Autowire;
+### PSR-12 Coding Standard
 
-class ReportGenerator
-{
-    public function __construct(
-        private readonly ReportRepository $repository,
-        #[Autowire('%kernel.project_dir%/var/reports')]
-        private readonly string $outputDir,
-    ) {
-    }
-}
-```
+PSR-12 extends PSR-1 and PSR-2 as the accepted PHP coding style. Key rules:
 
-### Event Dispatcher
+- 4-space indentation, no trailing whitespace
+- One class per file
+- `use` statements after namespace with a blank line before and after
+- Visibility required on all properties, methods, and constants
+- Opening braces on same line for control structures
+- Opening braces on next line for classes and methods
 
-```php
-use Symfony\Component\EventDispatcher\Attribute\AsEventListener;
+---
 
-#[AsEventListener(event: OrderPlaced::class)]
-class SendOrderConfirmation
-{
-    public function __invoke(OrderPlaced $event): void
-    {
-        // Send confirmation email for $event->orderId
-    }
-}
-```
+## Phase 1: ASSESS
 
-## Quality Enforcement
+Determine what kind of PHP quality review is needed:
 
-Run these tools in CI:
+| Request type | Load references | Action |
+|-------------|----------------|--------|
+| Code review | All three | Full quality pass |
+| Type system question | `modern-php-features.md` | Feature-specific guidance |
+| Framework patterns | `framework-idioms.md` | Idiomatic pattern review |
+| Tooling setup | `quality-tools.md` | Config and CI guidance |
 
-```bash
-# PHP-CS-Fixer — auto-fix PSR-12 violations
-./vendor/bin/php-cs-fixer fix --dry-run --diff
+**Gate**: Request classified and relevant references loaded.
 
-# PHPStan — static analysis (level 0-9, aim for 6+)
-./vendor/bin/phpstan analyse src --level=6
+---
 
-# Psalm — alternative static analysis
-./vendor/bin/psalm --show-info=true
+## Phase 2: REVIEW
 
-# Rector — automated refactoring and upgrades
-./vendor/bin/rector process src --dry-run
-```
+Apply loaded reference knowledge to the user's code or question. Every review checks:
+1. `declare(strict_types=1)` present
+2. PSR-12 compliance
+3. Modern PHP features used where appropriate (from references)
+4. Framework idioms followed (if applicable)
+5. Quality tooling configured (if applicable)
 
-| Tool | Purpose | Config File |
-|---|---|---|
-| PHP-CS-Fixer | Code style enforcement | `.php-cs-fixer.dist.php` |
-| PHPStan | Static analysis, type checking | `phpstan.neon` |
-| Psalm | Static analysis, taint analysis | `psalm.xml` |
-| Rector | Automated refactoring | `rector.php` |
+**Gate**: Specific, reference-backed feedback provided.
diff --git a/skills/php-quality/references/framework-idioms.md b/skills/php-quality/references/framework-idioms.md
@@ -0,0 +1,83 @@
+# Framework Idioms Reference
+
+> **Scope**: Idiomatic patterns for Laravel and Symfony. Covers Eloquent scopes, Collections, Service Container binding, Symfony DI attributes, and Event Dispatcher. Does NOT cover raw PHP patterns without a framework or quality tooling configuration.
+> **Version range**: Laravel 10+, Symfony 6.2+
+> **Generated**: 2026-04-16
+
+---
+
+## Laravel Idioms
+
+### Eloquent
+
+```php
+// Scopes for reusable query constraints
+class User extends Model
+{
+    public function scopeActive(Builder $query): Builder
+    {
+        return $query->where('active', true);
+    }
+}
+
+// Usage: User::active()->where('role', 'admin')->get();
+```
+
+### Collections
+
+```php
+// Prefer collection methods over raw loops
+$names = collect($users)
+    ->filter(fn (User $u) => $u->isActive())
+    ->map(fn (User $u) => $u->fullName())
+    ->sort()
+    ->values()
+    ->all();
+```
+
+### Service Container
+
+```php
+// Bind interface to implementation in a ServiceProvider
+$this->app->bind(PaymentGateway::class, StripeGateway::class);
+
+// Contextual binding
+$this->app->when(OrderService::class)
+    ->needs(PaymentGateway::class)
+    ->give(StripeGateway::class);
+```
+
+---
+
+## Symfony Idioms
+
+### Dependency Injection with Attributes
+
+```php
+use Symfony\Component\DependencyInjection\Attribute\Autowire;
+
+class ReportGenerator
+{
+    public function __construct(
+        private readonly ReportRepository $repository,
+        #[Autowire('%kernel.project_dir%/var/reports')]
+        private readonly string $outputDir,
+    ) {
+    }
+}
+```
+
+### Event Dispatcher
+
+```php
+use Symfony\Component\EventDispatcher\Attribute\AsEventListener;
+
+#[AsEventListener(event: OrderPlaced::class)]
+class SendOrderConfirmation
+{
+    public function __invoke(OrderPlaced $event): void
+    {
+        // Send confirmation email for $event->orderId
+    }
+}
+```
diff --git a/skills/php-quality/references/modern-php-features.md b/skills/php-quality/references/modern-php-features.md
@@ -0,0 +1,197 @@
+# Modern PHP Features Reference
+
+> **Scope**: PHP 8.0, 8.1, and 8.2 language features relevant to code quality reviews: type system improvements, enums, readonly, match expressions, named arguments, null-safe operator. Does NOT cover framework-specific patterns or tooling configuration.
+> **Version range**: PHP 8.0 through 8.2
+> **Generated**: 2026-04-16
+
+---
+
+## Type Declarations
+
+### Union Types (PHP 8.0)
+
+```php
+function parseId(int|string $id): User
+{
+    return match (true) {
+        is_int($id)    => $this->findById($id),
+        is_string($id) => $this->findBySlug($id),
+    };
+}
+```
+
+### Intersection Types (PHP 8.1)
+
+```php
+function processItem(Countable&Iterator $collection): void
+{
+    // $collection must implement BOTH interfaces
+    foreach ($collection as $item) {
+        // ...
+    }
+}
+```
+
+### DNF Types (PHP 8.2)
+
+Disjunctive Normal Form combines union and intersection types.
+
+```php
+function handle((Countable&Iterator)|null $items): void
+{
+    // Combines union and intersection: (A&B)|C
+    if ($items === null) {
+        return;
+    }
+    // ...
+}
+```
+
+---
+
+## Enums (PHP 8.1)
+
+### Backed Enums
+
+```php
+enum Status: string
+{
+    case Active   = 'active';
+    case Inactive = 'inactive';
+    case Pending  = 'pending';
+
+    // Enums can have methods
+    public function label(): string
+    {
+        return match ($this) {
+            self::Active   => 'Active',
+            self::Inactive => 'Inactive',
+            self::Pending  => 'Pending Review',
+        };
+    }
+
+    // And implement interfaces
+    public function isTerminal(): bool
+    {
+        return $this === self::Inactive;
+    }
+}
+
+// Usage
+$status = Status::from('active');        // throws ValueError if invalid
+$status = Status::tryFrom('unknown');    // returns null if invalid
+$value  = Status::Active->value;         // 'active'
+```
+
+Backed enums can be `string` or `int`. Use them instead of class constants for fixed value sets.
+
+---
+
+## Readonly Properties and Classes (PHP 8.1 / 8.2)
+
+```php
+// Readonly properties (PHP 8.1) — set once, immutable after
+class Money
+{
+    public function __construct(
+        public readonly int $amount,
+        public readonly string $currency,
+    ) {
+    }
+}
+
+// Readonly classes (PHP 8.2) — all properties are implicitly readonly
+readonly class Coordinate
+{
+    public function __construct(
+        public float $latitude,
+        public float $longitude,
+    ) {
+    }
+}
+
+$c = new Coordinate(37.7749, -122.4194);
+// $c->latitude = 0; // Error: Cannot modify readonly property
+```
+
+---
+
+## Named Arguments (PHP 8.0)
+
+Named arguments improve readability for functions with many parameters or boolean flags.
+
+```php
+// Before: positional arguments — what does true mean?
+$user = createUser('Alice', 'alice@example.com', true, false);
+
+// After: named arguments — intent is clear
+$user = createUser(
+    name: 'Alice',
+    email: 'alice@example.com',
+    isAdmin: true,
+    sendWelcomeEmail: false,
+);
+
+// Named arguments can skip optional parameters
+htmlspecialchars($string, encoding: 'UTF-8');
+```
+
+---
+
+## Match Expressions (PHP 8.0)
+
+`match` is a stricter alternative to `switch`. It uses strict comparison (`===`), returns a value, and throws `UnhandledMatchError` for missing cases.
+
+```php
+// switch — loose comparison, fall-through risk, verbose
+switch ($statusCode) {
+    case 200:
+        $text = 'OK';
+        break;
+    case 404:
+        $text = 'Not Found';
+        break;
+    default:
+        $text = 'Unknown';
+}
+
+// match — strict comparison, no fall-through, expression
+$text = match ($statusCode) {
+    200     => 'OK',
+    301     => 'Moved Permanently',
+    404     => 'Not Found',
+    500     => 'Internal Server Error',
+    default => 'Unknown',
+};
+
+// match with no subject — replaces if/elseif chains
+$category = match (true) {
+    $age < 13  => 'child',
+    $age < 18  => 'teen',
+    $age < 65  => 'adult',
+    default    => 'senior',
+};
+```
+
+---
+
+## Null Safe Operator (PHP 8.0)
+
+The `?->` operator short-circuits to `null` when the left side is null, eliminating nested null checks.
+
+```php
+// Before: defensive null checking
+$country = null;
+if ($user !== null) {
+    $address = $user->getAddress();
+    if ($address !== null) {
+        $country = $address->getCountry();
+    }
+}
+
+// After: nullsafe chaining
+$country = $user?->getAddress()?->getCountry();
+
+// Combine with null coalescing for defaults
+$countryCode = $user?->getAddress()?->getCountry()?->code ?? 'US';
+```
diff --git a/skills/php-quality/references/quality-tools.md b/skills/php-quality/references/quality-tools.md
@@ -0,0 +1,52 @@
+# Quality Tools Reference
+
+> **Scope**: PHP code quality tool configuration and usage: PHP-CS-Fixer, PHPStan, Psalm, Rector. Covers CI integration commands, config files, and recommended strictness levels. Does NOT cover language features or framework patterns.
+> **Version range**: PHP-CS-Fixer 3.x, PHPStan 1.x, Psalm 5.x, Rector 1.x
+> **Generated**: 2026-04-16
+
+---
+
+## CI Commands
+
+Run these tools in CI:
+
+```bash
+# PHP-CS-Fixer — auto-fix PSR-12 violations
+./vendor/bin/php-cs-fixer fix --dry-run --diff
+
+# PHPStan — static analysis (level 0-9, aim for 6+)
+./vendor/bin/phpstan analyse src --level=6
+
+# Psalm — alternative static analysis
+./vendor/bin/psalm --show-info=true
+
+# Rector — automated refactoring and upgrades
+./vendor/bin/rector process src --dry-run
+```
+
+---
+
+## Tool Reference
+
+| Tool | Purpose | Config File |
+|------|---------|-------------|
+| PHP-CS-Fixer | Code style enforcement | `.php-cs-fixer.dist.php` |
+| PHPStan | Static analysis, type checking | `phpstan.neon` |
+| Psalm | Static analysis, taint analysis | `psalm.xml` |
+| Rector | Automated refactoring | `rector.php` |
+
+### PHP-CS-Fixer
+
+Enforces PSR-12 and custom code style rules. Config file `.php-cs-fixer.dist.php` defines rulesets. Use `--dry-run --diff` in CI to detect violations without modifying files. Run `fix` locally to auto-correct.
+
+### PHPStan
+
+Static analysis with levels 0 through 9. Level 6 is the recommended minimum for production code: it covers method return types, property types, and dead code detection. Higher levels add strictness around mixed types and dynamic property access.
+
+### Psalm
+
+Alternative to PHPStan with taint analysis for security-sensitive code paths. Shows data flow from user input to dangerous sinks (SQL queries, shell commands, file operations). Use `--show-info=true` to surface non-error findings like unused variables.
+
+### Rector
+
+Automated refactoring engine. Upgrades PHP syntax to target version (e.g., converting `switch` to `match`, adding property promotion). Always run with `--dry-run` first in CI to preview changes.
PATCH

echo "Gold patch applied."
