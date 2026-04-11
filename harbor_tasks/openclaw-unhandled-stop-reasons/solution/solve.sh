#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

# Create the stop-reason recovery module
cat > src/agents/pi-embedded-runner/run/attempt.stop-reason-recovery.ts << 'TSEOF'
import type { StreamFn } from "@mariozechner/pi-agent-core";
import { createAssistantMessageEventStream, streamSimple } from "@mariozechner/pi-ai";
import { buildStreamErrorAssistantMessage } from "../../stream-message-shared.js";

const UNHANDLED_STOP_REASON_RE = /^Unhandled stop reason:\s*(.+)$/i;

function formatUnhandledStopReasonErrorMessage(stopReason: string): string {
  return `The model stopped because the provider returned an unhandled stop reason: ${stopReason}. Please rephrase and try again.`;
}

function normalizeUnhandledStopReasonMessage(message: unknown): string | undefined {
  if (typeof message !== "string") {
    return undefined;
  }
  const match = message.trim().match(UNHANDLED_STOP_REASON_RE);
  const stopReason = match?.[1]?.trim();
  if (!stopReason) {
    return undefined;
  }
  return formatUnhandledStopReasonErrorMessage(stopReason);
}

function patchUnhandledStopReasonInAssistantMessage(message: unknown): void {
  if (!message || typeof message !== "object") {
    return;
  }

  const assistant = message as { errorMessage?: unknown; stopReason?: unknown };
  const normalizedMessage = normalizeUnhandledStopReasonMessage(assistant.errorMessage);
  if (!normalizedMessage) {
    return;
  }

  assistant.stopReason = "error";
  assistant.errorMessage = normalizedMessage;
}

function buildUnhandledStopReasonErrorStream(
  model: Parameters<StreamFn>[0],
  errorMessage: string,
): ReturnType<typeof streamSimple> {
  const stream = createAssistantMessageEventStream();
  queueMicrotask(() => {
    stream.push({
      type: "error",
      reason: "error",
      error: buildStreamErrorAssistantMessage({
        model: {
          api: model.api,
          provider: model.provider,
          id: model.id,
        },
        errorMessage,
      }),
    });
    stream.end();
  });
  return stream;
}

function wrapStreamHandleUnhandledStopReason(
  model: Parameters<StreamFn>[0],
  stream: ReturnType<typeof streamSimple>,
): ReturnType<typeof streamSimple> {
  const originalResult = stream.result.bind(stream);
  stream.result = async () => {
    try {
      const message = await originalResult();
      patchUnhandledStopReasonInAssistantMessage(message);
      return message;
    } catch (err) {
      const normalizedMessage = normalizeUnhandledStopReasonMessage(
        err instanceof Error ? err.message : String(err),
      );
      if (!normalizedMessage) {
        throw err;
      }
      return buildStreamErrorAssistantMessage({
        model: {
          api: model.api,
          provider: model.provider,
          id: model.id,
        },
        errorMessage: normalizedMessage,
      });
    }
  };

  const originalAsyncIterator = stream[Symbol.asyncIterator].bind(stream);
  (stream as { [Symbol.asyncIterator]: typeof originalAsyncIterator })[Symbol.asyncIterator] =
    function () {
      const iterator = originalAsyncIterator();
      let emittedSyntheticTerminal = false;
      return {
        async next() {
          if (emittedSyntheticTerminal) {
            return { done: true as const, value: undefined };
          }

          try {
            const result = await iterator.next();
            if (!result.done && result.value && typeof result.value === "object") {
              const event = result.value as { error?: unknown };
              patchUnhandledStopReasonInAssistantMessage(event.error);
            }
            return result;
          } catch (err) {
            const normalizedMessage = normalizeUnhandledStopReasonMessage(
              err instanceof Error ? err.message : String(err),
            );
            if (!normalizedMessage) {
              throw err;
            }
            emittedSyntheticTerminal = true;
            return {
              done: false as const,
              value: {
                type: "error" as const,
                reason: "error" as const,
                error: buildStreamErrorAssistantMessage({
                  model: {
                    api: model.api,
                    provider: model.provider,
                    id: model.id,
                  },
                  errorMessage: normalizedMessage,
                }),
              },
            };
          }
        },
        async return(value?: unknown) {
          return iterator.return?.(value) ?? { done: true as const, value: undefined };
        },
        async throw(error?: unknown) {
          return iterator.throw?.(error) ?? { done: true as const, value: undefined };
        },
        [Symbol.asyncIterator]() {
          return this;
        },
      };
    };

  return stream;
}

export function wrapStreamFnHandleSensitiveStopReason(baseFn: StreamFn): StreamFn {
  return (model, context, options) => {
    try {
      const maybeStream = baseFn(model, context, options);
      if (maybeStream && typeof maybeStream === "object" && "then" in maybeStream) {
        return Promise.resolve(maybeStream).then(
          (stream) => wrapStreamHandleUnhandledStopReason(model, stream),
          (err) => {
            const normalizedMessage = normalizeUnhandledStopReasonMessage(
              err instanceof Error ? err.message : String(err),
            );
            if (!normalizedMessage) {
              throw err;
            }
            return buildUnhandledStopReasonErrorStream(model, normalizedMessage);
          },
        );
      }
      return wrapStreamHandleUnhandledStopReason(model, maybeStream);
    } catch (err) {
      const normalizedMessage = normalizeUnhandledStopReasonMessage(
        err instanceof Error ? err.message : String(err),
      );
      if (!normalizedMessage) {
        throw err;
      }
      return buildUnhandledStopReasonErrorStream(model, normalizedMessage);
    }
  };
}
TSEOF

# Use Python to patch attempt.ts reliably
python3 << 'PYEOF'
import re

ATTEMPT_TS = "src/agents/pi-embedded-runner/run/attempt.ts"

with open(ATTEMPT_TS, "r") as f:
    content = f.read()

# Add import if not present
import_line = 'import { wrapStreamFnHandleSensitiveStopReason } from "./attempt.stop-reason-recovery.js";' 
if "attempt.stop-reason-recovery.js" not in content:
    # Find the tool-call-argument-repair import block and add after its closing
    pattern = r'(} from "./attempt\.tool-call-argument-repair\.js";\n)(import \{[^}]+\} from "./attempt\.tool-call-normalization\.js";)' 
    replacement = r'\1' + import_line + r'\n\2'
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content == content:
        # Fallback: try simpler pattern
        pattern = r'(} from "./attempt\.tool-call-argument-repair\.js";\n)'
        replacement = r'\1' + import_line + r'\n'
        new_content = re.sub(pattern, replacement, content, count=1)
    content = new_content

# Add wrapper call if not present
if "wrapStreamFnHandleSensitiveStopReason(" not in content:
    # Find the sanitizeSessionHistory line and add before it
    pattern = r'(const prior = await sanitizeSessionHistory)'
    replacement = r'''      // Anthropic-compatible providers can add new stop reasons before pi-ai maps them.
      // Recover the known "sensitive" stop reason here so a model refusal does not
      // bubble out as an uncaught runner error and stall channel polling.
      activeSession.agent.streamFn = wrapStreamFnHandleSensitiveStopReason(
        activeSession.agent.streamFn,
      );
\1'''
    content = re.sub(pattern, replacement, content, count=1)

with open(ATTEMPT_TS, "w") as f:
    f.write(content)

print("attempt.ts patched successfully")
PYEOF
