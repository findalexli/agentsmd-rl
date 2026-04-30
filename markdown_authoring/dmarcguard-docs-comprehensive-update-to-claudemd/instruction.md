# docs: comprehensive update to CLAUDE.md

Source: [dmarcguardhq/dmarcguard#71](https://github.com/dmarcguardhq/dmarcguard/pull/71)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Update Go version to 1.25+ (dynamic reference to go.mod)
- Add new internal packages: logger, mcp, mcp/oauth, metrics
- Document MCP server with stdio and HTTP/SSE transport support
- Document OAuth2 authentication for MCP HTTP endpoints
- Add Prometheus metrics documentation with key metrics
- Update project structure with all new directories and files
- Add deployment options: DigitalOcean, Dokploy, Coolify, CapRover
- Document Grafana dashboard and provisioning
- Add CLI flags table with environment variable mappings
- Update frontend components structure (dashboard/, tools/)
- Add MCP tools reference table
- Add architecture notes section

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
