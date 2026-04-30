# Add .github/copilot-instructions.md for FMD Framework agent onboarding

Source: [edkreuk/FMD_FRAMEWORK#210](https://github.com/edkreuk/FMD_FRAMEWORK/pull/210)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds a `copilot-instructions.md` so cloud agents have immediate, structured context about this repo without needing to rediscover it from scratch each session.

## What's covered

- **Repo layout** — every top-level directory, artifact type, and naming convention
- **Architecture** — workspace separation (Code / Data / Config), pipeline naming patterns (`PL_FMD_LDZ_COMMAND_*`, `PL_FMD_LOAD_*`), Medallion layers and their lakehouses
- **Config database schemas** — `integration`, `execution`, `logging` tables and key stored procedures (notably `sp_UpsertLandingzoneBronzeSilver` for atomic LDZ→Bronze→Silver registration)
- **Notebooks** — purpose of each, shared parameter conventions, AAD-token pyodbc connection pattern used throughout
- **Variable Libraries** — meaning of every variable in `VAR_CONFIG_FMD` and `VAR_FMD`
- **Deployment** — concise walkthrough for both FMD Framework and Business Domain setup notebooks; what `config/item_config.yaml` is
- **Adding a new data source** — the three-step integration flow
- **SQL project conventions** — schema layout, file naming, stored procedure patterns
- **Common pitfalls** — Fabric Admin role requirement, Service Principal vs. Workspace Identity nuances, Spark session timeout, ODBC driver version, Variable Library overwrite flag

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
