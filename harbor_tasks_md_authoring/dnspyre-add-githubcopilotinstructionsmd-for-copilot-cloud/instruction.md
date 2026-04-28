# Add .github/copilot-instructions.md for Copilot cloud agent onboarding

Source: [Tantalor93/dnspyre#459](https://github.com/Tantalor93/dnspyre/pull/459)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds a `copilot-instructions.md` so the Copilot cloud agent can orient itself quickly on first encounter with this repo.

## What's documented

- **Repo layout** — annotated directory tree covering `main.go`, `cmd/`, `pkg/dnsbench/`, `pkg/reporter/`, `data/`, `docs/`, CI configs
- **Core design** — `Benchmark` struct lifecycle, CLI-to-struct wiring via kingpin, concurrency model, protocol dispatch logic, data source loading
- **Dev commands** — build, test (with `-race`), lint (`golangci-lint v2`), GoReleaser check
- **Testing patterns** — white-box (`benchmark_test.go`) vs black-box (`benchmark_*_api_test.go`), in-process DNS server helper, golden-file reporter tests, table-driven style conventions
- **CI/workflows** — what each CircleCI job and GitHub Actions workflow does
- **Notable dependencies** — key packages and their roles (`miekg/dns`, `doh-go`, `doq-go`, `gonum/plot`, etc.)
- **Pitfalls** — `--number`/`--duration` mutual exclusion, DoH URL detection requirement, embedded default domains, platform-specific nameserver files, intentional `gosec` G104 exclusion, pprof side-effect import
- **Release process** — tag-driven GoReleaser pipeline, cosign signing

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
