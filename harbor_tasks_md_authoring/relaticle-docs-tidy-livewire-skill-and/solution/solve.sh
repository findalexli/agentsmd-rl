#!/usr/bin/env bash
set -euo pipefail

cd /workspace/relaticle

# Idempotency guard
if grep -qF "Before creating a component, check `config/livewire.php` for directory overrides" ".github/skills/livewire-development/SKILL.md" && grep -qF "- Laravel can be deployed using [Laravel Cloud](https://cloud.laravel.com/), whi" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/livewire-development/SKILL.md b/.github/skills/livewire-development/SKILL.md
@@ -18,30 +18,16 @@ Use `search-docs` for detailed Livewire 4 patterns and documentation.
 
 ```bash
 
-# Single-file component (SFC - default in v4)
-
-# Creates: resources/views/components/⚡create-post.blade.php
+# Single-file component (default in v4)
 
 php artisan make:livewire create-post
 
-# Page component (SFC - Full Page in v4)
-
-# Creates: resources/views/pages/⚡create-post.blade.php
-
-php artisan make:livewire pages::create-post
-
-# Multi-file component (MFC)
-
-# Creates: resources/views/components/⚡create-post/create-post.php
-
-#          resources/views/components/⚡create-post/create-post.blade.php
+# Multi-file component
 
 php artisan make:livewire create-post --mfc
 
 # Class-based component (v3 style)
 
-# Creates: app/Livewire/CreatePost.php AND resources/views/livewire/create-post.blade.php
-
 php artisan make:livewire create-post --class
 
 # With namespace
@@ -55,23 +41,18 @@ Use `php artisan livewire:convert create-post` to convert between single-file, m
 
 ### Choosing a Component Format
 
-> **Always follow the project's existing conventions first.** Before creating any component, inspect the project's existing Livewire components to determine the established format (SFC, MFC, or class-based) and directory structure. Check `app/Livewire/`, `resources/views/components/`, and `resources/views/livewire/` for existing components. If the project already uses a consistent format, **use that same format** — even if it differs from the Livewire v4 defaults below. Only fall back to the v4 defaults (SFC in `resources/views/components/`) when no existing convention is established.
-
-Also check `config/livewire.php` for `make_command.type`, `make_command.emoji`, `component_locations`, and `component_namespaces` overrides, which change the default format and where files are stored.
+Before creating a component, check `config/livewire.php` for directory overrides, which change where files are stored. Then, look at existing files in those directories (defaulting to `app/Livewire/` and `resources/views/livewire/`) to match the established convention.
 
 ### Component Format Reference
 
 | Format | Flag | Class Path | View Path |
 |--------|------|------------|-----------|
-| Single-file (SFC) | default | — | `resources/views/components/⚡create-post.blade.php` (PHP + Blade in one file) |
-| Full Page SFC | `pages::name` | — | `resources/views/pages/⚡create-post.blade.php` |
-| Multi-file (MFC) | `--mfc` | `resources/views/components/⚡create-post/create-post.php` | `resources/views/components/⚡create-post/create-post.blade.php` |
+| Single-file (SFC) | default | — | `resources/views/livewire/create-post.blade.php` (PHP + Blade in one file) |
+| Multi-file (MFC) | `--mfc` | `app/Livewire/CreatePost.php` | `resources/views/livewire/create-post.blade.php` |
 | Class-based | `--class` | `app/Livewire/CreatePost.php` | `resources/views/livewire/create-post.blade.php` |
-| View-based | default (Blade-only) | — | `resources/views/components/⚡create-post.blade.php` (Blade-only with functional state) |
-
-> **Important:** The ⚡ prefix shown above is the **default** behavior in Livewire v4 — it is **configurable**. Check `config/livewire.php` for the `make_command.emoji` setting. When `true` (default), always include the ⚡ prefix in filenames you create. When `false`, omit the ⚡ prefix from all paths above.
+| View-based | ⚡ prefix | — | `resources/views/livewire/create-post.blade.php` (Blade-only with functional state) |
 
-Namespaced components map to subdirectories: `make:livewire Posts/CreatePost` creates `resources/views/components/posts/⚡create-post.blade.php` (single-file by default). Use `make:livewire Posts/CreatePost --mfc` for multi-file output at `resources/views/components/posts/⚡create-post/create-post.php` and `resources/views/components/posts/⚡create-post/create-post.blade.php`.
+Namespaced components map to subdirectories: `make:livewire Posts/CreatePost` creates files at `app/Livewire/Posts/CreatePost.php` and `resources/views/livewire/posts/create-post.blade.php`.
 
 ### Single-File Component Example
 
@@ -87,7 +68,7 @@ new class extends Component {
     {
         $this->count++;
     }
-};
+}
 ?>
 
 <div>
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -295,12 +295,6 @@ This project has domain-specific skills available. You MUST activate the relevan
 - Prefer PHPDoc blocks over inline comments. Only add inline comments for exceptionally complex logic.
 - Use array shape type definitions in PHPDoc blocks.
 
-=== deployments rules ===
-
-# Deployment
-
-- Laravel can be deployed using [Laravel Cloud](https://cloud.laravel.com/), which is the fastest way to deploy and scale production Laravel applications.
-
 === herd rules ===
 
 # Laravel Herd
@@ -345,6 +339,10 @@ This project has domain-specific skills available. You MUST activate the relevan
 
 - If you receive an "Illuminate\Foundation\ViteException: Unable to locate file in Vite manifest" error, you can run `npm run build` or ask the user to run `npm run dev` or `composer run dev`.
 
+## Deployment
+
+- Laravel can be deployed using [Laravel Cloud](https://cloud.laravel.com/), which is the fastest way to deploy and scale production Laravel applications.
+
 === laravel/v12 rules ===
 
 # Laravel 12
@@ -542,9 +540,5 @@ livewire(ListUsers::class)
 
 - **Never assume public file visibility.** File visibility is `private` by default. Always use `->visibility('public')` when public access is needed.
 - **Never assume full-width layout.** `Grid`, `Section`, and `Fieldset` do not span all columns by default. Explicitly set column spans when needed.
-- **Use correct property types when overriding Page, Resource, and Widget properties.** These properties have union types or changed modifiers that must be preserved:
-  - `$navigationIcon`: `protected static string | BackedEnum | null` (not `?string`)
-  - `$navigationGroup`: `protected static string | UnitEnum | null` (not `?string`)
-  - `$view`: `protected string` (not `protected static string`) on Page and Widget classes
 
 </laravel-boost-guidelines>
PATCH

echo "Gold patch applied."
