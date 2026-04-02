# Add requestUnsandboxedExecutionReason to Terminal Tool Telemetry

## Problem

The `RunInTerminalToolTelemetry` class tracks various metrics about terminal command executions for analytics purposes. However, when the model requests unsandboxed execution (executing commands outside the terminal sandbox), the reason provided by the model is not being captured in telemetry data.

This makes it difficult to analyze why models are requesting unsandboxed execution and whether those requests are legitimate or potentially problematic.

## Relevant Files

- `src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts` - Telemetry reporter class
- `src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts` - Tool implementation that invokes the telemetry

## Expected Behavior

The telemetry should include the `requestUnsandboxedExecutionReason` field (a string or undefined) that captures why the model requested unsandboxed execution, if applicable.

This requires:
1. Adding the property to the internal telemetry state interface
2. Adding the property to the telemetry data event interface sent to the telemetry service
3. Adding the proper telemetry classification metadata for the new field
4. Mapping the state property to the telemetry data when logging
5. Updating the tool to pass this value when reporting telemetry

## Notes

- Follow the existing patterns in the telemetry code for similar string properties
- Ensure proper TypeScript typing (string | undefined)
- The telemetry classification should use `SystemMetaData` with `FeatureInsight` purpose
