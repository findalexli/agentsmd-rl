#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

TARGET="src/cli/completion-cli.ts"

# Replace the bare compdef line with deferred registration
# The old code has: compdef _${rootCmd}_root_completion ${rootCmd}
# Replace with the deferred pattern
sed -i '/^compdef _\${rootCmd}_root_completion \${rootCmd}$/c\
_${rootCmd}_register_completion() {\
  if (( ! $+functions[compdef] )); then\
    return 0\
  fi\
\
  compdef _${rootCmd}_root_completion ${rootCmd}\
  precmd_functions=(\\${precmd_functions:#_${rootCmd}_register_completion})\
  unfunction _${rootCmd}_register_completion 2>/dev/null\
}\
\
_${rootCmd}_register_completion\
if (( ! $+functions[compdef] )); then\
  typeset -ga precmd_functions\
  if [[ -z "\\${precmd_functions[(r)_${rootCmd}_register_completion]}" ]]; then\
    precmd_functions+=(_${rootCmd}_register_completion)\
  fi\
fi' "$TARGET"
