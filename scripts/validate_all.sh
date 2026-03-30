#!/usr/bin/env bash
# Validate all filled tasks: build images, run oracle+nop, generate report.
# Usage:
#   ./scripts/validate_all.sh                    # deterministic only (fast, free)
#   ./scripts/validate_all.sh --with-judge       # include LLM rubric judge ($)
#   ./scripts/validate_all.sh --rebuild          # force rebuild all images
#   ./scripts/validate_all.sh --only-new         # skip already-built images
set -euo pipefail
cd "$(dirname "$0")/.."

REBUILD=false
ONLY_NEW=false
WITH_JUDGE=false
for arg in "$@"; do
  case "$arg" in
    --rebuild) REBUILD=true ;;
    --only-new) ONLY_NEW=true ;;
    --with-judge) WITH_JUDGE=true ;;
  esac
done

# Load API key for LLM judge if enabled
JUDGE_ENV=""
if [ "$WITH_JUDGE" = true ]; then
  API_KEY="${ANTHROPIC_API_KEY:-}"
  if [ -z "$API_KEY" ] && [ -f .env ]; then
    API_KEY=$(grep ANTHROPIC_API_KEY .env 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'")
  fi
  if [ -n "$API_KEY" ]; then
    JUDGE_ENV="-e ANTHROPIC_API_KEY=$API_KEY -e LLM_JUDGE=1"
    echo "LLM judge: ENABLED"
  else
    echo "WARNING: --with-judge but no ANTHROPIC_API_KEY found. Judge disabled."
  fi
else
  echo "LLM judge: DISABLED (use --with-judge to enable)"
fi

RESULTS_FILE="validation_results.csv"
echo "TASK,ORACLE,NOP,STATUS" > "$RESULTS_FILE"

PASS=0; FAIL_ORACLE=0; FAIL_NOP=0; ERROR=0; SKIP=0

for dir in harbor_tasks/*/; do
  task=$(basename "$dir")
  test_file="$dir/tests/test.sh"
  solve_file="$dir/solution/solve.sh"

  # Skip unfilled
  if [ ! -f "$test_file" ] || grep -q "TODO: Implement tests\|TODO: Agent must" "$test_file" 2>/dev/null; then
    continue
  fi
  if [ ! -f "$solve_file" ] || grep -q "TODO: Apply gold patch\|TODO: Agent" "$solve_file" 2>/dev/null; then
    continue
  fi

  image="harbor-${task}:latest"

  # Build if needed
  if ! docker image inspect "$image" >/dev/null 2>&1 || [ "$REBUILD" = true ]; then
    if [ "$ONLY_NEW" = true ] && docker image inspect "$image" >/dev/null 2>&1; then
      : # skip
    else
      echo "Building $task..."
      docker build -t "$image" "harbor_tasks/${task}/environment/" 2>&1 | tail -1
    fi
  fi

  if ! docker image inspect "$image" >/dev/null 2>&1; then
    echo "$task,NO_IMAGE,,SKIP" >> "$RESULTS_FILE"
    SKIP=$((SKIP + 1))
    continue
  fi

  # Oracle: apply gold patch, then run tests
  oracle=$(timeout 180 docker run --rm --memory=4g --cpus=1 \
    -v "$(pwd)/harbor_tasks/${task}/solution:/solution" \
    -v "$(pwd)/harbor_tasks/${task}/tests:/tests" \
    -v "$(pwd)/harbor_tasks/${task}/rubric.yaml:/rubric.yaml:ro" \
    $JUDGE_ENV \
    "$image" \
    bash -c "chmod +x /solution/solve.sh /tests/test.sh && /solution/solve.sh 2>/dev/null && /tests/test.sh 2>/dev/null; cat /logs/verifier/reward.txt 2>/dev/null || echo ERROR" 2>&1 | tail -1)

  # Nop: run tests on buggy code (no patch)
  nop=$(timeout 180 docker run --rm --memory=4g --cpus=1 \
    -v "$(pwd)/harbor_tasks/${task}/tests:/tests" \
    -v "$(pwd)/harbor_tasks/${task}/rubric.yaml:/rubric.yaml:ro" \
    $JUDGE_ENV \
    "$image" \
    bash -c "chmod +x /tests/test.sh && /tests/test.sh 2>/dev/null; cat /logs/verifier/reward.txt 2>/dev/null || echo ERROR" 2>&1 | tail -1)

  if [[ "$oracle" =~ ^1\.0 ]]; then
    if [[ "$nop" =~ ^1\.0 ]]; then
      status="FAIL_NOP_HIGH"
      FAIL_NOP=$((FAIL_NOP + 1))
    elif [[ "$nop" == "ERROR" ]]; then
      status="ERROR"
      ERROR=$((ERROR + 1))
    else
      status="PASS"
      PASS=$((PASS + 1))
    fi
  elif [[ "$oracle" == "ERROR" ]]; then
    status="ERROR"
    ERROR=$((ERROR + 1))
  else
    status="FAIL_ORACLE"
    FAIL_ORACLE=$((FAIL_ORACLE + 1))
  fi

  echo "$task,$oracle,$nop,$status" >> "$RESULTS_FILE"
  echo "$task: oracle=$oracle nop=$nop [$status]"
done

echo ""
echo "=== SUMMARY ==="
echo "PASS: $PASS"
echo "FAIL_ORACLE: $FAIL_ORACLE"
echo "FAIL_NOP_HIGH: $FAIL_NOP"
echo "ERROR: $ERROR"
echo "SKIP: $SKIP"
echo "Results saved to $RESULTS_FILE"
