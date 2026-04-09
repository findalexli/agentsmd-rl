#!/bin/bash
set -e

cd /workspace/dagster

# Apply the fix using Python instead of patch
python3 << 'PYEOF'
import re

# Read the current file
with open("python_modules/libraries/dagster-k8s/dagster_k8s/pipes.py", "r") as f:
    content = f.read()

# Add import codecs at the top (after any existing imports)
if "import codecs" not in content:
    content = content.replace(
        "import logging",
        "import codecs\nimport logging"
    )

# Find and replace the _process_log_stream function
old_function = '''def _process_log_stream(stream: Iterator[bytes]) -> Iterator[LogItem]:
    timestamp = ""
    log = ""

    for log_chunk in stream:
        for line in log_chunk.decode("utf-8").split("\\n"):
            maybe_timestamp, _, tail = line.partition(" ")
            if not timestamp:
                # The first item in the stream will always have a timestamp.
                timestamp = maybe_timestamp
                log = tail
            elif maybe_timestamp == timestamp:
                # We have multiple messages with the same timestamp in this chunk, add them separated
                # with a new line
                log += f"\\n{tail}"
            elif not (
                len(maybe_timestamp) == len(timestamp) and _is_kube_timestamp(maybe_timestamp)
            ):
                # The line is continuation of a long line that got truncated and thus doesn't
                # have a timestamp in the beginning of the line.

                # Since all timestamps in the RFC format returned by Kubernetes have the same
                # length (when represented as strings) we know that the value won't be a timestamp
                # if the string lengths differ, however if they do not differ, we need to parse the
                # timestamp.
                log += line
            else:
                # New log line has been observed, send in the next cycle
                yield LogItem(timestamp=timestamp, log=log)
                timestamp = maybe_timestamp
                log = tail

    # Send the last message that we were building
    if log or timestamp:
        yield LogItem(timestamp=timestamp, log=log)'''

new_function = '''def _process_log_stream(stream: Iterator[bytes]) -> Iterator[LogItem]:
    timestamp = ""
    log = ""

    # Incremental decoder: supports UTF-8 sequences split across chunks.
    # errors="replace" prevents crashing if a container emits invalid bytes.
    decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")

    def handle_line(line: str) -> Iterator[LogItem]:
        nonlocal timestamp, log

        if not line:
            return

        maybe_timestamp, _, tail = line.partition(" ")

        if not timestamp:
            # First item must begin with a timestamp.
            timestamp = maybe_timestamp
            log = tail
        elif maybe_timestamp == timestamp:
            # Some runtimes can emit multiple lines sharing the same timestamp.
            log += f"\\n{tail}"
        elif not (len(maybe_timestamp) == len(timestamp) and _is_kube_timestamp(maybe_timestamp)):
            # Continuation of a long line that got split across chunks (no timestamp prefix).
            log += line
        else:
            # New timestamp => finalize previous log item.
            yield LogItem(timestamp=timestamp, log=log)
            timestamp = maybe_timestamp
            log = tail

    for log_chunk in stream:
        text = decoder.decode(log_chunk, final=False)

        # Keep original behavior: split *within the chunk*, but if there is no "\\n"
        # we still treat it as a single "line" candidate.
        for line in text.split("\\n"):
            yield from handle_line(line)

    # Flush any buffered bytes from the decoder (e.g. when stream ends cleanly).
    tail = decoder.decode(b"", final=True)
    for line in tail.split("\\n"):
        yield from handle_line(line)

    # Emit the last in-progress log item (if any).
    if log or timestamp:
        yield LogItem(timestamp=timestamp, log=log)'''

if old_function in content:
    content = content.replace(old_function, new_function)
    print("Function replaced successfully")
else:
    print("Warning: Could not find exact function match, trying alternative approach...")
    # If exact match fails, the function might have slight differences
    # Check if already patched
    if "incrementaldecoder" in content:
        print("File appears to already be patched (incrementaldecoder found)")
    else:
        raise ValueError("Could not find function to patch and file is not already patched")

# Write the modified file
with open("python_modules/libraries/dagster-k8s/dagster_k8s/pipes.py", "w") as f:
    f.write(content)

print("Patch applied successfully")
PYEOF

# Verify the patch was applied
grep -q "incrementaldecoder" python_modules/libraries/dagster-k8s/dagster_k8s/pipes.py && echo "Verification passed: incrementaldecoder found" || (echo "Patch verification failed" && exit 1)
