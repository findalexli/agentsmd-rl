# Fix flaky TestPropertyValueSchema/serialized

## Symptom

The test `TestPropertyValueSchema/serialized` in `pkg/resource/stack/deployment_test.go` is flaky and fails intermittently. The failure occurs when the test generates NaN or Inf float64 values.

## Root cause

`SerializePropertyValue` (in `pkg/resource/stack/deployment.go`) serializes NaN and Inf float64 values as JSON objects containing a special signature and an IEEE 754 hex representation. When schema validation is performed against `sdk/go/common/apitype/property-values.json`, these objects are rejected because the schema has no definition for this float representation type.

## Verification criteria

The fix must satisfy the following (these are what the tests check):

1. **JSON Schema**: The property value schema at `sdk/go/common/apitype/property-values.json` must have a definition in its `oneOf` array that matches float objects. This definition must:
   - Have the title "Float property values"
   - Describe NaN and Inf handling
   - Include a property with key `4dabf18193072939515e22adb298388d` having const value `8ad145fe-0d11-4827-bfd7-1abcbf086f5c`
   - Include a `value` property that is a string matching pattern `^[0-9a-f]{16}$`

2. **Test generator**: The test file `pkg/resource/stack/deployment_test.go` must have a generator function that produces float objects with:
   - The float signature key set to the `floatSignature` constant
   - Hex values representing NaN (`7ff8000000000001`), +Inf (`7ff0000000000000`), and -Inf (`fff0000000000000`)
   - These hex values must be strings drawn from the standard IEEE 754 representations

3. **Integration**: The generator must be integrated into the test's object value generation, following the same pattern used by other object types.

## Verification

After implementing the fix, verify by running:

```bash
cd /workspace/pulumi/pkg
go test -run 'TestPropertyValueSchema/serialized' ./resource/stack/... -count=10 -tags all
```

The test should pass reliably without flaking.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
