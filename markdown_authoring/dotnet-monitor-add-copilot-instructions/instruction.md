# Add Copilot instructions

Source: [dotnet/dotnet-monitor#8972](https://github.com/dotnet/dotnet-monitor/pull/8972)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

###### Summary

Adds `.github/copilot-instructions.md` to provide repository context to GitHub Copilot coding agents. The file documents:

- **Tech stack**: C#, .NET 10.0, ASP.NET Core 8.0/9.0/10.0, xUnit, MSBuild with Arcade SDK
- **Build/test**: Platform-specific commands (`./build.sh`, `.\Build.cmd`, etc.)
- **C# conventions**: Explicit types (no `var`), block-scoped namespaces, required license headers, expression-bodied member rules from `.editorconfig`
- **Repository structure**: Key directories and their purposes
- **Common patterns**: Options pattern, IEgressProvider extensions, collection rule implementations
- **Security**: MSRC reporting process, API key authentication requirements

This enables Copilot to generate code that aligns with repository standards without additional prompting.

<!-- A single line description of the changes for the release notes. It will automatically be formatted correctly and linked to this PR. Leave blank if not needed.-->
###### Release Notes Entry

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by firewall rules:
>
> - `gh.io`
>   - Triggering command: `/home/REDACTED/work/_temp/ghcca-node/node/bin/node /home/REDACTED/work/_temp/ghcca-node/node/bin/node --enable-source-maps /home/REDACTED/work/_temp/copilot-developer-action-main/dist/index.js` (dns block)
>
> If you need me to

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
