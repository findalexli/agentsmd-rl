# Add .github/copilot-instructions.md for Copilot cloud agent onboarding

Source: [nanoframework/nanoFramework.IoT.Device#1508](https://github.com/nanoframework/nanoFramework.IoT.Device/pull/1508)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds agent instructions to help Copilot cloud agent work efficiently in this repo from a cold start, covering the key nanoFramework-specific constraints and conventions that differ from standard .NET.

## What's documented

- **nanoFramework runtime constraints** — no `Console` (use `Debug.WriteLine`), no generic collections, no multidimensional arrays, `SpanByte` instead of `Span<byte>`, limited enum API surface
- **Project structure** — `.nfproj`/`.sln`/`.nuspec`/`packages.config`/`version.json`/`category.txt` per device; required files for a new binding
- **Build system** — Windows-only MSBuild + nanoFramework project system; `dotnet build`/`dotnet restore` do **not** work on `.nfproj` files; CI is Azure Pipelines, not GitHub Actions
- **Conventions** — file license headers, assembly naming (`Iot.Device.<Name>`), strong-name signing with shared `key.snk`, StyleCop enforcement, mandatory XML doc comments
- **I2C pattern for ESP32** — always `Configuration.SetPinFunction(Gpio.IO21/IO22, ...)` before creating `I2cDevice`; GPIO21=SDA, GPIO22=SCL for bus 1
- **Unit testing** — `nanoFramework.TestFramework` attributes (`[TestClass]`, `[TestMethod]`, `[Setup]`), `nano.runsettings` with `IsRealHardware=False` for emulator runs
- **Cross-device dependencies** — NFC devices depend on `Card.sln`; Mpu9250 depends on Ak8963
- **Known errors and workarounds** — `dotnet` toolchain failures on `.nfproj`, StyleCop build errors, NuGet locked-mode restore issues

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
