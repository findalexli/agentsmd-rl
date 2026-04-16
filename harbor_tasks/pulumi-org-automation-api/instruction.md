# Add `org` commands to Python and Go Automation APIs

The Pulumi Automation API needs to support organization management commands. Specifically, the `org get-default` and `org set-default` CLI commands need to be exposed through both the Go and Python Automation APIs.

## What needs to be done

Add methods to interact with the default organization setting in both language SDKs:

### Go SDK (`sdk/go/auto/`)

The Go Automation API's `Workspace` interface needs two new methods:
- `OrgGetDefault` - returns the default organization name, signature: `OrgGetDefault(context.Context) (string, error)`
- `OrgSetDefault` - sets the default organization, signature: `OrgSetDefault(ctx context.Context, orgName string) error`

The `LocalWorkspace` struct in `local_workspace.go` must implement these methods by invoking the pulumi CLI org commands.

### Python SDK (`sdk/python/lib/pulumi/automation/`)

The Python Automation API's `Workspace` abstract base class needs:
- `org_get_default(self) -> str` - returns the default organization name
- `org_set_default(self, org_name: str) -> None` - sets the default organization

The `LocalWorkspace` class in `_local_workspace.py` must implement these methods using the pulumi CLI command runner.

### Command invocation patterns

The Go implementation must invoke the pulumi CLI with the command arguments passed as separate string values:
- For `OrgGetDefault`: pass `"org"` and `"get-default"` as separate arguments to the command runner
- For `OrgSetDefault`: pass `"org"`, `"set-default"`, and the org name as separate arguments

The Python implementation must invoke the pulumi CLI with command arguments as a list:
- For `org_get_default`: use `["org", "get-default"]`
- For `org_set_default`: use `["org", "set-default", org_name]`

### Error handling

Go org methods must use `newAutoError` when wrapping errors from failed command invocations.

### Docstrings

Python abstract method declarations must include docstrings. The `org_get_default` method docstring must contain the phrase "Returns the default organization".

### Tests

Both language SDKs need integration test coverage for the org methods:
- Go: a test function named `TestOrgGetSetDefault` in `local_workspace_test.go`
- Python: a test function named `test_org_get_set_default_integration` in `test_local_workspace.py`

## Relevant files

- `sdk/go/auto/workspace.go` - Workspace interface definition
- `sdk/go/auto/local_workspace.go` - LocalWorkspace implementation
- `sdk/go/auto/local_workspace_test.go` - Go tests
- `sdk/python/lib/pulumi/automation/_workspace.py` - Workspace abstract class
- `sdk/python/lib/pulumi/automation/_local_workspace.py` - LocalWorkspace implementation
- `sdk/python/lib/test/automation/test_local_workspace.py` - Python tests

## Verification

After implementing, run `go build ./...` in `sdk/go/` to verify Go code compiles. Python syntax can be checked with `python3 -m py_compile` on the modified files.