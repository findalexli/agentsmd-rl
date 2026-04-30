# docs: update CLAUDE.md (#1318) [no ci]

Source: [ShokoAnime/ShokoServer#1318](https://github.com/ShokoAnime/ShokoServer/pull/1318)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## 1. `var` preference corrected
**Before:** "`var` when type is apparent"
**After:** "`var` preferred everywhere" with all three editorconfig settings listed

**Why:** The `.editorconfig` sets `csharp_style_var_elsewhere`, `csharp_style_var_for_built_in_types`, and `csharp_style_var_when_type_is_apparent` all to `true` (enforced as warnings in `src/` paths). The original phrasing implied a narrower preference than what's actually enforced.

---

## 2. Added naming conventions
**Added:** `_camelCase` for instance/static fields, `PascalCase` for methods/classes/properties, `camelCase` for locals/parameters

**Why:** These are explicitly defined in `.editorconfig` via `dotnet_naming_rule` entries but were missing from the docs.

---

## 3. Fixed `Shoko.CLI` description
**Before:** "Hosts `SystemService` as `IHostedService`"
**After:** "Instantiates and manages `SystemService` directly"

**Why:** `SystemService` does **not** implement `IHostedService`. Both entry points (`Shoko.CLI/Program.cs` and `Shoko.TrayService/Program.cs`) create `new SystemService()` directly, which internally builds and starts the `IHost`.

---

## 4. Added explicit entry point paths to Startup Sequence
**Added:** "Entry points: `Shoko.CLI/Program.cs` (headless) or `Shoko.TrayService/Program.cs` (tray app). Both instantiate `new SystemService()` directly, which internally builds and starts the `IHost`."

**Why:** There is no `Program.cs` in `Shoko.Server/`. The original "Program

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
